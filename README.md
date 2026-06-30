# ExpenseIQ ??

A modern, AI-powered personal finance management application built with Flask and Google Gemini. Track expenses, manage budgets, analyze spending patterns, and get personalized financial coaching.

![Version](https://img.shields.io/badge/version-1.1.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Flask](https://img.shields.io/badge/flask-2.0+-orange)
![License](https://img.shields.io/badge/license-MIT-green)

## ?? Features

### Core Functionality
- **Expense Tracking**: Log and categorize expenses with real-time analytics
- **Budget Management**: Set budgets per category and monitor spending
- **Income Management**: Track multiple income sources
- **Bank Statement Import**: Upload and analyze bank statements (PDF/CSV) with password protection
- **Calendar View**: Visualize financial events across months and years
- **Subscription Tracking**: Monitor recurring payments and renewal alerts
- **Goals Tracking**: Set and monitor financial savings goals

### AI-Powered Features
- **AI Financial Coach**: Powered by Google Gemini for personalized financial advice
- **Smart Analysis**: AI-driven insights on spending patterns
- **Bank Statement Analysis**: Automatic transaction categorization and summary

### Analytics & Reports
- **Dashboard Analytics**: Real-time spending overview with charts
- **Monthly Reports**: Detailed expense breakdowns by category
- **Income vs Expense**: Comparative analysis and trend tracking

### Authentication
- **Modern Login/Signup**: Email/password authentication
- **Social Login**: Google OAuth integration
- **Secure Authentication**: JWT-based with bcrypt password hashing

## ??? Tech Stack

### Backend
- **Framework**: Flask (Python)
- **Authentication**: Flask-JWT-Extended
- **Database**: MongoDB
- **AI**: Google Generative AI (Gemini)
- **File Processing**: PyPDF2 for password-protected PDFs, CSV import

### Frontend
- **HTML5/CSS3**: Responsive design
- **JavaScript**: Vanilla JS
- **Bootstrap**: Grid system for layout

## ?? Prerequisites

- Python 3.8 or higher
- MongoDB instance (local or cloud)
- Google Generative AI API key

## ?? Installation

### 1. Clone the Repository
`ash
git clone https://github.com/heersagaria09/ExpenseIQ.git
cd ExpenseIQ
`

### 2. Create Virtual Environment
`ash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
`

### 3. Install Dependencies
`ash
pip install -r requirements.txt
`

### 4. Environment Configuration
Create a .env file in the root directory:

`env
# Flask
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# MongoDB
MONGO_URI=mongodb://localhost:27017/expenseiq
# Or for MongoDB Atlas:
# MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/expenseiq

# Google Gemini API
GEMINI_API_KEY=your-google-gemini-api-key

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here

# Server
PORT=5000
HOST=0.0.0.0
`

### 5. Run the Application
`ash
python app.py
`

The app will be available at http://localhost:5000

## ?? Project Structure

`
ExpenseIQ/
+-- app.py                 # Entry point
+-- app/                   # Main application package
¦   +-- config/            # Configuration
¦   +-- models/            # Database models
¦   +-- routes/            # API routes
¦   +-- services/          # Business logic
¦   +-- templates/         # HTML templates
¦   +-- static/            # CSS/JS assets
¦   +-- utils/             # Utilities
+-- data/                  # Local database
+-- requirements.txt       # Python dependencies
+-- .env.example           # Environment template
`

## ?? API Endpoints

### Authentication
`
POST   /api/auth/signup           - Register new user
POST   /api/auth/login            - User login
POST   /api/auth/logout           - User logout
POST   /api/auth/google           - Google OAuth login
`

### Expenses
`
GET    /api/expenses              - Get all expenses
POST   /api/expenses              - Add new expense
PUT    /api/expenses/<id>         - Update expense
DELETE /api/expenses/<id>         - Delete expense
`

### Income
`
GET    /api/income                - Get all income
POST   /api/income                - Add new income
PUT    /api/income/<id>           - Update income
DELETE /api/income/<id>           - Delete income
`

### Bank Statements
`
GET    /api/statements            - Get statements
POST   /api/statements/upload     - Upload statement (supports password-protected PDFs)
POST   /api/statements/<id>/analyze - AI analysis
DELETE /api/statements/<id>       - Delete statement
`

### AI Coach
`
POST   /api/ai/chat               - Chat with AI
`

### Settings
`
PUT    /api/settings/profile      - Update profile
`

## ?? Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt for secure password storage
- **Input Validation**: XSS and SQL injection prevention

## ?? License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ????? Author

- **Heer Sagaria** - Initial work and development

---

**Made with ?? by Heer Sagaria**

Last Updated: June 2026
