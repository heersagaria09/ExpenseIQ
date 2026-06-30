from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from app.services.gemini_service import analyze_finances, get_budget_recommendations, get_goal_forecast
from app.services.analytics_service import get_dashboard_data
from app.models.notification import get_unread_count

ai_bp = Blueprint('ai', __name__)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated


@ai_bp.route('/ai-coach')
@login_required
def index():
    user_id = session['user_id']
    unread = get_unread_count(user_id)
    return render_template('ai_coach.html',
                           user_name=session.get('user_name', 'User'),
                           user_email=session.get('user_email', ''),
                           unread_count=unread)


@ai_bp.route('/api/ai/chat', methods=['POST'])
@login_required
def chat():
    user_id = session['user_id']
    data = request.get_json()
    question = data.get('question', '').strip()
    if not question:
        return jsonify({'success': False, 'message': 'Question is required'}), 400
    if len(question) > 500:
        return jsonify({'success': False, 'message': 'Question too long (max 500 characters)'}), 400
    user_data = get_dashboard_data(user_id)
    cat_breakdown = user_data.get('category_breakdown', [])
    cat_str = '\n'.join([f"- {c['_id']}: ₹{c['total']:,.0f}" for c in cat_breakdown[:5]])
    user_data['category_breakdown'] = cat_str
    response, err = analyze_finances(user_data, question)
    if err:
        return jsonify({'success': False, 'message': f'AI unavailable: {err}'}), 503
    return jsonify({'success': True, 'data': {'response': response, 'question': question}})


@ai_bp.route('/api/ai/budget-recommendations', methods=['GET'])
@login_required
def budget_recs():
    user_id = session['user_id']
    from datetime import datetime
    from app.models.budget import get_budgets
    from app.models.expense import get_category_breakdown
    now = datetime.utcnow()
    budgets = get_budgets(user_id, now.year, now.month)
    cat_breakdown = get_category_breakdown(user_id, now.year, now.month)
    if not budgets and not cat_breakdown:
        return jsonify({'success': False, 'message': 'Add budgets and expenses to get recommendations'}), 400
    budget_str = [{'category': b['category'], 'budget': b['amount']} for b in budgets]
    expense_str = [{'category': c['_id'], 'spent': c['total']} for c in cat_breakdown]
    response, err = get_budget_recommendations(budget_str, expense_str)
    if err:
        return jsonify({'success': False, 'message': f'AI unavailable: {err}'}), 503
    return jsonify({'success': True, 'data': {'recommendations': response}})


@ai_bp.route('/api/ai/goal-forecast/<goal_id>', methods=['GET'])
@login_required
def goal_forecast(goal_id):
    user_id = session['user_id']
    from app.models.goal import get_goal_by_id
    goal = get_goal_by_id(goal_id, user_id)
    if not goal:
        return jsonify({'success': False, 'message': 'Goal not found'}), 404
    dashboard = get_dashboard_data(user_id)
    monthly_savings = dashboard.get('savings', 0)
    response, err = get_goal_forecast(goal, monthly_savings)
    if err:
        return jsonify({'success': False, 'message': f'AI unavailable: {err}'}), 503
    return jsonify({'success': True, 'data': {'forecast': response}})
