"""Main CrewAI orchestration for code analysis."""

from typing import Any

from crewai import Crew, Process

from src.crew.tasks import (
    create_code_quality_analysis_task,
    create_performance_analysis_task,
    create_report_consolidation_task,
)


class CodeAnalysisCrew:
    """
    Orchestrates the code analysis crew with multiple specialized agents.

    This crew coordinates three agents:
    1. Performance Analyzer - Focuses on performance optimization
    2. Code Quality Analyzer - Focuses on maintainability and best practices
    3. Report Writer - Consolidates findings into actionable report
    """

    def __init__(self):
        """Initialize the Code Analysis Crew."""
        self.crew = None

    def analyze_code(self, code: str) -> dict[str, Any]:
        """
        Analyze Python code using the crew of specialized agents.

        This method orchestrates the analysis workflow:
        1. Performance analyzer examines the code for optimization opportunities
        2. Code quality analyzer reviews for best practices and maintainability
        3. Report writer consolidates both analyses into a unified report

        Args:
            code: Python code string to analyze

        Returns:
            Dictionary containing:
                - suggestions: Consolidated markdown report with all recommendations
                - performance_analysis: Raw performance analysis (optional)
                - quality_analysis: Raw quality analysis (optional)
                - status: 'success' or 'error'
                - error: Error message if status is 'error'

        Raises:
            Exception: If crew analysis fails
        """
        try:
            print("[CREW] Starting code analysis workflow...")

            # Create tasks for the analysis
            performance_task = create_performance_analysis_task(code)
            quality_task = create_code_quality_analysis_task(code)

            print("[CREW] Created performance and quality analysis tasks")

            # Create the crew with sequential process
            # Tasks will execute in order: performance -> quality -> report
            crew = Crew(
                agents=[
                    performance_task.agent,
                    quality_task.agent,
                ],
                tasks=[performance_task, quality_task],
                process=Process.sequential,
                verbose=True,
            )

            print("[CREW] Executing performance and quality analysis...")

            # Execute the initial analysis tasks
            result = crew.kickoff()

            print("[CREW] Initial analysis complete. Consolidating report...")

            # Extract the task outputs
            performance_output = (
                performance_task.output.raw
                if hasattr(performance_task.output, "raw")
                else str(performance_task.output)
            )
            quality_output = (
                quality_task.output.raw
                if hasattr(quality_task.output, "raw")
                else str(quality_task.output)
            )

            # Create report consolidation task
            report_task = create_report_consolidation_task(
                code=code,
                performance_analysis=performance_output,
                quality_analysis=quality_output,
            )

            # Create a new crew for report consolidation
            report_crew = Crew(
                agents=[report_task.agent],
                tasks=[report_task],
                process=Process.sequential,
                verbose=True,
            )

            print("[CREW] Generating final consolidated report...")

            # Generate the final report
            final_result = report_crew.kickoff()

            # Extract the final report
            final_report = (
                final_result.raw if hasattr(final_result, "raw") else str(final_result)
            )

            print("[CREW] Analysis workflow completed successfully")

            return {
                "suggestions": final_report,
                "performance_analysis": performance_output,
                "quality_analysis": quality_output,
                "status": "success",
            }

        except Exception as e:
            error_msg = f"Crew analysis failed: {str(e)}"
            print(f"[CREW ERROR] {error_msg}")

            # Return a user-friendly error message
            return {
                "suggestions": (
                    "## Analysis Error\n\n"
                    "We encountered an error while analyzing your code. "
                    "This could be due to:\n"
                    "- Syntax errors in the provided code\n"
                    "- Complexity beyond current analysis capabilities\n"
                    "- Temporary service issues\n\n"
                    f"**Error details**: {str(e)}\n\n"
                    "Please check your code syntax and try again. If the problem "
                    "persists, contact support."
                ),
                "status": "error",
                "error": error_msg,
            }

    async def analyze_code_async(self, code: str) -> dict[str, Any]:
        """
        Async wrapper for analyze_code.

        CrewAI's kickoff is synchronous, so this method runs it in a way that's
        compatible with async contexts (FastAPI endpoints).

        Args:
            code: Python code string to analyze

        Returns:
            Dictionary containing analysis results (same as analyze_code)
        """
        # Note: CrewAI's kickoff() is synchronous, but we can call it directly
        # since Python's asyncio will handle it appropriately. For true async
        # execution, you might want to use run_in_executor in production.
        return self.analyze_code(code)
