from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Database connection string (Placeholder for environment variable)
# We will use a simple SQLite for local development, but the final deployment will use PostgreSQL
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./billing.db"

# Create the asynchronous engine
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, 
    echo=True, 
    connect_args={"check_same_thread": False} # Only needed for SQLite
)

# Create the session maker
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
)

# Base class for our models
Base = declarative_base()

# Dependency to get the database session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
