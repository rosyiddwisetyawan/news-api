# News REST API (FastAPI & PostgreSQL)

Project REST API mandiri untuk menyajikan data berita hasil scraping dari database **PostgreSQL** dalam format **JSON Response**.

---

## Fitur Utama

- **Fast & Modern**: Menggunakan framework **FastAPI** dengan performa tinggi.
- **Connection Pooling**: Koneksi database PostgreSQL efisien menggunakan `psycopg2.pool.ThreadedConnectionPool`.
- **Interactive API Docs**: Dilengkapi dokumentasi otomatis interaktif (**Swagger UI**) di `/docs` dan **ReDoc** di `/redoc`.
- **Fitur Endpoint Lengkap**:
  - Paginasi (`page`, `limit`)
  - Pencarian kata kunci pada judul & konten (`search`)
  - Filter berdasarkan nama penulis (`author`)
  - Detail artikel berdasarkan ID
  - Endpoint statistik (total artikel, top authors, rentang tanggal)
  - Health check endpoint

---

## Daftar Endpoint API

Semua respons menggunakan format standar:
```json
{
  "status": "success",
  "message": "...",
  "data": { ... }
}
```

| Method | Endpoint | Deskripsi | Query Parameters |
|---|---|---|---|
| `GET` | `/` | Informasi root & daftar endpoint | - |
| `GET` | `/health` | Status server & koneksi PostgreSQL | - |
| `GET` | `/api/articles` | Daftar artikel dengan paginasi & filter | `page=1`, `limit=10`, `search=...`, `author=...` |
| `GET` | `/api/articles/{id}` | Detail artikel lengkap berdasarkan ID | `id` (path) |
| `GET` | `/api/stats` | Statistik data artikel & top author | - |
| `GET` | `/docs` | Dokumentasi Interaktif Swagger UI | - |

---

## Cara Menjalankan

### 1. Masuk ke Direktori Project
```bash
cd /../news-api
```

### 2. Aktifkan Virtual Environment & Jalankan Server
```bash
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Server akan berjalan di: `http://localhost:8000`

---

## Contoh Penggunaan (cURL)

### 1. Cek Kesehatan Database
```bash
curl http://localhost:8000/health
```

### 2. Mengambil Daftar Berita (5 Data Pertama)
```bash
curl "http://localhost:8000/api/articles?limit=5"
```

### 3. Mencari Berita dengan Kata Kunci
```bash
curl "http://localhost:8000/api/articles?search=Polri"
```

### 4. Mengambil Detail Satu Berita Berdasarkan ID
```bash
curl http://localhost:8000/api/articles/2
```

### 5. Melihat Statistik Berita
```bash
curl http://localhost:8000/api/stats
```

