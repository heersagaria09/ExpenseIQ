# ExpenseIQ — Project Documentation

Personal finance web app for tracking expenses, income, budgets, goals, and subscriptions — with AI coaching powered by Google Gemini.

**Stack:** Python · Flask · Jinja2 · MongoDB (or local file DB) · Vanilla JavaScript

---

## Table of Contents

1. [Features](#features)
2. [Project Structure](#project-structure)
3. [Prerequisites](#prerequisites)
4. [Local Setup (Windows)](#local-setup-windows)
5. [Environment Variables](#environment-variables)
6. [Database](#database)
7. [Authentication](#authentication)
8. [Web Pages](#web-pages)
9. [API Reference](#api-reference)
10. [Frontend Overview](#frontend-overview)
11. [Testing](#testing)
12. [Push to GitHub](#push-to-github)
13. [Deploy Online (No Docker)](#deploy-online-no-docker)
14. [Optional: Docker](#optional-docker)
15. [Troubleshooting](#troubleshooting)

---

## Features

| Module | What it does |
|--------|----------------|
| **Dashboard** | Monthly income, expenses, savings, health score, charts |
| **Expenses** | Add, edit, delete, filter; receipt OCR scan |
| **Income** | Track income sources with filters |
| **Budgets** | Monthly category budgets with alerts |
| **Goals** | Savings goals with contributions |
| **Subscriptions** | Recurring payments and renewal reminders |
| **Calendar** | Day-by-day expense/income view |
| **Bank Statements** | Upload PDF/CSV, parse transactions, AI analysis |
| **Analytics** | Cashflow, category breakdown, trends |
| **AI Coach** | Chat with Gemini using your financial context |
| **Settings** | Profile, theme (dark/light), data export |
| **Auth** | Email/password, mobile OTP, Google sign-in |

---

## Project Structure

```
ExpenseIQ/
├── app.py                  # Entry point — run this to start the server
├── requirements.txt        # Python dependencies
├── .env.example            # Template for environment variables
├── run_smoke.py            # Quick smoke tests
│
├── app/                    # Main application package
│   ├── __init__.py         # Flask app factory (create_app)
│   ├── config/
│   │   ├── settings.py     # App configuration (keys, paths, currency)
│   │   └── database.py     # MongoDB or local mock database
│   │
│   ├── models/             # Data access (users, expenses, budgets, etc.)
│   ├── routes/             # Flask blueprints (pages + API endpoints)
│   ├── services/           # Business logic (AI, OCR, analytics, parsing)
│   ├── utils/              # Helpers and validators
│   │
│   ├── templates/          # HTML pages (Jinja2)
│   └── static/
│       ├── css/            # Stylesheets
│       ├── js/             # Client-side JavaScript
│       ├── images/         # Icons, favicon
│       └── uploads/        # User uploads (receipts, statements)
│
├── data/
│   └── mockdb.json         # Local dev database (auto-created)
│
├── tools/                  # Dev utilities (e2e test, demos)
├── .github/workflows/      # CI pipeline on GitHub
├── render.yaml             # Render.com deploy config
├── Procfile                # Process file for cloud hosts
└── Dockerfile              # Optional container deploy (not required)
```

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| **Python 3.8+** | 3.11 recommended |
| **pip** | Comes with Python |
| **Git** | For GitHub |
| **MongoDB** | Optional — app works without it (uses local file DB) |
| **Gemini API key** | Optional — needed only for AI Coach and statement analysis |
| **Google OAuth** | Optional — needed only for Google sign-in |

---

## Local Setup (Windows)

### 1. Open the project folder

```powershell
cd "C:\Users\hp\OneDrive\Desktop\PROJECTS\ExpenseIQ"
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Create your environment file

```powershell
copy .env.example .env
```

Edit `.env` and set at least:

```env
SECRET_KEY=change-this-to-a-random-string
JWT_SECRET_KEY=change-this-to-another-random-string
FLASK_DEBUG=True
PORT=5000
```

Leave `MONGO_URI` empty to use the built-in local database (no MongoDB install needed).

### 5. Run the app

```powershell
python app.py
```

Open **http://localhost:5000** in your browser.

### 6. Create an account

1. Go to **Sign Up** → register with email and password  
2. Log in at **http://localhost:5000/login**  
3. You land on the dashboard

---

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `SECRET_KEY` | Yes (production) | built-in dev key | Flask session signing |
| `JWT_SECRET_KEY` | Yes (production) | built-in dev key | JWT token signing |
| `FLASK_DEBUG` | No | `True` | Debug mode |
| `FLASK_ENV` | No | — | Set `development` to show OTP in API response |
| `PORT` | No | `5000` | Server port |
| `MONGO_URI` | No | — | MongoDB connection string |
| `MONGODB_URI` | No | — | Alternative name for MongoDB URI |
| `DB_NAME` | No | `expenseiq` | MongoDB database name |
| `GEMINI_API_KEY` | For AI | — | Google Gemini API |
| `GOOGLE_CLIENT_ID` | For Google login | — | Google OAuth client ID |
| `FAST2SMS_API_KEY` | For SMS OTP | — | Sends OTP via Fast2SMS |

**Generate secret keys (PowerShell):**

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Run twice — once for `SECRET_KEY`, once for `JWT_SECRET_KEY`.

---

## Database

ExpenseIQ picks a database automatically:

```
1. MongoDB  →  if MONGO_URI / MONGODB_URI is set AND connection works
2. Local DB →  fallback: file at data/mockdb.json (mongomock)
```

### Option A — Local file database (easiest)

- Do **not** set `MONGO_URI` in `.env`
- Data is stored in `data/mockdb.json`
- Auto-saves every 30 seconds and on exit
- Good for development and demos

### Option B — MongoDB Atlas (cloud, free tier)

1. Create a free cluster at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create a database user and allow network access (0.0.0.0/0 for dev)
3. Copy the connection string
4. Add to `.env`:

```env
MONGO_URI=mongodb+srv://USERNAME:PASSWORD@cluster.mongodb.net/expenseiq
```

### Option C — Local MongoDB

```env
MONGO_URI=mongodb://localhost:27017/expenseiq
```

---

## Authentication

ExpenseIQ uses **Flask sessions** (cookie-based) for page access and **JWT tokens** for API clients.

| Method | Flow |
|--------|------|
| **Email / password** | POST `/api/auth/login` → session cookie + JWT returned |
| **Sign up** | POST `/api/auth/signup` → redirect to login |
| **Mobile OTP** | POST `/api/auth/send-otp` → POST `/api/auth/verify-otp` |
| **Google** | Client-side Google button → POST `/api/auth/google` |
| **Forgot password** | POST `/api/auth/forgot-password` → POST `/api/auth/reset-password` |

- Passwords are hashed with **bcrypt**
- Login is rate-limited: 10 attempts per IP per 15 minutes
- Protected pages redirect to `/login` if not signed in

---

## Web Pages

| URL | Page | Auth |
|-----|------|------|
| `/` | Landing | Public |
| `/login` | Login | Public |
| `/signup` | Sign up | Public |
| `/dashboard` | Dashboard | Required |
| `/expenses` | Expenses | Required |
| `/income` | Income | Required |
| `/analytics` | Analytics | Required |
| `/budgets` | Budgets | Required |
| `/goals` | Goals | Required |
| `/subscriptions` | Subscriptions | Required |
| `/calendar` | Calendar | Required |
| `/bank-statements` | Bank statements | Required |
| `/ai-coach` | AI Coach | Required |
| `/notifications` | Notifications | Required |
| `/settings` | Settings | Required |
| `/logout` | Sign out | — |

---

## API Reference

Base URL: `http://localhost:5000`

All `/api/*` routes (except auth signup/login/config) require an active session cookie from login.

### Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/auth/config` | Public — returns Google client ID |
| POST | `/api/auth/signup` | Register user |
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/send-otp` | Send mobile OTP |
| POST | `/api/auth/verify-otp` | Verify OTP |
| POST | `/api/auth/google` | Google OAuth login |
| POST | `/api/auth/forgot-password` | Request reset token |
| POST | `/api/auth/reset-password` | Reset password |
| POST | `/api/auth/change-password` | Change password |
| POST | `/api/auth/refresh` | Refresh JWT |
| GET | `/api/auth/me` | Current user profile |

### Finance

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/data` | Dashboard summary |
| GET/POST | `/api/expenses` | List / create expenses |
| GET/PUT/DELETE | `/api/expenses/<id>` | Get / update / delete expense |
| POST | `/api/expenses/receipt-scan` | OCR receipt upload |
| GET/POST | `/api/incomes` | List / create income |
| GET/PUT/DELETE | `/api/incomes/<id>` | Get / update / delete income |
| GET | `/api/analytics` | Analytics data |
| GET/POST | `/api/budgets` | List / create budgets |
| GET/PUT/DELETE | `/api/budgets/<id>` | Manage budget |
| GET/POST | `/api/goals` | List / create goals |
| POST | `/api/goals/<id>/contribute` | Add to goal |
| GET/POST | `/api/subscriptions` | List / create subscriptions |

### Statements, AI, Settings

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/statements/upload` | Upload bank statement |
| GET | `/api/statements/<year>/<month>` | Get statement |
| POST | `/api/statements/<id>/analyze` | AI analysis |
| POST | `/api/ai/chat` | AI Coach chat |
| GET | `/api/ai/budget-recommendations` | AI budget tips |
| GET | `/api/ai/goal-forecast/<id>` | AI goal forecast |
| GET | `/api/calendar/events` | Calendar events |
| GET | `/api/notifications` | Notifications list |
| PUT | `/api/settings/profile` | Update profile |
| GET | `/api/settings/export` | Export data as JSON |

---

## Frontend Overview

### Templates

| File | Used for |
|------|----------|
| `base.html` | Public pages shell |
| `app_base.html` | Authenticated app shell (sidebar + topbar) |
| `landing.html`, `login.html`, `signup.html` | Auth and marketing |
| `dashboard.html`, `expenses.html`, etc. | Feature pages |

### CSS (`static/css/`)

| File | Purpose |
|------|---------|
| `main.css` | Design tokens, theme variables |
| `app.css` | App layout (sidebar, cards) |
| `auth.css` | Login / signup pages |
| `landing.css` | Landing page |
| `animations.css` | Transitions and motion |

### JavaScript (`static/js/`)

| File | Purpose |
|------|---------|
| `theme.js` | Dark / light mode |
| `main.js` | Toasts, shared UI helpers |
| `app.js` | Notifications, profile menu |
| `auth.js` | Login, signup, OTP, Google |
| `animations.js` | Page animations |

Theme is stored in `localStorage` under key `expenseiq_theme`.

---

## Testing

### Smoke test (recommended)

```powershell
python run_smoke.py
```

Checks: auth config, signup/login API, dashboard access.

### End-to-end auth test

```powershell
python tools/e2e_test.py
```

---

## Push to GitHub

If you have not published the project yet:

### 1. Create a GitHub repository

1. Go to [github.com/new](https://github.com/new)
2. Name it `ExpenseIQ`
3. Do **not** add README or `.gitignore` (you already have them)
4. Click **Create repository**

### 2. Initialize and push (first time)

```powershell
cd "C:\Users\hp\OneDrive\Desktop\PROJECTS\ExpenseIQ"
git init
git add .
git commit -m "Initial commit: ExpenseIQ personal finance app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ExpenseIQ.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

### What gets ignored (`.gitignore`)

- `.env` (secrets — never commit)
- `.venv/`, `__pycache__/`
- `static/uploads/` (user files)
- `*.log`, `.local/`, `.agents/`

---

## Deploy Online (No Docker)

The simplest path is **Render** — free tier, connects to GitHub, no Docker needed.

### Step 1 — MongoDB Atlas (recommended for production)

1. Create a free cluster at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Copy your connection string
3. Keep it for Step 3

### Step 2 — Gemini API key (for AI features)

1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Create an API key

### Step 3 — Deploy on Render

1. Sign up at [render.com](https://render.com)
2. Click **New → Web Service**
3. Connect your GitHub account and select the `ExpenseIQ` repo
4. Render reads `render.yaml` automatically, or set manually:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `python app.py`
5. Add environment variables in the Render dashboard:

| Key | Value |
|-----|-------|
| `FLASK_ENV` | `production` |
| `FLASK_DEBUG` | `False` |
| `SECRET_KEY` | random 64-char hex string |
| `JWT_SECRET_KEY` | random 64-char hex string |
| `MONGO_URI` | your MongoDB Atlas URI |
| `GEMINI_API_KEY` | your Gemini key |
| `PORT` | `5000` |

6. Click **Deploy**

Your app will be live at `https://your-app-name.onrender.com`.

> **Note:** On Render free tier, the app may sleep after inactivity. First load can take 30–60 seconds.

### Alternative: Railway, PythonAnywhere, or VPS

Same idea: install Python, run `pip install -r requirements.txt`, set env vars, run `python app.py` or use the `Procfile`:

```
web: python app.py
```

---

## Optional: Docker

Docker is **not required**. Use it only if you already use containers.

```powershell
docker build -t expenseiq .
docker run -p 5000:5000 --env-file .env expenseiq
```

Then open http://localhost:5000.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Activate venv and run `pip install -r requirements.txt` |
| App crashes on Windows console | Fixed in `config/database.py` — use ASCII log messages |
| AI Coach says unavailable | Set `GEMINI_API_KEY` in `.env` |
| Google login not working | Set `GOOGLE_CLIENT_ID` in `.env` |
| Data lost after restart | Without MongoDB, data lives in `data/mockdb.json` — do not delete it |
| Port already in use | Change `PORT=5001` in `.env` |
| Email already registered (smoke test) | Normal if test user exists — login instead |

---

## Quick Command Reference

```powershell
# Activate environment
.venv\Scripts\activate

# Run app
python app.py

# Run tests
python run_smoke.py

# Generate secret key
python -c "import secrets; print(secrets.token_hex(32))"
```

---

**Author:** Heer Sagaria  
**License:** MIT — see [LICENSE](LICENSE)  
**Last updated:** June 2026
