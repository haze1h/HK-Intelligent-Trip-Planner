# HK Intelligent Trip Planner

A course project that generates multi-day Hong Kong travel itineraries with a local LLM.

The system combines a React + TypeScript frontend, a FastAPI backend, budget estimation logic, itinerary generation, and itinerary critique.

---

## Project Overview

This project accepts user inputs such as trip duration, total budget, pace, preferences, and must-include activities, then generates a Hong Kong itinerary.

### Main components

- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI
- **LLM runtime**: Ollama
- **Model**: `mistral:7b`
- **Dataset**: `data/hk_activities.json`

### Current workflow

1. User submits trip requirements in the frontend.
2. Frontend sends a `POST` request to `/api/travel-plan`.
3. Backend normalizes the request.
4. Budget logic estimates fixed trip costs and available activity budget.
5. Planner agent calls the local LLM to generate the itinerary.
6. Critic agent evaluates the result.
7. Backend returns itinerary + budget summary + critique report.

---

## Project Structure

```text
HK-Intelligent-Trip-Planner/
├─ frontend/                      # React frontend
│  ├─ src/
│  ├─ public/                     # only if present
│  ├─ package.json
│  ├─ package-lock.json
│  ├─ vite.config.ts
│  ├─ index.html
│  ├─ tailwind.config.js
│  ├─ postcss.config.js
│  └─ .env.example
├─ budget_tool/                   # Budget estimation module
├─ critic_agent/                  # Itinerary evaluation module
├─ planner_agent/                 # Planner + prompt + schema + Ollama client
├─ data/
│  └─ hk_activities.json          # Activity dataset
├─ api_server.py                  # FastAPI backend entry
├─ requirements.txt               # Python dependencies
├─ README.md                      # Project documentation
├─ RUN_GUIDE.md                   # Local run instructions
└─ .gitignore
```

---

## Features

- Multi-day Hong Kong itinerary generation
- Budget-aware planning
- Pace control (`relaxed`, `moderate`, `packed`)
- Preference-based activity selection
- Local LLM deployment with Ollama
- Frontend-backend integrated workflow
- Health check API for quick debugging

---

## Tech Stack

### Frontend

- React 18
- TypeScript
- Vite
- Tailwind CSS
- Lucide React

### Backend

- FastAPI
- Pydantic
- Uvicorn
- Ollama Python client

### Local LLM

- Ollama
- `mistral:7b`

---

## Environment Requirements

Install these first:

- Python 3.10+
- Node.js 18+
- npm
- Ollama

---

## LLM Setup

This project uses a **local** Mistral 7B model through Ollama.

### Install the model

```bash
ollama pull mistral:7b
```

### Start Ollama

```bash
ollama serve
```

If Ollama is not running, the backend may return errors such as:

- `Failed to generate itinerary`
- `Planner output is invalid`
- `503 Service Unavailable`

---

## Backend Setup

In the project root directory:

```bash
pip install -r requirements.txt
uvicorn api_server:app --reload --host 127.0.0.1 --port 8000
```

### Backend health check

Open this URL in the browser after starting the backend:

```text
http://127.0.0.1:8000/api/health
```

A healthy response should contain fields like:

- `ok`
- `model`
- `data_path`
- `activities_loaded`

---

## Frontend Setup

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

By default, Vite runs at:

```text
http://127.0.0.1:5173
```

---

## Frontend Environment Variables

Copy `.env.example` to `.env` inside the `frontend/` directory.

Example:

```env
VITE_API_URL=/api/travel-plan
VITE_USE_MOCK=false
```

### Notes

- `VITE_USE_MOCK=false` means the frontend will call the real backend.
- `VITE_API_URL=/api/travel-plan` works with the Vite proxy configuration.

---

## API

### `GET /api/health`

Checks whether the backend and dataset load correctly.

### `POST /api/travel-plan`

Generates a travel plan.

Example request body:

```json
{
  "destination": "Hong Kong",
  "days": 3,
  "total_budget_hkd": 3000,
  "preferences": ["food", "nature"],
  "pace": "moderate",
  "must_include": ["Victoria Peak"],
  "avoid": ["Disneyland"],
  "travelers": 2,
  "budget_style": "standard"
}
```

---

## Common Errors

### 1. `500 Internal Server Error`

Possible causes:

- Dataset path not found
- Python dependency missing
- Planner output validation failed

### 2. `503 Service Unavailable`

Possible causes:

