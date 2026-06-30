import os
from datetime import datetime
from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from app.models.expense import create_expense, get_expenses, get_expense_by_id, update_expense, delete_expense
from app.models.notification import get_unread_count
from app.utils.validators import validate_expense
from app.utils.constants import EXPENSE_CATEGORIES

expense_bp = Blueprint('expense', __name__)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated


@expense_bp.route('/expenses')
@login_required
def index():
    user_id = session['user_id']
    unread = get_unread_count(user_id)
    return render_template('expenses.html',
                           user_name=session.get('user_name', 'User'),
                           user_email=session.get('user_email', ''),
                           unread_count=unread,
                           categories=EXPENSE_CATEGORIES)


@expense_bp.route('/api/expenses', methods=['GET'])
@login_required
def list_expenses():
    try:
        user_id = session['user_id']
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        filters = {}
        if request.args.get('category'):
            filters['category'] = request.args['category']
        if request.args.get('search'):
            filters['search'] = request.args['search']
        if request.args.get('start_date') and request.args.get('end_date'):
            try:
                filters['start_date'] = datetime.strptime(request.args['start_date'], '%Y-%m-%d')
                filters['end_date'] = datetime.strptime(request.args['end_date'], '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            except ValueError:
                pass
        result = get_expenses(user_id, filters, page, per_page)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        print(f'Error in list_expenses: {e}')
        return jsonify({'success': False, 'message': 'Failed to load expenses', 'error': str(e)}), 500


@expense_bp.route('/api/expenses', methods=['POST'])
@login_required
def add_expense():
    user_id = session['user_id']
    data = request.get_json()
    errors = validate_expense(data)
    if errors:
        return jsonify({'success': False, 'message': errors[0]}), 400
    try:
        if data.get('date'):
            data['date'] = datetime.strptime(data['date'], '%Y-%m-%d')
        else:
            data['date'] = datetime.utcnow()
    except ValueError:
        data['date'] = datetime.utcnow()
    expense = create_expense(user_id, data)
    _check_budget_alert(user_id, data.get('category'))
    return jsonify({'success': True, 'message': 'Expense added successfully', 'data': expense}), 201


@expense_bp.route('/api/expenses/<expense_id>', methods=['PUT'])
@login_required
def edit_expense(expense_id):
    user_id = session['user_id']
    data = request.get_json()
    errors = validate_expense(data)
    if errors:
        return jsonify({'success': False, 'message': errors[0]}), 400
    try:
        if data.get('date'):
            data['date'] = datetime.strptime(data['date'], '%Y-%m-%d')
    except ValueError:
        pass
    if update_expense(expense_id, user_id, data):
        return jsonify({'success': True, 'message': 'Expense updated'})
    return jsonify({'success': False, 'message': 'Expense not found'}), 404


@expense_bp.route('/api/expenses/<expense_id>', methods=['DELETE'])
@login_required
def remove_expense(expense_id):
    user_id = session['user_id']
    if delete_expense(expense_id, user_id):
        return jsonify({'success': True, 'message': 'Expense deleted'})
    return jsonify({'success': False, 'message': 'Expense not found'}), 404


@expense_bp.route('/api/expenses/<expense_id>', methods=['GET'])
@login_required
def get_single(expense_id):
    user_id = session['user_id']
    expense = get_expense_by_id(expense_id, user_id)
    if expense:
        if isinstance(expense.get('date'), datetime):
            expense['date_input'] = expense['date'].strftime('%Y-%m-%d')
        return jsonify({'success': True, 'data': expense})
    return jsonify({'success': False, 'message': 'Not found'}), 404


@expense_bp.route('/api/expenses/receipt-scan', methods=['POST'])
@login_required
def receipt_scan():
    if 'receipt' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'}), 400
    file = request.files['receipt']
    if not file.filename:
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    allowed = {'png', 'jpg', 'jpeg', 'webp'}
    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in allowed:
        return jsonify({'success': False, 'message': 'Only image files allowed (PNG, JPG, JPEG)'}), 400
    upload_dir = os.path.join('static', 'uploads', 'receipts')
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"receipt_{session['user_id']}_{int(datetime.utcnow().timestamp())}.{ext}"
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)
    from app.services.ocr_service import process_receipt_image
    parsed, err = process_receipt_image(file_path)
    if err:
        return jsonify({'success': False, 'message': f'OCR failed: {err}'}), 500
    return jsonify({'success': True, 'data': parsed})


def _check_budget_alert(user_id, category):
    if not category:
        return
    try:
        from app.models.budget import get_budgets
        from app.models.expense import get_category_breakdown
        from app.models.notification import create_notification
        now = datetime.utcnow()
        budgets = get_budgets(user_id, now.year, now.month)
        cat_breakdown = get_category_breakdown(user_id, now.year, now.month)
        spent_map = {c['_id']: c['total'] for c in cat_breakdown}
        for b in budgets:
            if b['category'] == category:
                spent = spent_map.get(category, 0)
                pct = (spent / b['amount']) * 100 if b['amount'] > 0 else 0
                threshold = b.get('alert_threshold', 80)
                if pct >= threshold:
                    create_notification(user_id,
                        f'Budget Alert: {category}',
                        f'You have used {pct:.0f}% (₹{spent:,.0f}) of your ₹{b["amount"]:,.0f} {category} budget',
                        'budget_alert')
    except Exception:
        pass
