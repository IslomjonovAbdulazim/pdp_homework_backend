from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .utils.constants import (
    DATABASE_URL, 
    DB_POOL_SIZE, 
    DB_MAX_OVERFLOW, 
    DB_POOL_TIMEOUT
)

# Create SQLAlchemy engine with configuration from environment
if DATABASE_URL.startswith("sqlite"):
    # SQLite specific configuration
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False},
        echo=False  # Set to True for SQL debugging
    )
else:
    # PostgreSQL/MySQL configuration with connection pooling
    engine = create_engine(
        DATABASE_URL,
        pool_size=DB_POOL_SIZE,
        max_overflow=DB_MAX_OVERFLOW,
        pool_timeout=DB_POOL_TIMEOUT,
        pool_pre_ping=True,  # Verify connections before use
        echo=False  # Set to True for SQL debugging
    )

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables - useful for initialization"""
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """Drop all tables - useful for testing/reset"""
    Base.metadata.drop_all(bind=engine)

def get_engine():
    """Get the SQLAlchemy engine"""
    return engine