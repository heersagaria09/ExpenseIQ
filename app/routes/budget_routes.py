from datetime import datetime
from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from app.models.budget import create_budget, get_budgets, get_budget_by_id, update_budget, delete_budget
from app.models.expense import get_category_breakdown
from app.models.notification import get_unread_count
from app.utils.validators import validate_budget
from app.utils.constants import EXPENSE_CATEGORIES

budget_bp = Blueprint('budget', __name__)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated


@budget_bp.route('/budgets')
@login_required
def index():
    user_id = session['user_id']
    now = datetime.utcnow()
    unread = get_unread_count(user_id)
    budgets = get_budgets(user_id, now.year, now.month)
    cat_breakdown = get_category_breakdown(user_id, now.year, now.month)
    spent_map = {c['_id']: c['total'] for c in cat_breakdown}
    for b in budgets:
        b['spent'] = spent_map.get(b['category'], 0)
        b['remaining'] = max(0, b['amount'] - b['spent'])
        b['pct'] = round((b['spent'] / b['amount']) * 100, 1) if b['amount'] > 0 else 0
        b['over_budget'] = b['spent'] > b['amount']
    total_budget = sum(b['amount'] for b in budgets)
    total_spent = sum(b['spent'] for b in budgets)
    return render_template('budgets.html',
                           user_name=session.get('user_name', 'User'),
                           user_email=session.get('user_email', ''),
                           unread_count=unread,
                           budgets=budgets,
                           categories=EXPENSE_CATEGORIES,
                           total_budget=total_budget,
                           total_spent=total_spent,
                           current_month=now.strftime('%B %Y'))


@budget_bp.route('/api/budgets', methods=['GET'])
@login_required
def list_budgets():
    user_id = session['user_id']
    now = datetime.utcnow()
    year = int(request.args.get('year', now.year))
    month = int(request.args.get('month', now.month))
    budgets = get_budgets(user_id, year, month)
    cat_breakdown = get_category_breakdown(user_id, year, month)
    spent_map = {c['_id']: c['total'] for c in cat_breakdown}
    for b in budgets:
        b['spent'] = spent_map.get(b['category'], 0)
        b['remaining'] = max(0, b['amount'] - b['spent'])
        b['pct'] = round((b['spent'] / b['amount']) * 100, 1) if b['amount'] > 0 else 0
        b['over_budget'] = b['spent'] > b['amount']
    return jsonify({'success': True, 'data': budgets})


@budget_bp.route('/api/budgets', methods=['POST'])
@login_required
def add_budget():
    user_id = session['user_id']
    data = request.get_json()
    errors = validate_budget(data)
    if errors:
        return jsonify({'success': False, 'message': errors[0]}), 400
    budget = create_budget(user_id, data)
    return jsonify({'success': True, 'message': 'Budget saved', 'data': budget}), 201


@budget_bp.route('/api/budgets/<budget_id>', methods=['PUT'])
@login_required
def edit_budget(budget_id):
    user_id = session['user_id']
    data = request.get_json()
    if update_budget(budget_id, user_id, data):
        return jsonify({'success': True, 'message': 'Budget updated'})
    return jsonify({'success': False, 'message': 'Budget not found'}), 404


@budget_bp.route('/api/budgets/<budget_id>', methods=['DELETE'])
@login_required
def remove_budget(budget_id):
    user_id = session['user_id']
    if delete_budget(budget_id, user_id):
        return jsonify({'success': True, 'message': 'Budget deleted'})
    return jsonify({'success': False, 'message': 'Budget not found'}), 404
