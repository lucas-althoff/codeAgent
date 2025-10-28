# Streamlit UI for Code Agent

A interactive web interface for testing the Code Analysis Agent.

## Features

- 📝 **Code Input**: Easy-to-use text area for entering Python code
- 🤖 **AI Analysis**: Get comprehensive code analysis from CrewAI agents
- 📊 **Results Display**: Beautiful markdown rendering of analysis results
- 📜 **History**: View past analyses
- 💡 **Examples**: Pre-loaded code examples to try
- ⚙️ **Settings**: Configure API endpoint and check health status

## Quick Start

### 1. Install Dependencies
```bash
uv sync
```

### 2. Start the FastAPI Backend
In one terminal:
```bash
uv run uvicorn src.app:app --reload
```

The API will be available at `http://localhost:8000`

### 3. Start the Streamlit UI

In another terminal:
```bash
python -m streamlit run src/ui/app.py
```

The UI will open automatically in your browser at `http://localhost:8501`

## Usage

1. **Enter Code**: Type or paste Python code in the left panel
2. **Analyze**: Click "🔍 Analyze Code" button
3. **Review Results**: See the analysis results in the right panel
4. **Try Examples**: Use the sidebar to load pre-made examples
5. **Check History**: Load previous analyses from the sidebar

## Features Overview

### Code Examples
The sidebar includes several example code snippets:
- Inefficient Loop
- Missing Type Hints
- Long Function
- Nested Loops

### Analysis Output
The analysis provides:
- **Performance Insights**: Algorithmic complexity, optimization opportunities
- **Code Quality**: SOLID principles, code smells, best practices
- **Actionable Recommendations**: Prioritized, specific guidance

### API Health Check
Use the "Check API Health" button in the sidebar to verify the backend is running.

## Architecture

```
┌─────────────────┐
│  Streamlit UI   │ (Port 8501)
│   (Frontend)    │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│   FastAPI       │ (Port 8000)
│   (Backend)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   CrewAI        │
│   (Agents)      │
└─────────────────┘
```

## Tips

- Use the examples to understand what kind of code patterns the agent can analyze
- The analysis is more valuable for larger, more complex code snippets
- Check the analysis history to compare different versions of your code
- The UI uses a 5-minute timeout to accommodate long-running analyses
