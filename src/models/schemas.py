"""Pydantic models for API request/response validation."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CodeAnalysisRequest(BaseModel):
    """Request model for code analysis endpoint."""

    code: str = Field(
        ...,
        description="Python code to analyze",
        min_length=1,
        max_length=10000,
        examples=["def hello():\n    print('world')"],
    )


class CodeAnalysisResponse(BaseModel):
    """Response model for code analysis endpoint."""

    analysis_id: UUID = Field(..., description="Unique identifier for this analysis")
    suggestions: str = Field(..., description="Analysis suggestions in markdown format")
    code_snippet: str = Field(..., description="Truncated code snippet that was analyzed")
    created_at: datetime = Field(..., description="Timestamp when analysis was created")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
                "suggestions": "## Performance Improvements\n- Use list comprehension\n\n## Code Quality\n- Add type hints",
                "code_snippet": "def hello():\n    print('world')",
                "created_at": "2025-01-15T10:30:00Z",
            }
        }


class AnalysisHistoryItem(BaseModel):
    """Model for a single analysis history item."""

    id: UUID = Field(..., description="Unique identifier")
    code_snippet: str = Field(..., description="Truncated code snippet")
    suggestions: Optional[str] = Field(None, description="Analysis suggestions")
    created_at: datetime = Field(..., description="Creation timestamp")


class AnalysisHistoryResponse(BaseModel):
    """Response model for analysis history list."""

    total: int = Field(..., description="Total number of items returned")
    items: list[AnalysisHistoryItem] = Field(..., description="List of analysis records")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = Field(..., description="Service status", examples=["healthy"])
    database: str = Field(..., description="Database connection status", examples=["connected"])
    version: str = Field(..., description="API version", examples=["1.0.0"])

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "status": "healthy",
                "database": "connected",
                "version": "1.0.0",
            }
        }


class ErrorResponse(BaseModel):
    """Response model for error responses."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Code cannot be empty",
                "detail": "The code field must contain at least 1 character",
            }
        }
