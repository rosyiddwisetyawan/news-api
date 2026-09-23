import os
from contextlib import contextmanager
from typing import List, Dict, Any, Optional, Tuple
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = int(os.getenv("PG_PORT", 5432))
PG_DATABASE = os.getenv("PG_DATABASE", "postgres")
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "postgres")

# Inisialisasi ThreadedConnectionPool untuk mendukung concurrency permintaan API
try:
    connection_pool = pool.ThreadedConnectionPool(
        minconn=1,
        maxconn=10,
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DATABASE,
        user=PG_USER,
        password=PG_PASSWORD,
    )
except Exception as e:
    connection_pool = None
    print(f"[ERROR] Gagal membuat PostgreSQL connection pool: {e}")


@contextmanager
def get_db():
    """Context manager untuk mengambil dan mengembalikan koneksi dari pool."""
    if connection_pool is None:
        raise ConnectionError("Connection pool ke PostgreSQL belum diinisialisasi")
    conn = connection_pool.getconn()
    try:
        yield conn
    finally:
        connection_pool.putconn(conn)


def check_db_health() -> bool:
    """Memeriksa kesehatan koneksi database."""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                res = cur.fetchone()
                return res is not None
    except Exception:
        return False


def get_articles(
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None,
    author: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Mengambil daftar artikel dengan paginasi, pencarian keyword judul/konten,
    dan filter nama author.
    Mengembalikan (daftar_artikel, total_records).
    """
    offset = (page - 1) * limit
    where_clauses = []
    params: List[Any] = []

    if search:
        where_clauses.append("(title ILIKE %s OR content ILIKE %s)")
        search_param = f"%{search}%"
        params.extend([search_param, search_param])

    if author:
        where_clauses.append("author ILIKE %s")
        params.append(f"%{author}%")

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Hitung total data yang cocok
            count_sql = f"SELECT COUNT(*) AS total FROM content {where_sql};"
            cur.execute(count_sql, tuple(params))
            total_count = cur.fetchone()["total"]

            # Ambil data sesuai paginasi
            query_sql = f"""
            SELECT id, source, title, author, date_content, content
            FROM content
            {where_sql}
            ORDER BY id DESC
            LIMIT %s OFFSET %s;
            """
            cur.execute(query_sql, tuple(params + [limit, offset]))
            items = cur.fetchall()

            return [dict(item) for item in items], total_count


def get_article_by_id(article_id: int) -> Optional[Dict[str, Any]]:
    """Mengambil satu artikel berdasarkan ID."""
    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, source, title, author, date_content, content FROM content WHERE id = %s;",
                (article_id,),
            )
            item = cur.fetchone()
            return dict(item) if item else None


def get_stats() -> Dict[str, Any]:
    """Mengambil data statistik artikel."""
    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Total artikel
            cur.execute("SELECT COUNT(*) AS total FROM content;")
            total = cur.fetchone()["total"]

            # Top 5 author terproduktif
            cur.execute("""
                SELECT author, COUNT(*) AS count
                FROM content
                GROUP BY author
                ORDER BY count DESC
                LIMIT 5;
            """)
            top_authors = cur.fetchall()

            # Artikel terbaru dan terlama
            cur.execute("""
                SELECT MIN(date_content) AS earliest_date, MAX(date_content) AS latest_date
                FROM content;
            """)
            dates = cur.fetchone()

            return {
                "total_articles": total,
                "top_authors": [dict(a) for a in top_authors],
                "earliest_date": dates["earliest_date"] if dates else None,
                "latest_date": dates["latest_date"] if dates else None,
            }

