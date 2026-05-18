from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app import models
from app.database import get_db

router = APIRouter()


@router.get("")
def search_packages(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * limit
    query = db.query(models.Package).filter(
        or_(
            models.Package.name.ilike(f"%{q}%"),
            models.Package.description.ilike(f"%{q}%"),
            models.Package.keywords.any(q),
        )
    )
    total = query.count()
    packages = query.offset(offset).limit(limit).all()

    results = []
    for pkg in packages:
        latest = pkg.versions[0] if pkg.versions else None
        results.append({
            "name": pkg.name,
            "description": pkg.description,
            "latest_version": latest.version if latest else None,
            "downloads": sum(v.downloads for v in pkg.versions),
        })

    return {"total": total, "page": page, "results": results}
