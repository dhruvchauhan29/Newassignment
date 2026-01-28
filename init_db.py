"""Initialize database tables."""
import asyncio

from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.db.base import Base

# Import all models to register them with Base
from app.models import artifact, epic, project, run, spec, story, user


async def init_db():
    """Initialize database."""
    print(f"Creating database tables for: {settings.DATABASE_URL}")
    
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        # Drop all tables (for development)
        await conn.run_sync(Base.metadata.drop_all)
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()
    print("Database tables created successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
