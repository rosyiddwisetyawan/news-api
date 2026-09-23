from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class ArticleItem(BaseModel):
    id: int
    source: str
    title: str
    author: Optional[str] = None
    date_content: Optional[str] = None
    content: Optional[str] = None


class PaginationMeta(BaseModel):
    total_records: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    has_prev: bool


class ArticleListData(BaseModel):
    pagination: PaginationMeta
    articles: List[ArticleItem]


class ApiResponse(BaseModel):
    status: str = "success"
    message: str = "OK"
    data: Any = None


class HealthResponse(BaseModel):
    status: str
    database: str
    service: str = "News REST API"

