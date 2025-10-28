"""CrewAI task definitions for code analysis workflow."""

from crewai import Task

from src.crew.agents import (
    create_code_quality_analyzer_agent,
    create_performance_analyzer_agent,
    create_report_writer_agent,
)


def create_performance_analysis_task(code: str) -> Task:
    """
    Create a task for performance analysis.

    Args:
        code: Python code to analyze

    Returns:
        Configured performance analysis task
    """
    return Task(
        description=(
            f"Analyze the following Python code for performance optimization opportunities:\n\n"
            f"```python\n{code}\n```\n\n"
            "Your analysis must include:\n"
            "1. **Algorithmic Complexity Analysis**: Identify the time and space complexity "
            "of functions and algorithms. Point out any O(n²) or worse operations that could "
            "be optimized to O(n log n) or O(n).\n\n"
            "2. **Data Structure Optimization**: Evaluate if the right data structures are used. "
            "For example, using sets for membership tests instead of lists, using deque for "
            "queue operations, or using defaultdict to avoid key checks.\n\n"
            "3. **Python-Specific Performance**: Identify opportunities to use:\n"
            "   - List comprehensions instead of loops with append\n"
            "   - Generators for memory efficiency with large datasets\n"
            "   - Built-in functions (sum, map, filter) instead of manual loops\n"
            "   - f-strings instead of string concatenation\n"
            "   - Local variable caching for repeatedly accessed attributes\n\n"
            "4. **Resource Management**: Check for:\n"
            "   - Unnecessary copying of data structures\n"
            "   - Redundant computations that could be cached\n"
            "   - Database query inefficiencies (N+1 queries)\n"
            "   - File I/O that could be buffered or batched\n\n"
            "5. **Concurrency Opportunities**: Identify CPU-bound or I/O-bound operations "
            "that could benefit from multiprocessing, threading, or async/await.\n\n"
            "Use your AST Analyzer and Code Metrics tools to gather data, then provide "
            "specific, actionable recommendations with code examples where helpful. "
            "Focus on changes that will have measurable impact."
        ),
        expected_output=(
            "A detailed performance analysis report in markdown format containing:\n"
            "- Identified performance bottlenecks with specific line numbers\n"
            "- Time and space complexity analysis\n"
            "- Specific optimization recommendations with code examples\n"
            "- Prioritized by potential performance impact (High/Medium/Low)\n"
            "- Estimated improvement for each recommendation"
        ),
        agent=create_performance_analyzer_agent(),
    )


def create_code_quality_analysis_task(code: str) -> Task:
    """
    Create a task for code quality analysis.

    Args:
        code: Python code to analyze

    Returns:
        Configured code quality analysis task
    """
    return Task(
        description=(
            f"Analyze the following Python code for quality, maintainability, and best practices:\n\n"
            f"```python\n{code}\n```\n\n"
            "Your analysis must include:\n\n"
            "1. **SOLID Principles Evaluation**:\n"
            "   - **Single Responsibility**: Does each class/function have one clear purpose?\n"
            "   - **Open/Closed**: Is the code open for extension but closed for modification?\n"
            "   - **Liskov Substitution**: Are inheritance hierarchies sound?\n"
            "   - **Interface Segregation**: Are interfaces minimal and focused?\n"
            "   - **Dependency Inversion**: Does the code depend on abstractions, not concretions?\n\n"
            "2. **Code Smells Detection**:\n"
            "   - Long methods/functions (> 50 lines)\n"
            "   - Large classes with too many responsibilities\n"
            "   - Duplicated code (DRY violations)\n"
            "   - Too many parameters (> 5)\n"
            "   - Deep nesting (> 3 levels)\n"
            "   - God objects or classes\n"
            "   - Feature envy\n"
            "   - Inappropriate intimacy between classes\n\n"
            "3. **Clean Code Practices**:\n"
            "   - Naming conventions (descriptive, intention-revealing names)\n"
            "   - Function/method length and complexity\n"
            "   - Comments (are they explaining 'why', not 'what'?)\n"
            "   - Error handling (specific exceptions, proper cleanup)\n"
            "   - Magic numbers and strings\n\n"
            "4. **Python Best Practices**:\n"
            "   - PEP 8 style compliance\n"
            "   - Proper use of type hints\n"
            "   - Context managers for resource handling\n"
            "   - Proper exception handling (no bare except)\n"
            "   - Pythonic idioms and patterns\n\n"
            "5. **Maintainability & Testability**:\n"
            "   - Code modularity and coupling\n"
            "   - How easy would this be to test?\n"
            "   - Documentation completeness\n\n"
            "Use your analysis tools to gather data, then provide specific refactoring "
            "recommendations. For each issue, explain WHY it's a problem and HOW to fix it."
        ),
        expected_output=(
            "A comprehensive code quality analysis report in markdown format containing:\n"
            "- SOLID principles violations with specific examples\n"
            "- Identified code smells with line numbers\n"
            "- Specific refactoring recommendations with before/after examples\n"
            "- Best practices violations and how to fix them\n"
            "- Prioritized by impact on maintainability (High/Medium/Low)"
        ),
        agent=create_code_quality_analyzer_agent(),
    )


