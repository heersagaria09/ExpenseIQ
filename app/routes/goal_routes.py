from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from app.models.goal import create_goal, get_goals, get_goal_by_id, update_goal, add_contribution, delete_goal
from app.models.notification import get_unread_count, create_notification
from app.utils.validators import validate_goal
from app.utils.constants import GOAL_CATEGORIES

goal_bp = Blueprint('goal', __name__)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated


@goal_bp.route('/goals')
@login_required
def index():
    user_id = session['user_id']
    unread = get_unread_count(user_id)
    goals = get_goals(user_id)
    active = [g for g in goals if not g.get('is_completed')]
    completed = [g for g in goals if g.get('is_completed')]
    return render_template('goals.html',
                           user_name=session.get('user_name', 'User'),
                           user_email=session.get('user_email', ''),
                           unread_count=unread,
                           goals=active,
                           completed_goals=completed,
                           categories=GOAL_CATEGORIES)


@goal_bp.route('/api/goals', methods=['GET'])
@login_required
def list_goals():
    user_id = session['user_id']
    goals = get_goals(user_id)
    return jsonify({'success': True, 'data': goals})


@goal_bp.route('/api/goals', methods=['POST'])
@login_required
def add_goal():
    user_id = session['user_id']
    data = request.get_json()
    errors = validate_goal(data)
    if errors:
        return jsonify({'success': False, 'message': errors[0]}), 400
    goal = create_goal(user_id, data)
    create_notification(user_id, f'New Goal: {goal["title"]}',
                        f'Goal created with target of ₹{goal["target_amount"]:,.0f}', 'goal_update')
    return jsonify({'success': True, 'message': 'Goal created', 'data': goal}), 201


@goal_bp.route('/api/goals/<goal_id>', methods=['PUT'])
@login_required
def edit_goal(goal_id):
    user_id = session['user_id']
    data = request.get_json()
    if update_goal(goal_id, user_id, data):
        return jsonify({'success': True, 'message': 'Goal updated'})
    return jsonify({'success': False, 'message': 'Goal not found'}), 404


@goal_bp.route('/api/goals/<goal_id>/contribute', methods=['POST'])
@login_required
def contribute(goal_id):
    user_id = session['user_id']
    data = request.get_json()
    amount = data.get('amount', 0)
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Valid amount required'}), 400
    if add_contribution(goal_id, user_id, amount):
        goal = get_goal_by_id(goal_id, user_id)
        if goal and goal.get('is_completed'):
            create_notification(user_id, f'Goal Achieved! 🎉', f'Congratulations! You achieved your goal: {goal["title"]}', 'goal_update')
        return jsonify({'success': True, 'message': f'₹{amount:,.0f} added to goal'})
    return jsonify({'success': False, 'message': 'Goal not found'}), 404


@goal_bp.route('/api/goals/<goal_id>', methods=['DELETE'])
@login_required
def remove_goal(goal_id):
    user_id = session['user_id']
    if delete_goal(goal_id, user_id):
        return jsonify({'success': True, 'message': 'Goal deleted'})
    return jsonify({'success': False, 'message': 'Goal not found'}), 404
