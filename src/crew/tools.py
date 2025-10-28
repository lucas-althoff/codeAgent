"""Custom tools for CrewAI agents to analyze code."""

import ast
from typing import Any

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class CodeAnalysisInput(BaseModel):
    """Input schema for code analysis tools."""

    code: str = Field(..., description="Python code to analyze")


class ASTAnalyzerTool(BaseTool):
    """Tool to parse and analyze Python code AST."""

    name: str = "AST Analyzer"
    description: str = (
        "Analyzes Python code by parsing its Abstract Syntax Tree (AST). "
        "Useful for understanding code structure, complexity, and identifying patterns. "
        "Returns detailed information about functions, classes, imports, and complexity metrics."
    )
    args_schema: type[BaseModel] = CodeAnalysisInput

    def _run(self, code: str) -> str:
        """
        Parse and analyze Python code AST.

        Args:
            code: Python code to analyze

        Returns:
            Analysis results as formatted string
        """
        try:
            tree = ast.parse(code)
            analysis = {
                "functions": [],
                "classes": [],
                "imports": [],
                "complexity_indicators": [],
            }

            for node in ast.walk(tree):
                # Analyze functions
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        "name": node.name,
                        "args": len(node.args.args),
                        "decorators": len(node.decorator_list),
                        "line": node.lineno,
                    }
                    analysis["functions"].append(func_info)

                    # Check for nested loops (complexity indicator)
                    for child in ast.walk(node):
                        if isinstance(child, (ast.For, ast.While)):
                            for nested in ast.walk(child):
                                if nested != child and isinstance(
                                    nested, (ast.For, ast.While)
                                ):
                                    analysis["complexity_indicators"].append(
                                        f"Nested loop in function '{node.name}' at line {node.lineno}"
                                    )

                # Analyze classes
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "methods": len(
                            [
                                n
                                for n in node.body
                                if isinstance(n, ast.FunctionDef)
                            ]
                        ),
                        "line": node.lineno,
                    }
                    analysis["classes"].append(class_info)

                # Analyze imports
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis["imports"].append(alias.name)
                    else:
                        module = node.module or ""
                        analysis["imports"].append(module)

            # Format results
            result = "## AST Analysis Results\n\n"

            if analysis["functions"]:
                result += "### Functions:\n"
                for func in analysis["functions"]:
                    result += f"- `{func['name']}`: {func['args']} arguments, {func['decorators']} decorators (line {func['line']})\n"
                result += "\n"

            if analysis["classes"]:
                result += "### Classes:\n"
                for cls in analysis["classes"]:
                    result += f"- `{cls['name']}`: {cls['methods']} methods (line {cls['line']})\n"
                result += "\n"

            if analysis["imports"]:
                result += f"### Imports:\n{len(analysis['imports'])} import(s) detected\n\n"

            if analysis["complexity_indicators"]:
                result += "### Complexity Indicators:\n"
                for indicator in analysis["complexity_indicators"]:
                    result += f"- {indicator}\n"
            else:
                result += "### Complexity: No major complexity issues detected\n"

            return result

        except SyntaxError as e:
            return f"Syntax Error: Unable to parse code. Error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return f"Error analyzing code: {str(e)}"


class CodeMetricsTool(BaseTool):
    """Tool to calculate code metrics like lines of code, complexity, etc."""

    name: str = "Code Metrics Calculator"
    description: str = (
        "Calculates various code metrics including lines of code, "
        "cyclomatic complexity estimates, comment ratio, and code quality indicators. "
        "Useful for quantitative analysis and performance assessment."
    )
    args_schema: type[BaseModel] = CodeAnalysisInput

    def _run(self, code: str) -> str:
        """
        Calculate code metrics.

        Args:
            code: Python code to analyze

        Returns:
            Metrics as formatted string
        """
        try:
            lines = code.split("\n")
            total_lines = len(lines)
            blank_lines = sum(1 for line in lines if not line.strip())
            comment_lines = sum(
                1 for line in lines if line.strip().startswith("#")
            )
            code_lines = total_lines - blank_lines - comment_lines

            # Parse AST for complexity
            tree = ast.parse(code)
            function_count = sum(
                1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
            )
            class_count = sum(
                1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
            )

            # Simple complexity estimation
            complexity_score = 0
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.For, ast.While, ast.With)):
                    complexity_score += 1
                elif isinstance(node, (ast.Try, ast.ExceptHandler)):
                    complexity_score += 1

            # Calculate averages
            avg_function_complexity = (
                complexity_score / function_count if function_count > 0 else 0
            )

            result = "## Code Metrics\n\n"
            result += f"**Total Lines:** {total_lines}\n"
            result += f"**Code Lines:** {code_lines}\n"
            result += f"**Blank Lines:** {blank_lines}\n"
            result += f"**Comment Lines:** {comment_lines}\n"
            result += f"**Comment Ratio:** {(comment_lines / total_lines * 100) if total_lines > 0 else 0:.1f}%\n\n"
            result += f"**Functions:** {function_count}\n"
            result += f"**Classes:** {class_count}\n"
            result += f"**Estimated Complexity Score:** {complexity_score}\n"
            result += f"**Average Function Complexity:** {avg_function_complexity:.2f}\n\n"

            # Quality indicators
            result += "### Quality Indicators:\n"
            if comment_lines / total_lines < 0.1 and total_lines > 10:
                result += "- ⚠️ Low comment ratio (< 10%)\n"
            if avg_function_complexity > 10:
                result += "- ⚠️ High average function complexity\n"
            if code_lines > 500:
                result += "- ⚠️ Large file size (> 500 lines)\n"
            if not any(
                [
                    comment_lines / total_lines < 0.1,
                    avg_function_complexity > 10,
                    code_lines > 500,
                ]
            ):
                result += "- ✓ No major quality concerns detected\n"

            return result

        except Exception as e:
            return f"Error calculating metrics: {str(e)}"