- Ollama is not running
- `mistral:7b` is not installed
- Backend cannot connect to Ollama

### 3. `Planner output is invalid`

This usually means the backend successfully called the model, but the model returned an incomplete or invalid itinerary.

Example:

- requested `days = 6`
- model only returned 1 itinerary day
- backend validation rejected the result

This is a **backend / LLM-generation issue**, not a frontend rendering issue.

---

## What to Upload to GitHub

You should upload the **project source code and documentation**, not your entire local environment.

### Upload these files and folders

```text
frontend/
budget_tool/
critic_agent/
planner_agent/
data/
api_server.py
requirements.txt
README.md
RUN_GUIDE.md
.gitignore
```

If these files are part of the project and needed to run it, keep them too:

```text
frontend/package.json
frontend/package-lock.json
frontend/vite.config.ts
frontend/index.html
frontend/tailwind.config.js
frontend/postcss.config.js
frontend/.env.example
```

### Do NOT upload these

```text
node_modules/
.venv/
venv/
__pycache__/
.pytest_cache/
dist/
build/
.env
.vscode/
.idea/
*.log
*.zip
*.rar
*.7z
```

### Do NOT upload the local Mistral model

Do **not** upload:

- Ollama model weights
- local model cache
- any large runtime files created by Ollama

Instead, explain in `README.md` that users should run:

```bash
ollama pull mistral:7b
ollama serve
```

---

## Recommended `.gitignore`

Use this in the project root:

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.venv/
venv/
env/
.env
.pytest_cache/

# Frontend
node_modules/
dist/
build/

# Logs
*.log

# IDE
.vscode/
.idea/

# OS files
.DS_Store
Thumbs.db

# Archives
*.zip
*.rar
*.7z

# Notebook
.ipynb_checkpoints/
```

---

## How to Upload This Project to GitHub

### Option 1: Upload with Git command line

#### Step 1: Open terminal in the project root

Example:

```bash
cd "C:\Users\YourName\Desktop\HK-Intelligent-Trip-Planner"
```

#### Step 2: Initialize Git

```bash
git init
```

#### Step 3: Add `.gitignore`

Create a `.gitignore` file in the root directory and paste the recommended content above.

#### Step 4: Check what will be uploaded

```bash
git status
```

Make sure these are **not** listed:

- `node_modules`
- `.venv`
- `__pycache__`
- model files
- zip files

#### Step 5: Add project files

```bash
git add .
```

#### Step 6: Commit

```bash
git commit -m "Initial commit for HK Intelligent Trip Planner"
```

#### Step 7: Create a GitHub repository

On GitHub:

1. Click **New repository**
2. Enter repository name, for example:
   - `HK-Intelligent-Trip-Planner`
3. Choose **Public** or **Private**
4. Click **Create repository**

#### Step 8: Connect local project to GitHub

Copy the repository URL from GitHub, then run:

```bash
git remote add origin https://github.com/YOUR_USERNAME/HK-Intelligent-Trip-Planner.git
```

#### Step 9: Push to GitHub

```bash
git branch -M main
git push -u origin main
```

---

### Option 2: Upload through GitHub website

If you do not want to use command line:

1. Create a new repository on GitHub.
2. Click **uploading an existing file**.
3. Drag these folders/files into the page:
   - `frontend/`
   - `budget_tool/`
   - `critic_agent/`
   - `planner_agent/`
   - `data/`
   - `api_server.py`
   - `requirements.txt`
   - `README.md`
   - `RUN_GUIDE.md`
   - `.gitignore`
4. Do **not** drag:
   - `node_modules/`
   - `.venv/`
   - `__pycache__/`
   - any zip package
   - any model file
5. Commit the upload.

---

## Before Pushing: Final Checklist

Make sure your repository contains:

- source code
- dataset file required by the project
- dependency files
- README
- `.gitignore`

Make sure your repository does **not** contain:

- local Python environment
- `node_modules`
- cache folders
- logs
- model weights
- zip archives

---

## Suggested Submission Notes

If this is for a course project, you can describe it like this:

> This project is a Hong Kong intelligent trip planner that integrates a React frontend, a FastAPI backend, and a locally deployed LLM through Ollama. The system accepts user travel preferences and budget, then generates a multi-day itinerary with budget analysis and quality critique.

---

## Acknowledgements

- FastAPI
- React
- Vite
- Tailwind CSS
- Ollama
- Mistral 7B

