from datetime import datetime
from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from app.services.analytics_service import get_analytics_data
from app.models.notification import get_unread_count

analytics_bp = Blueprint('analytics', __name__)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated


@analytics_bp.route('/analytics')
@login_required
def index():
    user_id = session['user_id']
    unread = get_unread_count(user_id)
    now = datetime.utcnow()
    data = get_analytics_data(user_id, now.year, now.month)
    return render_template('analytics.html',
                           user_name=session.get('user_name', 'User'),
                           user_email=session.get('user_email', ''),
                           unread_count=unread,
                           data=data)


@analytics_bp.route('/api/analytics')
@login_required
def api_analytics():
    user_id = session['user_id']
    now = datetime.utcnow()
    year = int(request.args.get('year', now.year))
    month = int(request.args.get('month', now.month))
    data = get_analytics_data(user_id, year, month)
    for item in data.get('category_breakdown', []):
        item['_id'] = str(item.get('_id', ''))
    for item in data.get('source_breakdown', []):
        item['_id'] = str(item.get('_id', ''))
    return jsonify({'success': True, 'data': data})
