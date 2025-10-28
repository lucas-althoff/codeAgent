"""FastAPI routes for code analysis endpoints."""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from src.config import settings
from src.models import (
    AnalysisHistoryResponse,
    CodeAnalysisRequest,
    CodeAnalysisResponse,
    ErrorResponse,
    HealthResponse,
)
from src.services import (
    check_database_connection,
    create_analysis,
    get_analysis_history,
)

# Create API router
router = APIRouter()


@router.post(
    "/analyze-code",
    response_model=CodeAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Analyze Python code",
    description="Submit Python code for analysis. Returns optimization suggestions based on performance and code quality best practices.",
    responses={
        201: {"description": "Analysis completed successfully", "model": CodeAnalysisResponse},
        400: {"description": "Invalid request", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse},
    },
)
async def analyze_code(request: CodeAnalysisRequest) -> CodeAnalysisResponse:
    """
    Analyze Python code and provide optimization suggestions.

    This endpoint uses CrewAI agents to analyze code from multiple perspectives:
    - Performance optimization
    - Code quality and best practices
    - SOLID principles adherence

    Args:
        request: Code analysis request containing the Python code to analyze

    Returns:
        CodeAnalysisResponse containing the analysis results

    Raises:
        HTTPException: If analysis fails or code is invalid
    """
    try:
        # Import CrewAI analysis
        from src.crew import CodeAnalysisCrew

        # Initialize and run the analysis crew
        crew = CodeAnalysisCrew()
        analysis_result = await crew.analyze_code_async(request.code)

        # Check if analysis was successful
        if analysis_result["status"] == "error":
            print(f"[API] Crew analysis returned error: {analysis_result.get('error')}")
            # Still save the error response to database for tracking
            suggestions = analysis_result["suggestions"]
        else:
            suggestions = analysis_result["suggestions"]
            print("[API] Crew analysis completed successfully")

        # Save analysis to database
        result = await create_analysis(
            code_snippet=request.code,
            suggestions=suggestions,
        )

        return CodeAnalysisResponse(
            analysis_id=result["analysis_id"],
            suggestions=result["suggestions"],
            code_snippet=result["code_snippet"],
            created_at=result["created_at"],
        )

    except Exception as e:
        print(f"[API] Error analyzing code: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze code: {str(e)}",
        )


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check the health status of the API and its dependencies",
    responses={
        200: {"description": "Service is healthy", "model": HealthResponse},
        503: {"description": "Service is unhealthy", "model": ErrorResponse},
    },
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint to verify service status.

    Returns:
        HealthResponse containing service status information

    Raises:
        HTTPException: If service is unhealthy
    """
    try:
        # Check database connection
        db_healthy = await check_database_connection()

        if not db_healthy:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection is unhealthy",
            )

        return HealthResponse(
            status="healthy",
            database="connected",
            version=settings.api_version,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}",
        )


@router.get(
    "/history",
    response_model=AnalysisHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get analysis history",
    description="Retrieve recent code analysis history",
    responses={
        200: {"description": "History retrieved successfully", "model": AnalysisHistoryResponse},
        500: {"description": "Internal server error", "model": ErrorResponse},
    },
)
async def get_history(limit: int = 10, offset: int = 0) -> AnalysisHistoryResponse:
    """
    Retrieve analysis history with pagination.

    Args:
        limit: Maximum number of records to return (default: 10)
        offset: Number of records to skip (default: 0)

    Returns:
        AnalysisHistoryResponse containing list of analysis records

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        # Validate parameters
        if limit < 1 or limit > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 100",
            )

        if offset < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Offset must be non-negative",
            )

        # Get history from database
        items = await get_analysis_history(limit=limit, offset=offset)

        return AnalysisHistoryResponse(
            total=len(items),
            items=items,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error retrieving history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve history: {str(e)}",
        )
