"""API client for communicating with the FastAPI backend."""

from typing import Any

import httpx


class CodeAnalysisClient:
    """Client for the Code Analysis API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the API client.

        Args:
            base_url: Base URL of the FastAPI application
        """
        self.base_url = base_url
        self.client = httpx.Client(timeout=300.0)  # 5 minute timeout for long analyses

    def health_check(self) -> dict[str, Any]:
        """
        Check API health status.

        Returns:
            Health check response

        Raises:
            httpx.HTTPError: If request fails
        """
        response = self.client.get(f"{self.base_url}/api/v1/health")
        response.raise_for_status()
        return response.json()

    def analyze_code(self, code: str) -> dict[str, Any]:
        """
        Submit code for analysis.

        Args:
            code: Python code to analyze

        Returns:
            Analysis response containing suggestions

        Raises:
            httpx.HTTPError: If request fails
        """
        response = self.client.post(
            f"{self.base_url}/api/v1/analyze-code",
            json={"code": code},
        )
        response.raise_for_status()
        return response.json()

    def get_history(self, limit: int = 10, offset: int = 0) -> dict[str, Any]:
        """
        Get analysis history.

        Args:
            limit: Maximum number of records to retrieve
            offset: Number of records to skip

        Returns:
            History response

        Raises:
            httpx.HTTPError: If request fails
        """
        response = self.client.get(
            f"{self.base_url}/api/v1/history",
            params={"limit": limit, "offset": offset},
        )
        response.raise_for_status()
        return response.json()

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
