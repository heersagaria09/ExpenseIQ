from datetime import datetime
from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from app.models.subscription import (create_subscription, get_subscriptions, get_subscription_by_id,
                                   update_subscription, delete_subscription, get_monthly_cost)
from app.models.notification import get_unread_count
from app.utils.constants import SUBSCRIPTION_CATEGORIES, BILLING_CYCLES

subscription_bp = Blueprint('subscription', __name__)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated


@subscription_bp.route('/subscriptions')
@login_required
def index():
    user_id = session['user_id']
    unread = get_unread_count(user_id)
    subs = get_subscriptions(user_id)
    monthly_cost = get_monthly_cost(user_id)
    yearly_cost = monthly_cost * 12
    active_count = sum(1 for s in subs if s.get('is_active'))
    renewal_soon = [s for s in subs if s.get('renewal_soon')]
    return render_template('subscriptions.html',
                           user_name=session.get('user_name', 'User'),
                           user_email=session.get('user_email', ''),
                           unread_count=unread,
                           subscriptions=subs,
                           monthly_cost=monthly_cost,
                           yearly_cost=yearly_cost,
                           active_count=active_count,
                           renewal_soon=renewal_soon,
                           categories=SUBSCRIPTION_CATEGORIES,
                           billing_cycles=BILLING_CYCLES)


@subscription_bp.route('/api/subscriptions', methods=['GET'])
@login_required
def list_subs():
    user_id = session['user_id']
    subs = get_subscriptions(user_id)
    for s in subs:
        if isinstance(s.get('next_renewal'), datetime):
            s['next_renewal'] = s['next_renewal'].isoformat()
    return jsonify({'success': True, 'data': subs})


@subscription_bp.route('/api/subscriptions', methods=['POST'])
@login_required
def add_sub():
    user_id = session['user_id']
    data = request.get_json()
    if not data.get('name'):
        return jsonify({'success': False, 'message': 'Subscription name required'}), 400
    try:
        data['amount'] = float(data.get('amount', 0))
        if data['amount'] <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Valid amount required'}), 400
    if data.get('next_renewal'):
        try:
            data['next_renewal'] = datetime.strptime(data['next_renewal'], '%Y-%m-%d')
        except ValueError:
            data['next_renewal'] = None
    sub = create_subscription(user_id, data)
    return jsonify({'success': True, 'message': 'Subscription added', 'data': sub}), 201


@subscription_bp.route('/api/subscriptions/<sub_id>', methods=['PUT'])
@login_required
def edit_sub(sub_id):
    user_id = session['user_id']
    data = request.get_json()
    if data.get('next_renewal'):
        try:
            data['next_renewal'] = datetime.strptime(data['next_renewal'], '%Y-%m-%d')
        except ValueError:
            pass
    if update_subscription(sub_id, user_id, data):
        return jsonify({'success': True, 'message': 'Subscription updated'})
    return jsonify({'success': False, 'message': 'Not found'}), 404


@subscription_bp.route('/api/subscriptions/<sub_id>', methods=['DELETE'])
@login_required
def remove_sub(sub_id):
    user_id = session['user_id']
    if delete_subscription(sub_id, user_id):
        return jsonify({'success': True, 'message': 'Subscription deleted'})
    return jsonify({'success': False, 'message': 'Not found'}), 404
