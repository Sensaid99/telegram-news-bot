import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Импортируем модели и конфигурацию
from database.models import Base
from config import DATABASE_URL

# Загружаем конфигурацию Alembic
config = context.config

# Загружаем конфигурацию логирования из alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Добавляем URL базы данных в конфигурацию
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Добавляем MetaData для автогенерации миграций
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Запускает миграции в 'оффлайн' режиме.
    
    В этом режиме миграции будут запущены напрямую в базу данных,
    без использования Engine. Хорошо подходит для скриптов.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    """Запускает миграции."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Запускает асинхронные миграции."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Запускает миграции в 'онлайн' режиме.
    
    В этом режиме миграции будут запущены с использованием Engine,
    который поддерживает пул соединений.
    """
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 