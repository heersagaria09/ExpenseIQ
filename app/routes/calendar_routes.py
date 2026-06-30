from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from datetime import datetime
import calendar as cal
from app.config.database import get_db
from app.models.notification import get_unread_count

calendar_bp = Blueprint('calendar', __name__)

MONTH_NAMES = ['January','February','March','April','May','June',
               'July','August','September','October','November','December']


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated


def _month_bounds(year, month):
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)
    return start, end


def get_month_events(user_id, year, month):
    db = get_db()
    start, end = _month_bounds(year, month)
    events = {}

    for e in db.expenses.find({'user_id': user_id, 'date': {'$gte': start, '$lt': end}}):
        d = e.get('date')
        if not hasattr(d, 'day'):
            continue
        day = d.day
        if day not in events:
            events[day] = {'expenses': [], 'income': [], 'total_expense': 0.0, 'total_income': 0.0}
        events[day]['expenses'].append({
            'title': e.get('title', ''),
            'amount': float(e.get('amount', 0)),
            'category': e.get('category', '')
        })
        events[day]['total_expense'] += float(e.get('amount', 0))

    for i in db.income.find({'user_id': user_id, 'date': {'$gte': start, '$lt': end}}):
        d = i.get('date')
        if not hasattr(d, 'day'):
            continue
        day = d.day
        if day not in events:
            events[day] = {'expenses': [], 'income': [], 'total_expense': 0.0, 'total_income': 0.0}
        events[day]['income'].append({
            'title': i.get('title', ''),
            'amount': float(i.get('amount', 0)),
            'source': i.get('source', '')
        })
        events[day]['total_income'] += float(i.get('amount', 0))

    return {str(k): v for k, v in events.items()}


def get_year_data(user_id, year):
    db = get_db()
    start = datetime(year, 1, 1)
    end = datetime(year + 1, 1, 1)

    expense_days = {}
    income_days = {}

    for e in db.expenses.find({'user_id': user_id, 'date': {'$gte': start, '$lt': end}}):
        d = e.get('date')
        if hasattr(d, 'month') and hasattr(d, 'day'):
            expense_days.setdefault(d.month, set()).add(d.day)

    for i in db.income.find({'user_id': user_id, 'date': {'$gte': start, '$lt': end}}):
        d = i.get('date')
        if hasattr(d, 'month') and hasattr(d, 'day'):
            income_days.setdefault(d.month, set()).add(d.day)

    year_data = {}
    for m in range(1, 13):
        matrix = cal.monthcalendar(year, m)
        exp_set = expense_days.get(m, set())
        inc_set = income_days.get(m, set())
        year_data[m] = {
            'matrix': matrix,
            'expense_days': list(exp_set),
            'income_days': list(inc_set),
            'has_data': bool(exp_set or inc_set)
        }
    return year_data


@calendar_bp.route('/calendar')
@login_required
def index():
    user_id = session['user_id']
    now = datetime.utcnow()
    year = int(request.args.get('year', now.year))
    month = int(request.args.get('month', now.month))
    month = max(1, min(12, month))

    unread = get_unread_count(user_id)
    events_by_day = get_month_events(user_id, year, month)
    cal_matrix = cal.monthcalendar(year, month)
    year_data = get_year_data(user_id, year)

    prev_month = 12 if month == 1 else month - 1
    prev_year = year - 1 if month == 1 else year
    next_month = 1 if month == 12 else month + 1
    next_year = year + 1 if month == 12 else year

    return render_template('calendar.html',
        year=year, month=month,
        month_name=MONTH_NAMES[month - 1],
        month_names=MONTH_NAMES,
        cal_matrix=cal_matrix,
        events_by_day=events_by_day,
        prev_month=prev_month, prev_year=prev_year,
        next_month=next_month, next_year=next_year,
        today_year=now.year, today_month=now.month, today_day=now.day,
        year_data=year_data,
        unread_count=unread,
        user_name=session.get('user_name', ''),
        user_email=session.get('user_email', ''),
    )


@calendar_bp.route('/api/calendar/events')
@login_required
def api_events():
    user_id = session['user_id']
    now = datetime.utcnow()
    year = int(request.args.get('year', now.year))
    month = int(request.args.get('month', now.month))
    events = get_month_events(user_id, year, month)
    return jsonify({'success': True, 'data': events})
