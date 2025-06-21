import logging
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

logger = logging.getLogger(__name__)

# Создаем асинхронный движок
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Отключаем вывод SQL-запросов в лог
    pool_size=5,  # Размер пула соединений
    max_overflow=10  # Максимальное количество дополнительных соединений
)

# Создаем фабрику сессий
AsyncSessionFactory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@asynccontextmanager
async def get_session() -> AsyncSession:
    """Контекстный менеджер для работы с сессией базы данных."""
    session = AsyncSessionFactory()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        await session.close()

async def init_db():
    """Инициализирует базу данных."""
    from .models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
async def close_db():
    """Закрывает соединения с базой данных."""
    await engine.dispose() 