def create_report_consolidation_task(
    code: str, performance_analysis: str, quality_analysis: str
) -> Task:
    """
    Create a task for consolidating analysis reports.

    Args:
        code: Original Python code that was analyzed
        performance_analysis: Performance analysis results
        quality_analysis: Code quality analysis results

    Returns:
        Configured report consolidation task
    """
    return Task(
        description=(
            "You have received two detailed code analysis reports. Your job is to "
            "consolidate them into a single, well-structured, user-friendly report.\n\n"
            f"**Original Code:**\n```python\n{code}\n```\n\n"
            f"**Performance Analysis:**\n{performance_analysis}\n\n"
            f"**Code Quality Analysis:**\n{quality_analysis}\n\n"
            "**Your Consolidation Tasks:**\n\n"
            "1. **Remove Redundancy**: If both reports mention the same issue from different "
            "angles (e.g., nested loops mentioned for both complexity and readability), "
            "consolidate into a single, comprehensive recommendation.\n\n"
            "2. **Prioritize by Impact**: Organize recommendations into three categories:\n"
            "   - **Critical**: Issues with significant performance impact or major "
            "maintainability concerns\n"
            "   - **Important**: Moderate improvements that should be addressed\n"
            "   - **Nice-to-Have**: Minor optimizations and polish\n\n"
            "3. **Structure the Report** with these sections:\n"
            "   - Executive Summary (2-3 sentences)\n"
            "   - Critical Issues (if any)\n"
            "   - Important Recommendations\n"
            "   - Nice-to-Have Improvements\n"
            "   - Summary of Metrics (lines of code, complexity, etc.)\n\n"
            "4. **Make it Actionable**: Each recommendation should:\n"
            "   - Clearly state the problem\n"
            "   - Explain why it matters\n"
            "   - Provide specific guidance on how to fix it\n"
            "   - Include code examples when helpful\n"
            "   - Reference specific line numbers when available\n\n"
            "5. **Use Clear Markdown Formatting**:\n"
            "   - Use proper headings (##, ###)\n"
            "   - Use bullet points for lists\n"
            "   - Use code blocks for examples\n"
            "   - Use bold for emphasis\n"
            "   - Use emojis sparingly for visual impact (⚠️ for warnings, ✅ for good practices)\n\n"
            "Remember: The goal is to give developers a clear, prioritized action plan, "
            "not to overwhelm them with information. Be concise but thorough."
        ),
        expected_output=(
            "A consolidated, well-structured code analysis report in markdown format with:\n"
            "- Executive summary\n"
            "- Prioritized recommendations (Critical/Important/Nice-to-Have)\n"
            "- Specific, actionable guidance with code examples\n"
            "- Clear formatting and professional presentation\n"
            "- All redundancy removed and overlapping issues consolidated"
        ),
        agent=create_report_writer_agent(),
    )
