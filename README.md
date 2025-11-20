## Ocean AI Author

AI-assisted document builder that lets teams plan Word or PowerPoint deliverables, generate first drafts with Gemini-compatible prompts, refine sections slide-by-slide, and export polished `.docx` or `.pptx` files. The stack uses FastAPI, SQLModel, and React.

### Features
- Secure email/password auth with JWT sessions
- Project dashboard with Word or PowerPoint modes
- Manual or AI-suggested outlines during setup
- Section-by-section LLM generation and refinement prompts
- Like/dislike feedback tracking plus internal comments
- Downloadable Word and PowerPoint exports that mirror the latest content

### Prerequisites
- Python 3.11+
- Node 20+

### Environment

Copy `env.example` to `.env` (root) and set values.

| Key | Description |
| --- | --- |
| `DATABASE_URL` | Default SQLite path |
| `JWT_SECRET_KEY` | Secret for signing access tokens |
| `GEMINI_API_KEY` | Google Generative AI key; leave blank for fallback text |
| `VITE_API_URL` | Frontend base URL to call the API (e.g., `http://localhost:8000`) |

### Backend setup
```bash
cd server
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API auto-migrates tables on startup and exposes docs at `/docs`. Without a Gemini key the service responds with deterministic sample prose so the flow keeps working.

### Frontend setup
```bash
cd client
npm install
npm run dev
```

Vite serves the UI on `http://localhost:5173` by default and proxies requests to `VITE_API_URL`.

### Typical flow
1. Register a new account, then sign in.
2. Create a project, choose Word or PowerPoint, define or auto-suggest the outline.
3. Generate first-pass content for all sections.
4. Use per-section prompts, likes/dislikes, and comments to refine tone and structure.
5. Export the final `.docx` or `.pptx` file.

### Demo script
Record a 5–10 minute walkthrough covering:
- Registration and login
- Creating one Word project and one PowerPoint project
- Using AI Outline Suggestion
- Initial content generation
- Making refinements (prompt submission, likes/dislikes, comments)
- Exporting both file types

### Tests and linting
- Frontend: `npm run build`
- Backend: run `uvicorn app.main:app --reload` to ensure startup succeeds. Add pytest or mypy as needed for extended coverage.

### Deployment notes
- FastAPI app is stateless so it can run on any ASGI host (such as Azure App Service or Fly.io). Configure the same `.env` keys in your hosting provider.
- React build output lives in `client/dist`. Serve it from static hosting or behind a CDN, pointing API requests at the deployed backend URL.

