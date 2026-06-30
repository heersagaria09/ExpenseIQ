from datetime import datetime
from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from app.models.income import create_income, get_incomes, get_income_by_id, update_income, delete_income
from app.models.notification import get_unread_count
from app.utils.validators import validate_income
from app.utils.constants import INCOME_SOURCES

income_bp = Blueprint('income', __name__)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated


@income_bp.route('/income')
@login_required
def index():
    user_id = session['user_id']
    unread = get_unread_count(user_id)
    return render_template('income.html',
                           user_name=session.get('user_name', 'User'),
                           user_email=session.get('user_email', ''),
                           unread_count=unread,
                           sources=INCOME_SOURCES)


@income_bp.route('/api/incomes', methods=['GET'])
@login_required
def list_incomes():
    user_id = session['user_id']
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    filters = {}
    if request.args.get('source'):
        filters['source'] = request.args['source']
    if request.args.get('search'):
        filters['search'] = request.args['search']
    result = get_incomes(user_id, filters, page, per_page)
    return jsonify({'success': True, 'data': result})


@income_bp.route('/api/incomes', methods=['POST'])
@login_required
def add_income():
    user_id = session['user_id']
    data = request.get_json()
    errors = validate_income(data)
    if errors:
        return jsonify({'success': False, 'message': errors[0]}), 400
    try:
        if data.get('date'):
            data['date'] = datetime.strptime(data['date'], '%Y-%m-%d')
        else:
            data['date'] = datetime.utcnow()
    except ValueError:
        data['date'] = datetime.utcnow()
    income = create_income(user_id, data)
    return jsonify({'success': True, 'message': 'Income added successfully', 'data': income}), 201


@income_bp.route('/api/incomes/<income_id>', methods=['PUT'])
@login_required
def edit_income(income_id):
    user_id = session['user_id']
    data = request.get_json()
    errors = validate_income(data)
    if errors:
        return jsonify({'success': False, 'message': errors[0]}), 400
    try:
        if data.get('date'):
            data['date'] = datetime.strptime(data['date'], '%Y-%m-%d')
    except ValueError:
        pass
    if update_income(income_id, user_id, data):
        return jsonify({'success': True, 'message': 'Income updated'})
    return jsonify({'success': False, 'message': 'Income not found'}), 404


@income_bp.route('/api/incomes/<income_id>', methods=['DELETE'])
@login_required
def remove_income(income_id):
    user_id = session['user_id']
    if delete_income(income_id, user_id):
        return jsonify({'success': True, 'message': 'Income deleted'})
    return jsonify({'success': False, 'message': 'Income not found'}), 404


@income_bp.route('/api/incomes/<income_id>', methods=['GET'])
@login_required
def get_single(income_id):
    user_id = session['user_id']
    income = get_income_by_id(income_id, user_id)
    if income:
        if isinstance(income.get('date'), datetime):
            income['date_input'] = income['date'].strftime('%Y-%m-%d')
        return jsonify({'success': True, 'data': income})
    return jsonify({'success': False, 'message': 'Not found'}), 404
