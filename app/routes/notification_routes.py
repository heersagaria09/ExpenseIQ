from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from app.models.notification import get_notifications, mark_read, mark_all_read, delete_notification, get_unread_count

notification_bp = Blueprint('notification', __name__)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated


@notification_bp.route('/notifications')
@login_required
def index():
    user_id = session['user_id']
    data = get_notifications(user_id)
    return render_template('notifications.html',
                           user_name=session.get('user_name', 'User'),
                           user_email=session.get('user_email', ''),
                           unread_count=data['unread'],
                           notifications=data['items'],
                           total=data['total'])


@notification_bp.route('/api/notifications')
@login_required
def list_notifs():
    user_id = session['user_id']
    unread_only = request.args.get('unread_only') == 'true'
    page = int(request.args.get('page', 1))
    data = get_notifications(user_id, unread_only, page)
    return jsonify({'success': True, 'data': data})


@notification_bp.route('/api/notifications/<notif_id>/read', methods=['POST'])
@login_required
def read_notif(notif_id):
    mark_read(notif_id, session['user_id'])
    return jsonify({'success': True})


@notification_bp.route('/api/notifications/read-all', methods=['POST'])
@login_required
def read_all():
    mark_all_read(session['user_id'])
    return jsonify({'success': True, 'message': 'All notifications marked as read'})


@notification_bp.route('/api/notifications/<notif_id>', methods=['DELETE'])
@login_required
def remove_notif(notif_id):
    delete_notification(notif_id, session['user_id'])
    return jsonify({'success': True})


@notification_bp.route('/api/notifications/count')
@login_required
def notif_count():
    count = get_unread_count(session['user_id'])
    return jsonify({'success': True, 'count': count})
