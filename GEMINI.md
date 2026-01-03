# LLM Council - Project Context

## Project Overview

**LLM Council** is a local web application that orchestrates a multi-stage deliberation process among various Large Language Models (LLMs) to answer user queries. It mimics a "council" setting where models first answer individually, then peer-review each other's work (anonymized), and finally, a "Chairman" model synthesizes a definitive response.

### Core Logic (The 3 Stages)
1.  **Stage 1 (First Opinions):** The user query is sent to all configured "Council" models in parallel.
2.  **Stage 2 (Peer Review):** Each model receives the anonymized responses of its peers and ranks them based on accuracy and insight.
3.  **Stage 3 (Synthesis):** A designated "Chairman" model reviews the original query, all individual responses, and the peer rankings to produce a final, synthesized answer.

## Tech Stack & Architecture

### Backend
*   **Language:** Python 3.10+
*   **Framework:** FastAPI
*   **Package Manager:** `uv`
*   **API Provider:** OpenRouter
*   **Key Modules:**
    *   `backend/main.py`: **Entry Point**. Application routes and logic.
    *   `backend/council.py`: Orchestrates the 3-stage deliberation flow.
    *   `backend/openrouter.py`: Handles API interactions with OpenRouter.
    *   `backend/config.py`: Configuration. **Check this file to see active models.**
    *   `main.py`: (Root) Stub file, do not use.

### Frontend
*   **Framework:** React + Vite
*   **Styling:** CSS Modules, Light Mode theme.
*   **Key Components:** `Stage1.jsx` (Opinions), `Stage2.jsx` (Peer Review), `Stage3.jsx` (Chairman Synthesis).

### Current Model Configuration (`backend/config.py`)
*   **Council Members:**
    *   `openai/gpt-5.2-pro`
    *   `google/gemini-3-pro-preview`
    *   `google/gemini-3-flash-preview`
    *   `anthropic/claude-sonnet-4.5`
    *   `x-ai/grok-4-fast`
*   **Chairman:** `google/gemini-3-pro-preview`

## Setup & Development

### Prerequisites
1.  **Node.js:** Required for frontend.
2.  **uv:** Required for Python backend management.
3.  **OpenRouter API Key:** Required for model access.

### Configuration
Create a `.env` file in the `llm-council` directory:
```env
OPENROUTER_API_KEY=sk-or-v1-...
```

### Installation

**Backend:**
```bash
# From llm-council directory
uv sync
```

**Frontend:**
```bash
# From llm-council/frontend directory
npm install
```

## Running the Application

### Option 1: Windows Manual Start (Recommended)
Since `start.sh` is a Bash script and may fail with path issues on Windows, run the services manually in two separate terminals.

**Terminal 1 (Backend):**
```powershell
# Navigate to llm-council directory
cd "D:\LLM Council\llm-council"
uv run python -m backend.main
```
*Port: http://localhost:8001*

**Terminal 2 (Frontend):**
```powershell
# Navigate to frontend directory
cd "D:\LLM Council\llm-council\frontend"
npm run dev
```
*Port: http://localhost:5173*

### Option 2: Git Bash
If using Git Bash, ensure you are **inside** the `llm-council` directory before running the script:
```bash
cd llm-council
./start.sh
```
*Note: If `uv` is not in your Git Bash PATH, use Option 1.*

## Troubleshooting

*   **`uv: command not found`:** Ensure `uv` is installed and added to your system PATH. If running in Git Bash, you might need to restart the shell or use PowerShell.
*   **`cd: frontend: No such file`:** You ran the start script from the wrong directory. You must be inside `llm-council/` when executing `./start.sh`.
*   **Backend Port:** The backend is hardcoded to port **8001**.
*   **Module Error:** If you see `ModuleNotFoundError`, ensure you are running with `python -m backend.main` from the `llm-council` root, NOT inside the `backend` folder.

## Conventions
*   **Vibe Code:** Focus on functionality and experimentation.
*   **Imports:** Use relative imports in backend modules.
*   **Data:** Conversations are stored in `data/conversations/`.