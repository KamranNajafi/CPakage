from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, BigInteger, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True)
    username   = Column(String(50), unique=True, nullable=False)
    email      = Column(String(255), unique=True, nullable=False)
    password   = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    packages = relationship("Package", back_populates="owner")


class Package(Base):
    __tablename__ = "packages"

    id          = Column(Integer, primary_key=True)
    name        = Column(String(100), unique=True, nullable=False)
    owner_id    = Column(Integer, ForeignKey("users.id"))
    description = Column(Text)
    homepage    = Column(String(500))
    license     = Column(String(50))
    keywords    = Column(ARRAY(String))
    created_at  = Column(DateTime, default=datetime.utcnow)

    owner    = relationship("User", back_populates="packages")
    versions = relationship("PackageVersion", back_populates="package", order_by="PackageVersion.published_at.desc()")


class PackageVersion(Base):
    __tablename__ = "package_versions"

    id           = Column(Integer, primary_key=True)
    package_id   = Column(Integer, ForeignKey("packages.id"))
    version      = Column(String(50), nullable=False)
    build_type   = Column(String(20))          # header-only | cmake | make | prebuilt
    file_path    = Column(String(500))
    file_size    = Column(BigInteger)
    checksum     = Column(String(64))          # SHA-256
    manifest     = Column(JSON)               # cpakage.toml as JSON
    downloads    = Column(Integer, default=0)
    published_at = Column(DateTime, default=datetime.utcnow)

    package      = relationship("Package", back_populates="versions")
    dependencies = relationship("Dependency", back_populates="package_version")


class Dependency(Base):
    __tablename__ = "dependencies"

    id                 = Column(Integer, primary_key=True)
    package_version_id = Column(Integer, ForeignKey("package_versions.id"))
    dep_name           = Column(String(100), nullable=False)
    dep_version_range  = Column(String(50))

    package_version = relationship("PackageVersion", back_populates="dependencies")
