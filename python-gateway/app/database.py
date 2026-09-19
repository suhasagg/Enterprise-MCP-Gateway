from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from .config import settings
from .models import Base
engine=create_async_engine(settings.database_url,pool_pre_ping=True)
Session=async_sessionmaker(engine,expire_on_commit=False,class_=AsyncSession)
async def init_db():
    async with engine.begin() as c: await c.run_sync(Base.metadata.create_all)
