from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routes import auth, packages, search

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CPakage Registry",
    description="PyPI-like package registry for C/C++ libraries",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,     prefix="/api/v1/auth",     tags=["auth"])
app.include_router(packages.router, prefix="/api/v1/packages", tags=["packages"])
app.include_router(search.router,   prefix="/api/v1/search",   tags=["search"])


@app.get("/")
def root():
    return {"message": "CPakage Registry", "docs": "/docs"}
