import re
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app import models, schemas
from app.auth import get_current_user
from app.database import get_db
from app.storage import save_package_file, get_package_path
import json

router = APIRouter()

NAME_PATTERN = re.compile(r"^[a-z][a-z0-9-]{0,48}[a-z0-9]$")


def _latest_version(package: models.Package) -> str | None:
    if package.versions:
        return package.versions[0].version
    return None


@router.get("/{name}", response_model=schemas.PackageOut)
def get_package(name: str, db: Session = Depends(get_db)):
    pkg = db.query(models.Package).filter(models.Package.name == name).first()
    if not pkg:
        raise HTTPException(status_code=404, detail=f"Package '{name}' not found")

    result = schemas.PackageOut.model_validate(pkg)
    result.latest_version = _latest_version(pkg)
    return result


@router.get("/{name}/versions")
def list_versions(name: str, db: Session = Depends(get_db)):
    pkg = db.query(models.Package).filter(models.Package.name == name).first()
    if not pkg:
        raise HTTPException(status_code=404, detail=f"Package '{name}' not found")
    return [v.version for v in pkg.versions]


@router.get("/{name}/{version}/download")
def download_package(name: str, version: str, db: Session = Depends(get_db)):
    pkg = db.query(models.Package).filter(models.Package.name == name).first()
    if not pkg:
        raise HTTPException(status_code=404, detail=f"Package '{name}' not found")

    ver = next((v for v in pkg.versions if v.version == version), None)
    if not ver:
        raise HTTPException(status_code=404, detail=f"Version '{version}' not found")

    file_path = get_package_path(name, version)
    ver.downloads += 1
    db.commit()

    return FileResponse(file_path, filename=f"{name}-{version}.tar.gz", media_type="application/gzip")


@router.post("/upload", status_code=201)
def upload_package(
    file: UploadFile = File(...),
    manifest_json: str = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        manifest = json.loads(manifest_json)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid manifest JSON")

    pkg_info = manifest.get("package", {})
    name = pkg_info.get("name", "").lower()
    version = pkg_info.get("version", "")

    if not NAME_PATTERN.match(name):
        raise HTTPException(status_code=400, detail="Invalid package name")
    if not version:
        raise HTTPException(status_code=400, detail="Version is required")

    # ایجاد یا یافتن پکیج
    pkg = db.query(models.Package).filter(models.Package.name == name).first()
    if pkg and pkg.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't own this package")

    if not pkg:
        pkg = models.Package(
            name=name,
            owner_id=current_user.id,
            description=pkg_info.get("description"),
            homepage=pkg_info.get("homepage"),
            license=pkg_info.get("license"),
            keywords=pkg_info.get("keywords", []),
        )
        db.add(pkg)
        db.flush()

    # بررسی نسخه تکراری
    existing = next((v for v in pkg.versions if v.version == version), None)
    if existing:
        raise HTTPException(status_code=409, detail=f"Version '{version}' already exists")

    data = file.file.read()
    file_path, file_size, checksum = save_package_file(name, version, data)

    build = manifest.get("build", {})
    ver = models.PackageVersion(
        package_id=pkg.id,
        version=version,
        build_type=build.get("type"),
        file_path=file_path,
        file_size=file_size,
        checksum=checksum,
        manifest=manifest,
    )
    db.add(ver)
    db.flush()

    for dep_name, dep_range in manifest.get("dependencies", {}).items():
        db.add(models.Dependency(
            package_version_id=ver.id,
            dep_name=dep_name,
            dep_version_range=dep_range,
        ))

    db.commit()
    return {"message": f"Package '{name}' version '{version}' published successfully"}
