from flask import Blueprint, render_template, session, redirect, url_for, jsonify
from app.services.analytics_service import get_dashboard_data
from app.models.notification import get_unread_count

dashboard_bp = Blueprint('dashboard', __name__)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated


@dashboard_bp.route('/dashboard')
@login_required
def index():
    user_id = session['user_id']
    data = get_dashboard_data(user_id)
    unread = get_unread_count(user_id)
    return render_template('dashboard.html',
                           user_name=session.get('user_name', 'User'),
                           user_email=session.get('user_email', ''),
                           unread_count=unread,
                           data=data)


@dashboard_bp.route('/api/dashboard/data')
@login_required
def api_data():
    data = get_dashboard_data(session['user_id'])
    return jsonify({'success': True, 'data': data})
