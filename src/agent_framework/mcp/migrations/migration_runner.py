"""Migration runner for MCP OAuth tables."""

import os
import logging
from pathlib import Path
from typing import List

import psycopg2
from psycopg2 import sql

logger = logging.getLogger(__name__)


def get_migration_files() -> List[Path]:
    """Get all migration files in order.

    Returns:
        List of migration file paths, sorted by name
    """
    migrations_dir = Path(__file__).parent
    migration_files = sorted(migrations_dir.glob("*.sql"))
    return migration_files


def run_migration(connection, migration_file: Path):
    """Run a single migration file.

    Args:
        connection: psycopg2 connection
        migration_file: Path to migration SQL file
    """
    logger.info(f"Running migration: {migration_file.name}")

    with open(migration_file, 'r') as f:
        migration_sql = f.read()

    with connection.cursor() as cursor:
        cursor.execute(migration_sql)
        connection.commit()

    logger.info(f"Migration {migration_file.name} completed successfully")


def run_migrations(database_url: str = None):
    """Run all MCP OAuth migrations.

    Args:
        database_url: PostgreSQL connection URL (uses AGENTSHIP_AUTH_DB_URI env if not provided)
    """
    if database_url is None:
        database_url = os.getenv("AGENTSHIP_AUTH_DB_URI")

    if not database_url:
        raise ValueError("AGENTSHIP_AUTH_DB_URI environment variable not set")

    logger.info("Starting MCP OAuth migrations")

    # Connect to database
    connection = psycopg2.connect(database_url)

    try:
        # Get all migration files
        migration_files = get_migration_files()

        if not migration_files:
            logger.warning("No migration files found")
            return

        # Run each migration
        for migration_file in migration_files:
            try:
                run_migration(connection, migration_file)
            except Exception as e:
                logger.error(f"Migration {migration_file.name} failed: {e}")
                connection.rollback()
                raise

        logger.info("All MCP OAuth migrations completed successfully")

    finally:
        connection.close()


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Run migrations
    run_migrations()
