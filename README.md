# LLM Council Frontend

**Note:** LLM-Council-Fork is my fork of the [llm-council](https://github.com/karpathy/llm-council) repository from Andrej Karpathy.

## Project Summary

**LLM Council** is a local web application that orchestrates a multi-stage deliberation process among various Large Language Models (LLMs) (like GPT-5, Claude, Gemini, Grok) to answer user queries.

The process consists of 3 stages:

1. **Stage 1 (First Opinions):** All models answer the user query individually.
2. **Stage 2 (Peer Review):** Models anonymously review and rank their peers' answers.
3. **Stage 3 (Synthesis):** A "Chairman" model synthesizes a final answer based on the reviews.

### Architecture

* **Frontend:** React + Vite (running on port 5173).
* **Backend:** Python FastAPI + uv (running on port 8001).
* **AI:** Uses OpenRouter API.

### Running the Frontend

Ensure the backend is running first (port 8001), then:

```bash
npm install
npm run dev
```

---

# React + Vite (Original Template Info)

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

* [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
* [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
