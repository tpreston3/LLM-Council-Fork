# Technology Stack

## Backend
- **Language:** Python 3.10+
- **Framework:** FastAPI
- **Package Manager:** `uv`
- **Networking:** `httpx` (async HTTP client for API interactions)
- **AI Integration:** OpenRouter API (Universal LLM gateway)

## Frontend
- **Framework:** React
- **Build Tool:** Vite
- **Package Manager:** `npm`
- **Styling:** CSS Modules
- **Content Rendering:** `react-markdown` (for model responses)

## Storage & Data
- **Persistence:** Local JSON files stored in `data/conversations/`
- **Data Format:** Standard JSON for conversation threads and model rankings

## Architecture
- **Type:** Client-Server (Decoupled)
- **Communication:** RESTful API between React frontend and FastAPI backend
