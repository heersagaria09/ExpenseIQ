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

- Python 3.8 or higher
- MongoDB instance (local or cloud)
- Google Generative AI API key

## 🚀 How to Run

1. Clone the repository:
`ash
git clone https://github.com/heersagaria09/ExpenseIQ.git
cd ExpenseIQ
`

2. Create virtual environment:
`ash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
`

3. Install dependencies:
`ash
pip install -r requirements.txt
`

4. Create .env file with your configuration:
`env
GEMINI_API_KEY=your-api-key
MONGO_URI=mongodb://localhost:27017/expenseiq
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
`

5. Run the application:
`ash
python app.py
`

Open http://localhost:5000 in your browser.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Heer Sagaria**

---

**Made with ❤️ by Heer Sagaria**
