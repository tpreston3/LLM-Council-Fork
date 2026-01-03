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
*   **API Provider:** OpenRouter (accesses models like GPT-4, Claude 3, Gemini, Grok, etc.)
*   **Key Modules:**
    *   `backend/main.py`: Application entry point and API routes.
    *   `backend/council.py`: Orchestrates the 3-stage deliberation flow.
    *   `backend/openrouter.py`: Handles API interactions with OpenRouter.
    *   `backend/config.py`: Configuration for model selection and API keys.

### Frontend
*   **Framework:** React
*   **Build Tool:** Vite
*   **Package Manager:** `npm`
*   **Styling:** CSS Modules, Light Mode theme.
*   **Key Components:**
    *   `components/Stage1.jsx`: Tabbed view of individual model responses.
    *   `components/Stage2.jsx`: Displays raw peer evaluations and calculated rankings.
    *   `components/Stage3.jsx`: Shows the final synthesized answer.

### Data & Storage
*   **Storage:** JSON-based filesystem storage in `data/conversations/`.
*   **Metadata:** Runtime metadata (like peer review mappings) is sent to the frontend but not persisted in the JSON storage.

## Setup & Development

### Prerequisites
*   **Python:** Managed via `uv`.
*   **Node.js:** Required for the frontend.
*   **API Key:** An OpenRouter API key is required.

### Configuration
1.  Create a `.env` file in the root directory:
    ```env
    OPENROUTER_API_KEY=sk-or-v1-...
    ```
2.  (Optional) Edit `backend/config.py` to change the Council members or Chairman model.

### Installation

**Backend:**
```bash
uv sync
```

**Frontend:**
```bash
cd frontend
npm install
cd ..
```

### Running the Application

**Option 1: All-in-one (Bash Script)**
```bash
./start.sh
```

**Option 2: Manual Start**

*   **Backend (Port 8001):**
    *   *Must be run from the project root to ensure module resolution works.*
    ```bash
    uv run python -m backend.main
    ```

*   **Frontend (Port 5173):**
    ```bash
    cd frontend
    npm run dev
    ```

## Conventions & Guidelines

*   **Module Execution:** Always run the backend as a module (`python -m backend.main`) from the root directory. Do not run `python main.py` directly from inside the `backend` folder.
*   **Ports:** The backend is explicitly configured to run on **port 8001** to avoid common conflicts on port 8000.
*   **Imports:** The backend uses relative imports (e.g., `from .config import ...`).
*   **Formatting:** The project relies on standard Python and JavaScript formatting tools.
*   **Vibe Code:** The project describes itself as "vibe coded," implying a focus on functionality and experimentation over rigid enterprise patterns, though the structure is clean and modular.
