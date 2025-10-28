
# codeAgents Components

## Tools Module

  Three specialized analysis tools:
  - AST Analyzer Tool: Parses code structure, identifies functions, classes, imports, and complexity indicators
  - Code Metrics Tool: Calculates LOC, cyclomatic complexity, comment ratios, and quality indicators
  - Best Practices Checker Tool: Validates PEP 8, SOLID principles, naming conventions, and anti-patterns

![Crew Architecture](https://github.com/lucas-althoff/codeAgent/blob/main/src/static/images/crew_architecture.png)

## Agents Module

  Three specialized agents with detailed backstories and goals:

  1. Performance Analyzer Agent
    - Role: Senior Performance Engineer with 15+ years experience
    - Focus: Algorithmic complexity, Python optimization, resource efficiency
    - Tools: AST Analyzer, Code Metrics
  2. Code Quality Analyzer Agent
    - Role: Principal Software Architect with 20+ years experience
    - Focus: SOLID principles, clean code, maintainability, design patterns
    - Tools: AST Analyzer, Best Practices Checker, Code Metrics
  3. Report Writer Agent
    - Role: Technical Documentation Specialist
    - Focus: Consolidating analyses into clear, actionable reports
    - Tools: None (synthesis only)

## Tasks Module

  Three comprehensive task definitions:
  - Performance Analysis Task: Deep dive into optimization opportunities
  - Code Quality Analysis Task: SOLID, clean code, and best practices evaluation
  - Report Consolidation Task: Synthesizes findings into prioritized, actionable report

## Crew Orchestration

  - CodeAnalysisCrew class orchestrates the workflow
  - Sequential process: Performance → Quality → Report
  - Error handling with user-friendly messages
  - Async-compatible for FastAPI integration

  1. Integration

## API Routes

  - Integrated CrewAI into the /analyze-code endpoint
  - Handles both successful analysis and error cases
  - Saves results to database for history tracking

## Configuration

  - Setup the OPENAI_API_KEY
  - .env file to exclude sensitive data