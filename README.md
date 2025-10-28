# Mirante - Code Agent

## Description  
Agent module that provides code optimization suggestions based on Python best practices using crewAI. 

## Installing and running

> If you don't have uv installed yet we suggest you doing so by following the official one-line install [guide](https://docs.astral.sh/uv/getting-started/installation)... (this docs consider you have uv installed)

Install dependencies:
```bash
uv sync
```

Run Backend (with auto-reload):
```bash
uv run uvicorn src.app:app --reload
```

Run Frontend (for testing):
```bash
python -m streamlit run src/ui/app.py
```

## Stack

- Backend: FastAPI + Python 3.13
- MAS Framework: CrewAI
- Database: Postgres
- Database migrations: Flyway
- Deploy: Docker

## Components:

  1. **FastAPI Entrypoint**

  - Complete FastAPI application with CORS middleware
  - Lifespan management for startup/shutdown events
  - API documentation at /docs and /redoc
  - Root redirect to documentation
  - Configured for development and production

2. **CrewAI agents:**
   1. Performance analyser: Must suggest code changes based on performance improvements reasons and best practices 
   2. Code Quality analyser: Must suggest code changes based on code quality, clean code, SOLID principles, and best practices
   3. Report writer: Must consolidate the answers coming from the analyser into a single user friendly answer respecting markdown formatting

3. **Postgres DB:**
- Postgres instance with vector engine if we want to add semantic search in the future
- 1 table named analysis_history with id, code_snippet, suggestions, created_at columns

4. **Streamlit UI:**
- UI made for testing and showcasing the solution:
  1. **Code Input**: Easy-to-use text area for entering Python code
  2. **AI Analysis**: Get comprehensive code analysis from CrewAI agents
  3. **Results Display**: Beautiful markdown rendering of analysis results
  4. **History**: View past analyses
  5. **Examples**: Pre-loaded code examples to try
  6. **Settings**: Configure API endpoint and check health status

## How to Use

  1. Set up environment:

  > Add your OpenAI API key to .env
  `OPENAI_API_KEY=your-actual-openai-api-key`

  2. Run the application:

  `uv run uvicorn src.app:app --reload`

  1. Access the API:

  - API Documentation: http://localhost:8000/docs
  - Health Check: http://localhost:8000/api/v1/health
  - Code Analysis: POST to http://localhost:8000/api/v1/analyze-code

  4. Example Request:

 ```json
  {
    "code": "def calculate_sum(numbers):\n    total = 0\n    for num in numbers:\n        total = total + num\n    return total"
  }
```

### Overview of the Setup Steps:
  1. Add your OpenAI API key to .env
  2. Ensure PostgreSQL is running on localhost:5434
  3. Run database migrations if needed
  4. Start the application and test with the /analyze-code endpoint

### Key Features

  ✅ Modular Design: Agents, tools, and tasks are separate and maintainable
  ✅ Comprehensive Prompts: Each agent has detailed instructions and backstory
  ✅ Multiple Analysis Angles: Performance + Quality + Consolidated Report
  ✅ Tool Integration: Custom tools for AST analysis, metrics, and best practices
  ✅ Error Handling: Graceful degradation with user-friendly error messages
  ✅ Database Integration: All analyses saved for history tracking
  ✅ Production Ready: CORS, logging, health checks, proper async handling

## Next Steps (Scalability Improvements)

- Include prompt Caching: Redis
- Include virtual machine for running tests in the background
- Include a task organizer to act as a todo list creator for enabling consistency
- Include Guard rails for detecting malicious requests
- Provide the capabilities as a MCP server
- Launching both analyses in PARALLEL could improve the crew performance


