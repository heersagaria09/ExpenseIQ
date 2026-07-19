# ExpenseIQ 💰

A modern, AI-powered personal finance management application built with Flask and Google Gemini. Track expenses, manage budgets, analyze spending patterns, and get personalized financial coaching.

![Version](https://img.shields.io/badge/version-1.1.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Flask](https://img.shields.io/badge/flask-2.0+-orange)
![License](https://img.shields.io/badge/license-MIT-green)

## 🎯 Features

- **Expense Tracking**: Log and categorize expenses with real-time analytics
- **Budget Management**: Set budgets per category and monitor spending
- **Income Management**: Track multiple income sources
- **Bank Statement Import**: Upload and analyze bank statements (PDF/CSV) with password protection
- **Calendar View**: Visualize financial events across months and years
- **Subscription Tracking**: Monitor recurring payments and renewal alerts
- **Goals Tracking**: Set and monitor financial savings goals
- **AI Financial Coach**: Powered by Google Gemini for personalized financial advice
- **Smart Analysis**: AI-driven insights on spending patterns
- **Dashboard Analytics**: Real-time spending overview with charts

## 🛠️ Tech Stack

- **Backend**: Flask (Python), MongoDB, Google Gemini AI
- **Frontend**: HTML5/CSS3, JavaScript, Bootstrap
- **Authentication**: JWT, Google OAuth
- **File Processing**: PyPDF2 for password-protected PDFs

## 📋 Prerequisites

- Python 3.8 or higher (3.10–3.12 recommended)
- Google Generative AI API key (optional — only needed for AI features)
- MongoDB instance (optional — the app falls back to a local file-backed database if no `MONGO_URI` is set)

## 🚀 How to Run

1. Clone the repository:

```bash
git clone https://github.com/heersagaria09/ExpenseIQ.git
cd ExpenseIQ
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv

# Windows (PowerShell / VS Code terminal)
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create your `.env` file (optional but recommended). Copy the example and edit the values:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

The app runs without a `.env` using sensible defaults and a local database. Set these keys to enable full functionality:

```env
GEMINI_API_KEY=your-google-gemini-api-key
MONGO_URI=mongodb://localhost:27017/expenseiq
SECRET_KEY=change-this-in-production
JWT_SECRET_KEY=change-this-in-production
```

5. Run the application:

```bash
python app.py
```

Open http://localhost:5000 in your browser.

## 🩺 Troubleshooting (VS Code / fresh download)

- **Select the right interpreter**: after creating `.venv`, in VS Code run `Python: Select Interpreter` and choose the `.venv` interpreter so the integrated terminal and IntelliSense use it.
- **`pip install` succeeds but the app can't find packages**: make sure the virtual environment is activated (your terminal prompt should show `(.venv)`).
- **No MongoDB installed**: that's fine — leave `MONGO_URI` empty and the app uses a local file-backed database (`app/data/mockdb.json`).
- **AI features disabled**: set `GEMINI_API_KEY` in `.env`. Without it the app still runs; only AI-powered features are unavailable.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Heer Sagaria**

---

**Made with ❤️ by Heer Sagaria**
