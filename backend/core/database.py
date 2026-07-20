from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings
from core.logging import logger

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def run_migrations():
    """Run Alembic migrations. Controlled by AUTO_MIGRATE env var."""
    if not settings.AUTO_MIGRATE:
        logger.info("AUTO_MIGRATE=false — checking migration status")
        _check_migration_status()
        return
    try:
        from alembic.config import Config
        from alembic import command

        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logger.info("Alembic migrations applied successfully")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


def _check_migration_status():
    """In production, verify schema is up to date without auto-migrating."""
    try:
        from alembic.config import Config
        from alembic.script import ScriptDirectory
        from alembic.runtime.environment import EnvironmentContext

        alembic_cfg = Config("alembic.ini")
        script = ScriptDirectory.from_config(alembic_cfg)

        with engine.connect() as conn:
            context = EnvironmentContext(alembic_cfg, script)
            head_revision = script.get_current_head()
            current_revision = context.get_head_revision()

        if current_revision != head_revision:
            logger.warning(
                f"Database is behind current migration. "
                f"Current: {current_revision}, Head: {head_revision}. "
                f"Run 'alembic upgrade head' manually."
            )
    except Exception as e:
        logger.warning(f"Could not verify migration status: {e}")
