import os
import google
from google import genai
from datetime import datetime


def get_gemini_model():
    api_key = os.environ.get('GEMINI_API_KEY', '')
    if not api_key:
        return None
    client = genai.Client(api_key=api_key)
    return client


def analyze_finances(user_data, question):
    client = get_gemini_model()
    if not client:
        return None, 'Gemini API key not configured'
    try:
        now = datetime.utcnow()
        context = f"""
You are ExpenseIQ's AI Financial Coach for an Indian user. Today is {now.strftime('%B %d, %Y')}.
Currency: Indian Rupees (₹ INR)

User's Financial Data:
- Monthly Income: ₹{user_data.get('monthly_income', 0):,.2f}
- Monthly Expenses: ₹{user_data.get('monthly_expenses', 0):,.2f}
- Monthly Savings: ₹{user_data.get('savings', 0):,.2f}
- Total Balance: ₹{user_data.get('total_balance', 0):,.2f}
- Top Expense Category: {user_data.get('top_category', 'N/A')}
- Active Budgets: {user_data.get('budget_count', 0)}
- Active Goals: {user_data.get('goal_count', 0)}
- Monthly Subscriptions Cost: ₹{user_data.get('subscription_cost', 0):,.2f}

Recent expense categories breakdown:
{user_data.get('category_breakdown', 'No data available')}

User Question: {question}

Provide specific, actionable financial advice based on the actual data above. 
Use ₹ (Indian Rupee) for all amounts. Be concise and practical. 
Do not make up data that isn't provided. Focus on real insights from the numbers shown.
"""
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=context
        )
        return response.text, None
    except Exception as e:
        return None, str(e)


def analyze_bank_statement(statement_text, month_name):
    client = get_gemini_model()
    if not client:
        return None, 'Gemini API key not configured'
    try:
        prompt = f"""
Analyze this bank statement for {month_name} and provide:
1. Total Credits (Income)
2. Total Debits (Expenses)  
3. Top 5 spending categories
4. Key observations
5. Money-saving recommendations

Statement content:
{statement_text[:4000]}

Use ₹ (Indian Rupees). Be specific and data-driven.
"""
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        return response.text, None
    except Exception as e:
        return None, str(e)


def get_budget_recommendations(budget_data, expense_data):
    client = get_gemini_model()
    if not client:
        return None, 'Gemini API key not configured'
    try:
        prompt = f"""
As an Indian personal finance advisor, analyze these budgets and expenses in ₹ INR:

Budgets: {budget_data}
Actual Expenses: {expense_data}

Provide 3 specific budget recommendations to improve financial health.
Focus on overspending areas and optimization opportunities.
Keep it concise and actionable.
"""
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        return response.text, None
    except Exception as e:
        return None, str(e)


def get_goal_forecast(goal_data, monthly_savings):
    client = get_gemini_model()
    if not client:
        return None, 'Gemini API key not configured'
    try:
        prompt = f"""
Help an Indian user achieve their financial goal:

Goal: {goal_data.get('title')}
Target Amount: ₹{goal_data.get('target_amount', 0):,.2f}
Current Savings: ₹{goal_data.get('current_amount', 0):,.2f}
Remaining: ₹{goal_data.get('target_amount', 0) - goal_data.get('current_amount', 0):,.2f}
Monthly Savings Available: ₹{monthly_savings:,.2f}
Target Date: {goal_data.get('target_date', 'Not set')}

Provide a realistic achievement timeline and 2-3 tips to reach this goal faster.
"""
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        return response.text, None
    except Exception as e:
        return None, str(e)
