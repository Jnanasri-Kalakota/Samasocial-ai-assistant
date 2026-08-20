from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Determine connection URL based on type
db_url = settings.DATABASE_URL
if settings.DATABASE_TYPE == "sqlite" and "sqlite" not in db_url:
    db_url = "sqlite+aiosqlite:///./samasocial.db"
elif settings.DATABASE_TYPE in ["supabase", "postgresql"] and db_url.startswith("postgres://"):
    # Fix postgres:// URI for asyncpg
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif settings.DATABASE_TYPE in ["supabase", "postgresql"] and db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# SQLite vs Postgres engine args
engine_args = {}
if "sqlite" in db_url:
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_async_engine(
    db_url,
    echo=False,
    future=True,
    **engine_args
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)
    logger.info(f"Database initialized successfully with {settings.DATABASE_TYPE} backend.")
