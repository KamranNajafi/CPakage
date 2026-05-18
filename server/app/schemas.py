from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class DependencyOut(BaseModel):
    name: str
    version_range: str

    class Config:
        from_attributes = True


class PackageVersionOut(BaseModel):
    version: str
    build_type: Optional[str]
    file_size: Optional[int]
    checksum: Optional[str]
    downloads: int
    published_at: datetime
    dependencies: List[DependencyOut] = []

    class Config:
        from_attributes = True


class PackageOut(BaseModel):
    name: str
    description: Optional[str]
    homepage: Optional[str]
    license: Optional[str]
    keywords: Optional[List[str]]
    created_at: datetime
    latest_version: Optional[str]
    versions: List[PackageVersionOut] = []

    class Config:
        from_attributes = True


class PackageSearchResult(BaseModel):
    name: str
    description: Optional[str]
    latest_version: Optional[str]
    downloads: int
