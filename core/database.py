from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

load_dotenv()

# We expect a PostgreSQL connection string in the .env like:
# postgresql+asyncpg://user:password@host:port/dbname
DATABASE_URL = os.environ.get("DATABASE_URL")

# Provide a fallback for local testing if not set (SQLite async)
if not DATABASE_URL:
    print("WARNING: DATABASE_URL not set in .env. Falling back to local SQLite.")
    DATABASE_URL = "sqlite+aiosqlite:///./groww.db"

# Create async engine optimized for Serverless / PgBouncer environments
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True to see pure SQL logs
    poolclass=NullPool, # Prevent overlapping transaction errors when tests spawn concurrent requests
    connect_args={"statement_cache_size": 0} # Required for PgBouncer/Neon compatibility
)

# Setup async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

async def get_db():
    ""
    "FastAPI dependency to inject DB sessions into routers."
    ""
    async with AsyncSessionLocal() as session:
        yield session
