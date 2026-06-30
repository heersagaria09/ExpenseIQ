# ExpenseIQ 💰

A modern, AI-powered personal finance management application built with Flask and Google Gemini. Track expenses, manage budgets, analyze spending patterns, and get personalized financial coaching.

![Version](https://img.shields.io/badge/version-1.1.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Flask](https://img.shields.io/badge/flask-2.0+-orange)
![License](https://img.shields.io/badge/license-MIT-green)

## 🎯 Features

### Core Functionality
- **Expense Tracking**: Log and categorize expenses with real-time analytics
- **Budget Management**: Set budgets per category and monitor spending
- **Income Management**: Track multiple income sources
- **Bank Statement Import**: Upload and analyze bank statements (PDF/CSV)
- **Calendar View**: Visualize financial events across months and years
- **Subscription Tracking**: Monitor recurring payments and renewal alerts
- **Goals Tracking**: Set and monitor financial savings goals

### AI-Powered Features
- **AI Financial Coach**: Powered by Google Gemini for personalized financial advice
- **Smart Analysis**: AI-driven insights on spending patterns
- **Bank Statement Analysis**: Automatic transaction categorization and summary
- **Predictive Insights**: Financial health scoring and recommendations

### Analytics & Reports
- **Dashboard Analytics**: Real-time spending overview with charts
- **Monthly Reports**: Detailed expense breakdowns by category
- **Year Overview**: Mini-calendar showing spending distribution
- **Income vs Expense**: Comparative analysis and trend tracking

### User Experience
- **Premium Fintech Design**: Modern, clean UI inspired by Stripe, Linear, Notion
- **Dark/Light Mode**: Instant theme switching with no white flashes
- **Responsive Design**: Optimized for desktop, tablet, and mobile (320px-1920px)
- **Smooth Animations**: Cubic-bezier transitions for all interactions
- **Accessibility**: Focus states, keyboard navigation, screen reader support

### Authentication
- **Modern Login/Signup**: Horizontal centered card layout with social auth
- **Password Strength**: Real-time strength indicator with color-coded feedback
- **Social Login**: Google, Apple, and Mobile OTP authentication options
- **Secure Authentication**: JWT-based with bcrypt password hashing

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask (Python)
- **Authentication**: Flask-JWT-Extended
- **Database**: MongoDB
- **AI**: Google Generative AI (Gemini)
- **File Processing**: PDF parsing, CSV import

### Frontend
- **HTML5/CSS3**: Responsive design
- **JavaScript**: Vanilla JS with smooth animations
- **Icons**: SVG-based iconography
- **Animations**: CSS transitions with cubic-bezier easing
- **Bootstrap**: Grid system for layout

### Key Libraries
```
Flask==2.3.0
Flask-JWT-Extended==4.4.0
Flask-CORS==4.0.0
python-dotenv==1.0.0
google-generativeai==0.3.0
pymongo==4.5.0
```

## 📋 Prerequisites

- Python 3.8 or higher
- MongoDB instance (local or cloud)
- Google Generative AI API key
- Modern web browser

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/heersagaria09/ExpenseIQ.git
cd ExpenseIQ
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory:

```env
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

# Server
PORT=5000
HOST=0.0.0.0
```

### 5. Run the Application
```bash
python app.py
```

The app will be available at `http://localhost:5000`

## 📁 Project Structure

```
ExpenseIQ/
├── app.py                 # Entry point — Flask app factory
├── app/                   # Main application package
│   ├── __init__.py        # Flask app factory (create_app)
│   ├── config/
│   │   └── settings.py    # Configuration management
│   ├── models/
│   │   ├── user.py        # User model
│   │   ├── expense.py     # Expense model
│   │   ├── income.py      # Income model
│   │   └── bank_statement.py # Bank statement model
│   ├── routes/
│   │   ├── auth_routes.py # Authentication endpoints
│   │   ├── expense_routes.py # Expense management
│   │   ├── calendar_routes.py # Calendar functionality
│   │   ├── settings_routes.py # User settings
│   │   └── ai_routes.py   # AI coach endpoints
│   ├── services/
│   │   ├── gemini_service.py # Google Gemini integration
│   │   ├── ocr_service.py # OCR for receipts
│   │   └── statement_parser.py # Bank statement parsing
│   ├── templates/
│   │   ├── base.html      # Base template
│   │   ├── dashboard.html # Dashboard page
│   │   ├── expenses.html  # Expenses page
│   │   ├── calendar.html  # Calendar page
│   │   ├── ai_coach.html  # AI coach page
│   │   ├── settings.html  # Settings page
│   │   └── ...
│   ├── static/
│   │   ├── css/           # Stylesheets
│   │   └── js/            # JavaScript files
│   └── utils/
│       ├── validators.py # Input validation
│       └── helpers.py     # Utility functions
├── data/
│   └── mockdb.json        # Local dev database
├── tools/                 # Dev utilities
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
└── DOCUMENTATION.md       # Full project documentation
```

## 🎨 Key Pages & Features

### Dashboard
- Real-time spending overview
- Monthly expense breakdown
- Budget status indicators
- Quick action buttons

### Calendar
- Monthly/yearly calendar view
- Visual expense indicators
- Transaction details in side panel
- Mini-calendar year overview

### Expenses
- Searchable expense table
- Category filtering
- Date range filtering
- Add/edit/delete operations
- Receipt scanner integration

### Bank Statements
- PDF/CSV upload
- AI-powered analysis
- Transaction extraction
- Summary statistics

### AI Coach
- Chat interface with Gemini AI
- Real-time financial analysis
- Quick prompt suggestions
- Message history

### Settings
- Profile management
- Security settings
- Notification preferences
- Theme selection (dark/light)
- Privacy controls
- Data export

## 🔐 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt for secure password storage
- **CORS Protection**: Cross-origin request handling
- **Data Encryption**: AES-256 for sensitive data
- **Input Validation**: XSS and SQL injection prevention
- **Rate Limiting**: API rate limiting (configurable)

## 🎯 API Endpoints

### Authentication
```
POST   /api/auth/signup           - Register new user
POST   /api/auth/login            - User login
POST   /api/auth/logout           - User logout
POST   /api/auth/refresh          - Refresh JWT token
POST   /api/auth/change-password  - Change password
```

### Expenses
```
GET    /api/expenses              - Get all expenses
POST   /api/expenses              - Add new expense
PUT    /api/expenses/<id>         - Update expense
DELETE /api/expenses/<id>         - Delete expense
GET    /api/expenses/analytics    - Get analytics
```

### Calendar
```
GET    /calendar                  - Calendar page
GET    /api/calendar/<year>/<month> - Calendar data
```

### Bank Statements
```
GET    /api/statements            - Get statements
POST   /api/statements/upload     - Upload statement
POST   /api/statements/<id>/analyze - AI analysis
DELETE /api/statements/<id>       - Delete statement
```

### AI Coach
```
POST   /api/ai/chat               - Chat with AI
GET    /api/ai/history            - Chat history
```

### Settings
```
PUT    /api/settings/profile      - Update profile
GET    /api/settings/export       - Export data
```

## 🎨 UI/UX Highlights

- **Premium Fintech Design**: Modern, clean UI inspired by Stripe, Linear, Notion, Vercel, and CRED
- **Smooth Animations**: Cubic-bezier transitions for all interactions
- **Responsive Design**: Mobile-first approach with comprehensive breakpoints (320px-1920px)
- **Dark Mode**: Comprehensive dark theme with CSS variables and instant switching
- **Accessibility**: Semantic HTML, ARIA labels, focus states, keyboard navigation
- **Loading States**: Visual feedback with spinners and progress indicators
- **Toast Notifications**: User-friendly success/error messages
- **Anti-Flash CSS**: Instant theme loading prevents white flashes on navigation
- **Horizontal Auth Layout**: Centered card design with two-column form grids
- **Gradient CTA Buttons**: Emerald green gradients with glow effects
- **Smooth Underline Effects**: Navigation links with animated underlines
- **Compact Form Design**: Optimized spacing for better UX

## 📊 Recent Updates

### Version 1.1.0 - June 2026
- ✅ Redesigned authentication pages with horizontal centered card layout
- ✅ Implemented premium fintech navbar with transparent background
- ✅ Added gradient CTA buttons with glow effects
- ✅ Optimized signup layout for compact form display
- ✅ Enhanced dark/light mode with instant theme switching
- ✅ Added smooth underline hover effects on navigation links
- ✅ Improved accessibility with focus states and keyboard navigation
- ✅ Fixed white flash issues on page navigation and refresh
- ✅ Added comprehensive responsive design for all breakpoints

### Version 1.0.0 - Previous Release
- ✅ Fixed calendar current date visibility (white text on green circle)
- ✅ Added smooth animations for calendar month expansion/collapse
- ✅ Implemented fade transitions for settings section switching
- ✅ Added smooth message animations in AI Coach
- ✅ Removed duplicate date filter box on expenses page
- ✅ Enhanced UI/UX across all pages

## 🐛 Known Issues & Limitations

- OCR accuracy depends on receipt image quality
- Gemini API requires internet connection
- Bank statement parsing supports common formats (extending support in progress)
- Mobile responsiveness optimized for screens 320px and above

## 🚀 Deployment

### Heroku Deployment

1. **Install Heroku CLI**
```bash
# Windows
choco install heroku-cli

# macOS
brew tap heroku/brew && brew install heroku
```

2. **Login to Heroku**
```bash
heroku login
```

3. **Create Procfile**
```
web: gunicorn app:app
```

4. **Create requirements.txt**
```bash
pip freeze > requirements.txt
```

5. **Deploy**
```bash
heroku create your-app-name
git push heroku main
heroku config:set MONGO_URI=your-mongodb-uri
heroku config:set GEMINI_API_KEY=your-api-key
heroku open
```

### Docker Deployment

1. **Create Dockerfile**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

2. **Build and Run**
```bash
docker build -t expenseiq .
docker run -p 5000:5000 --env-file .env expenseiq
```

### AWS/GCP Deployment
- Use managed database services (AWS RDS, Cloud SQL)
- Deploy app with Elastic Beanstalk or App Engine
- Use Cloud Storage for file uploads
- Configure environment variables in deployment platform

## 📚 Documentation

Full project documentation: **[DOCUMENTATION.md](DOCUMENTATION.md)**

Covers local setup, environment variables, API reference, GitHub push, and Render deployment (no Docker required).

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure:
- Code follows PEP 8 style guide
- Add tests for new features
- Update documentation
- Test on multiple browsers

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Authors

- **Heer Sagaria** - Initial work and development

## 🙏 Acknowledgments

- Google Generative AI (Gemini) for AI capabilities
- Flask and Python community
- Bootstrap for responsive design
- All contributors and testers

## 📞 Support

For issues, questions, or suggestions:
- **GitHub Issues**: [Create an issue](https://github.com/heersagaria09/ExpenseIQ/issues)
- **Email**: support@expenseiq.com
- **Discord**: [Join our community](https://discord.gg/expenseiq)

## 🗺️ Roadmap

### Q2 2026 (Current Focus)
- [x] Authentication page redesign with horizontal layout
- [x] Premium fintech navbar implementation
- [x] Dark/light mode optimization
- [x] Accessibility enhancements
- [x] Responsive design improvements
- [ ] Mobile app (React Native)
- [ ] Investment tracking module
- [ ] Crypto wallet integration
- [ ] Advanced reporting dashboard

### Q3 2026
- [ ] Multi-currency support for international users
- [ ] Collaborative budgets for families/teams
- [ ] Financial advisor matching service
- [ ] Predictive spending forecasts using ML
- [ ] Receipt scanning with OCR
- [ ] Bill splitting functionality
- [ ] Recurring transaction automation
- [ ] Enhanced security with 2FA

### Q4 2026
- [ ] Business expense management
- [ ] Team analytics and reporting
- [ ] Integration with banking APIs
- [ ] Advanced AI insights and recommendations
- [ ] Tax preparation features
- [ ] Export to accounting software (QuickBooks, Xero)
- [ ] Offline mode with sync capability
- [ ] Performance optimization for large datasets

### 2027 Vision
- [ ] Peer comparison (anonymized spending benchmarks)
- [ ] Financial health scoring system
- [ ] Educational content on financial literacy
- [ ] Community features for financial tips
- [ ] White-label options for businesses
- [ ] API for third-party integrations
- [ ] Real-time data synchronization
- [ ] Enterprise features with role-based access

## 📊 Project Status

- **Development**: Active ✅
- **Testing**: In Progress 🔄
- **Documentation**: Complete ✅
- **Deployment**: Not Deployed ❌ (Code available on GitHub)
- **Ready for Production**: Soon 🚀

---

**Made with ❤️ by Heer Sagaria**

Last Updated: June 2026