class BestPracticesCheckerTool(BaseTool):
    """Tool to check Python best practices and coding standards."""

    name: str = "Best Practices Checker"
    description: str = (
        "Checks code against Python best practices including PEP 8 naming conventions, "
        "SOLID principles, DRY principle, proper error handling, and common anti-patterns. "
        "Provides specific recommendations for improvements."
    )
    args_schema: type[BaseModel] = CodeAnalysisInput

    def _run(self, code: str) -> str:
        """
        Check code against best practices.

        Args:
            code: Python code to analyze

        Returns:
            Best practices analysis as formatted string
        """
        try:
            tree = ast.parse(code)
            issues = []
            recommendations = []

            for node in ast.walk(tree):
                # Check function naming (should be snake_case)
                if isinstance(node, ast.FunctionDef):
                    if node.name != node.name.lower() or " " in node.name:
                        issues.append(
                            f"Function '{node.name}' (line {node.lineno}) doesn't follow snake_case naming"
                        )

                    # Check for long functions (> 50 lines is a code smell)
                    if hasattr(node, "end_lineno") and hasattr(node, "lineno"):
                        func_length = node.end_lineno - node.lineno
                        if func_length > 50:
                            issues.append(
                                f"Function '{node.name}' is too long ({func_length} lines). Consider breaking it down."
                            )
                            recommendations.append(
                                f"Refactor '{node.name}' into smaller, single-responsibility functions"
                            )

                    # Check for too many parameters
                    if len(node.args.args) > 5:
                        issues.append(
                            f"Function '{node.name}' has too many parameters ({len(node.args.args)})"
                        )
                        recommendations.append(
                            f"Consider using a configuration object or dataclass for '{node.name}'"
                        )

                # Check class naming (should be PascalCase)
                elif isinstance(node, ast.ClassDef):
                    if not node.name[0].isupper():
                        issues.append(
                            f"Class '{node.name}' (line {node.lineno}) should use PascalCase naming"
                        )

                # Check for bare except clauses
                elif isinstance(node, ast.ExceptHandler):
                    if node.type is None:
                        issues.append(
                            f"Bare except clause detected (line {node.lineno}). Catch specific exceptions."
                        )
                        recommendations.append(
                            "Replace bare 'except:' with specific exception types"
                        )

                # Check for mutable default arguments
                elif isinstance(node, ast.FunctionDef):
                    for default in node.args.defaults:
                        if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                            issues.append(
                                f"Mutable default argument in '{node.name}' (line {node.lineno})"
                            )
                            recommendations.append(
                                f"Use None as default and initialize inside '{node.name}'"
                            )

            result = "## Best Practices Analysis\n\n"

            if issues:
                result += "### Issues Found:\n"
                for issue in issues[:10]:  # Limit to top 10
                    result += f"- {issue}\n"
                result += "\n"
            else:
                result += "### ✓ No major best practice violations detected\n\n"

            if recommendations:
                result += "### Recommendations:\n"
                for rec in recommendations[:8]:  # Limit to top 8
                    result += f"- {rec}\n"

            return result

        except Exception as e:
            return f"Error checking best practices: {str(e)}"


# Initialize tools for use in agents
ast_analyzer_tool = ASTAnalyzerTool()
code_metrics_tool = CodeMetricsTool()
best_practices_checker_tool = BestPracticesCheckerTool()
