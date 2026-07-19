# ExpenseIQ 💰

A modern, AI-powered personal finance management application built with Flask and Google Gemini. Track expenses, manage budgets, analyze spending patterns, and get personalized financial coaching.

![Version](https://img.shields.io/badge/version-1.1.0-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.0+-000000?style=for-the-badge&logo=flask&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

## 🎯 Features

- 🧾 **Expense Tracking**: Log and categorize expenses with real-time analytics
- 💵 **Budget Management**: Set budgets per category and monitor spending
- 💰 **Income Management**: Track multiple income sources
- 🏦 **Bank Statement Import**: Upload and analyze bank statements (PDF/CSV) with password protection
- 📅 **Calendar View**: Visualize financial events across months and years
- 🔁 **Subscription Tracking**: Monitor recurring payments and renewal alerts
- 🎯 **Goals Tracking**: Set and monitor financial savings goals
- 🤖 **AI Financial Coach**: Powered by Google Gemini for personalized financial advice
- 🧠 **Smart Analysis**: AI-driven insights on spending patterns
- 📊 **Dashboard Analytics**: Real-time spending overview with charts

## 🛠️ Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=flat-square&logo=mongodb&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=flat-square&logo=googlegemini&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?style=flat-square&logo=bootstrap&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=flat-square&logo=jsonwebtokens&logoColor=white)

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

```bash
git clone https://github.com/heersagaria09/ExpenseIQ.git
cd ExpenseIQ
```

2. Create virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create .env file with your configuration:

```env
GEMINI_API_KEY=your-api-key
MONGO_URI=mongodb://localhost:27017/expenseiq
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

5. Run the application:

```bash
python app.py
```

Open http://localhost:5000 in your browser.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Heer Sagaria**

---

**Made with ❤️ by Heer Sagaria**
