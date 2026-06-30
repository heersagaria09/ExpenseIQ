from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from app.models.user import find_user_by_id, update_user
from app.models.notification import get_unread_count

settings_bp = Blueprint('settings', __name__)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated


@settings_bp.route('/settings')
@login_required
def index():
    user_id = session['user_id']
    user = find_user_by_id(user_id)
    unread = get_unread_count(user_id)
    if user:
        user.pop('password_hash', None)
    return render_template('settings.html',
                           user_name=session.get('user_name', 'User'),
                           user_email=session.get('user_email', ''),
                           unread_count=unread,
                           user=user)


@settings_bp.route('/api/settings/profile', methods=['PUT'])
@login_required
def update_profile():
    user_id = session['user_id']
    data = request.get_json()
    allowed = ['full_name', 'mobile', 'avatar', 'theme']
    update_data = {k: v for k, v in data.items() if k in allowed}
    if not update_data:
        return jsonify({'success': False, 'message': 'No valid fields to update'}), 400
    update_user(user_id, update_data)
    if 'full_name' in update_data:
        session['user_name'] = update_data['full_name']
    return jsonify({'success': True, 'message': 'Profile updated'})


@settings_bp.route('/api/settings/theme', methods=['POST'])
@login_required
def set_theme():
    user_id = session['user_id']
    data = request.get_json()
    theme = data.get('theme', 'dark')
    if theme not in ['dark', 'light']:
        return jsonify({'success': False, 'message': 'Invalid theme'}), 400
    update_user(user_id, {'theme': theme})
    return jsonify({'success': True, 'message': f'Theme set to {theme}'})


@settings_bp.route('/api/settings/export', methods=['GET'])
@login_required
def export_data():
    user_id = session['user_id']
    from app.models.expense import get_expenses
    from app.models.income import get_incomes
    expenses = get_expenses(user_id, per_page=1000)
    incomes = get_incomes(user_id, per_page=1000)
    data = {
        'expenses': expenses['items'],
        'incomes': incomes['items'],
        'exported_at': __import__('datetime').datetime.utcnow().isoformat()
    }
    try:
        import json
        from flask import Response
        json_str = json.dumps(data, default=str, indent=2)
        return Response(json_str, mimetype='application/json',
                        headers={'Content-Disposition': 'attachment; filename=expenseiq_data.json'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
