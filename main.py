import math
import os
from typing import Optional
import uvicorn
from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import database
from schemas import (
    ApiResponse,
    HealthResponse,
    ArticleItem,
    PaginationMeta,
    ArticleListData,
)

load_dotenv()

app = FastAPI(
    title="News Scraping REST API",
    description="REST API untuk mengakses artikel berita hasil scraping detik.com yang tersimpan di PostgreSQL.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS agar API bisa diakses dari Frontend / browser manapun
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=ApiResponse, tags=["Root"])
def root():
    """Halaman sambutan dan informasi API."""
    return ApiResponse(
        status="success",
        message="Selamat datang di News Scraping REST API",
        data={
            "docs": "/docs",
            "endpoints": {
                "health": "/health",
                "articles": "/api/articles",
                "article_detail": "/api/articles/{id}",
                "stats": "/api/stats",
            },
        },
    )


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """Mengecek status kesehatan server API dan koneksi database PostgreSQL."""
    db_healthy = database.check_db_health()
    if not db_healthy:
        raise HTTPException(
            status_code=503,
            detail="Database PostgreSQL tidak dapat dihubungi",
        )
    return HealthResponse(
        status="healthy",
        database="connected (PostgreSQL)",
    )


@app.get("/api/articles", response_model=ApiResponse, tags=["Articles"])
def list_articles(
    page: int = Query(1, ge=1, description="Nomor halaman (mulai dari 1)"),
    limit: int = Query(10, ge=1, le=100, description="Jumlah artikel per halaman (maks: 100)"),
    search: Optional[str] = Query(None, description="Kata kunci pencarian judul atau konten"),
    author: Optional[str] = Query(None, description="Filter berdasarkan nama penulis/author"),
):
    """
    Mengambil daftar artikel dengan paginasi, pencarian judul/konten, dan filter author.
    """
    try:
        articles, total_records = database.get_articles(
            page=page,
            limit=limit,
            search=search,
            author=author,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    total_pages = math.ceil(total_records / limit) if total_records > 0 else 0

    pagination = PaginationMeta(
        total_records=total_records,
        page=page,
        limit=limit,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )

    data = ArticleListData(
        pagination=pagination,
        articles=[ArticleItem(**art) for art in articles],
    )

    return ApiResponse(
        status="success",
        message=f"Berhasil mengambil {len(articles)} artikel",
        data=data,
    )


@app.get("/api/articles/{id}", response_model=ApiResponse, tags=["Articles"])
def get_article(
    id: int = Path(..., ge=1, description="ID unik artikel"),
):
    """
    Mengambil satu artikel lengkap berdasarkan ID.
    """
    try:
        article = database.get_article_by_id(id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    if not article:
        raise HTTPException(
            status_code=404,
            detail=f"Artikel dengan ID {id} tidak ditemukan",
        )

    return ApiResponse(
        status="success",
        message="Artikel ditemukan",
        data=ArticleItem(**article),
    )


@app.get("/api/stats", response_model=ApiResponse, tags=["Statistics"])
def get_statistics():
    """
    Mengambil statistik data artikel di database (total artikel, top author, rentang tanggal).
    """
    try:
        stats = database.get_stats()
        return ApiResponse(
            status="success",
            message="Statistik artikel berhasil diambil",
            data=stats,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")


if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    print(f"Menjalankan News REST API pada http://{host}:{port} ...")
    uvicorn.run("main:app", host=host, port=port, reload=True)

