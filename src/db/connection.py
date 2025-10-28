"""Database connection pool management."""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import asyncpg

from src.config import settings

# Keep one pool per running loop to avoid conflicts across workers
_pools: dict[int, asyncpg.Pool] = {}
_owns_pool: bool = True


async def get_db_pool() -> asyncpg.Pool:
    """
    Get or create a PostgreSQL connection pool tied to the current event loop.

    Returns:
        asyncpg.Pool: Connection pool for the current event loop
    """
    loop_id = id(asyncio.get_running_loop())

    if loop_id not in _pools:
        # Parse postgres URL: postgresql://user:password@host:port/database?params
        url = settings.postgres_url

        # Extract components from URL
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "")

        # Split user:pass@host:port/db?params
        auth_and_rest = url.split("@")
        user_pass = auth_and_rest[0].split(":")
        host_port_db = auth_and_rest[1].split("?")[0]
        host_port = host_port_db.split("/")[0]
        database = host_port_db.split("/")[1]
        host = host_port.split(":")[0]
        port = int(host_port.split(":")[1])

        user = user_pass[0]
        password = user_pass[1]

        _pools[loop_id] = await asyncpg.create_pool(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database,
            min_size=2,
            max_size=10,
            command_timeout=60,
        )
        print(f"[DB] Connection pool created for loop {loop_id}")

    return _pools[loop_id]


def attach_external_pool(pool: asyncpg.Pool) -> None:
    """
    Attach externally-managed pool (from lifespan/GlobalResources).

    Args:
        pool: External asyncpg pool to attach
    """
    global _owns_pool
    loop_id = id(asyncio.get_running_loop())
    _pools[loop_id] = pool
    _owns_pool = False
    print(f"[DB] External pool attached for loop {loop_id}")


async def close_db_pool() -> None:
    """Close and clean up all owned pools."""
    global _owns_pool

    for loop_id, pool in list(_pools.items()):
        try:
            if _owns_pool and pool:
                await pool.close()
                print(f"[DB] Closed pool for loop {loop_id}")
        except Exception as e:
            print(f"[DB] Error closing pool {loop_id}: {e}")
        finally:
            _pools.pop(loop_id, None)

    _owns_pool = False


@asynccontextmanager
async def get_db_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """
    Context manager for a database connection from the pool.

    Yields:
        asyncpg.Connection: Database connection from the pool

    Example:
        async with get_db_connection() as conn:
            result = await conn.fetch("SELECT * FROM analysis_history")
    """
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        try:
            yield conn
        except Exception as e:
            print(f"[DB CONN] Error during DB connection usage: {e}")
            raise
