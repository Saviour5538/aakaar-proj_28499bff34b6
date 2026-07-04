import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import psycopg2
from psycopg2.extras import register_uuid
import pgvector.psycopg2

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/taskflow"
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import models to ensure tables are created
from backend.models.user import User
from backend.models.task import Task

# FastAPI application setup
app = FastAPI(
    title="TaskFlow",
    description="A task management web application",
    version="1.0.0"
)

# CORS middleware setup
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Startup logic - create tables
        Base.metadata.create_all(bind=engine)
        # Test connection and register vector extension
        with engine.connect() as conn:
            # Create pgvector extension if not exists
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            # Commit the extension creation
            conn.commit()
            # Register pgvector adapter for the connection
            pgvector.psycopg2.register_vector(conn.connection.connection)
            # Register UUID type if needed
            register_uuid()
        yield
    finally:
        # Shutdown logic
        engine.dispose()

app.router.lifespan_context = lifespan

# Import routers after database setup to avoid circular imports
from backend.routes.auth import router as auth_router
from backend.routes.tasks import router as tasks_router

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")

# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat()
    }