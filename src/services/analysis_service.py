"""Service layer for code analysis operations."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from src.db.connection import get_db_connection


async def create_analysis(code_snippet: str, suggestions: str) -> dict[str, Any]:
    """
    Create a new analysis record in the database.

    Args:
        code_snippet: The code that was analyzed (will be truncated to 255 chars)
        suggestions: The analysis suggestions in markdown format

    Returns:
        Dictionary containing the created record data

    Raises:
        Exception: If database operation fails
    """
    async with get_db_connection() as conn:
        # Truncate code snippet to fit the column size
        truncated_code = code_snippet[:255]

        result = await conn.fetchrow(
            """
            INSERT INTO analysis_history (code_snippet, suggestions, created_at)
            VALUES ($1, $2, NOW())
            RETURNING id, code_snippet, suggestions, created_at
            """,
            truncated_code,
            suggestions,
        )

        return {
            "analysis_id": result["id"],
            "code_snippet": result["code_snippet"],
            "suggestions": result["suggestions"],
            "created_at": result["created_at"],
        }


async def get_analysis_by_id(analysis_id: UUID) -> Optional[dict[str, Any]]:
    """
    Retrieve a specific analysis by ID.

    Args:
        analysis_id: UUID of the analysis record

    Returns:
        Dictionary containing the analysis record or None if not found
    """
    async with get_db_connection() as conn:
        row = await conn.fetchrow(
            """
            SELECT id, code_snippet, suggestions, created_at
            FROM analysis_history
            WHERE id = $1
            """,
            analysis_id,
        )

        if row:
            return {
                "id": row["id"],
                "code_snippet": row["code_snippet"],
                "suggestions": row["suggestions"],
                "created_at": row["created_at"],
            }

        return None


async def get_analysis_history(limit: int = 10, offset: int = 0) -> list[dict[str, Any]]:
    """
    Retrieve recent analysis history from the database.

    Args:
        limit: Maximum number of records to retrieve
        offset: Number of records to skip (for pagination)

    Returns:
        List of analysis history records as dictionaries
    """
    async with get_db_connection() as conn:
        rows = await conn.fetch(
            """
            SELECT id, code_snippet, suggestions, created_at
            FROM analysis_history
            ORDER BY created_at DESC
            LIMIT $1 OFFSET $2
            """,
            limit,
            offset,
        )

        return [
            {
                "id": row["id"],
                "code_snippet": row["code_snippet"],
                "suggestions": row["suggestions"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]


async def get_analysis_count() -> int:
    """
    Get the total count of analysis records.

    Returns:
        Total number of analysis records in the database
    """
    async with get_db_connection() as conn:
        result = await conn.fetchval(
            """
            SELECT COUNT(*) FROM analysis_history
            """
        )

        return result or 0


async def check_database_connection() -> bool:
    """
    Check if database connection is healthy.

    Returns:
        True if database is accessible, False otherwise
    """
    try:
        async with get_db_connection() as conn:
            await conn.fetchval("SELECT 1")
        return True
    except Exception as e:
        print(f"[DB HEALTH] Database connection check failed: {e}")
        return False
