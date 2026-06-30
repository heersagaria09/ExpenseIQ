from datetime import datetime, timedelta
from app.models.expense import get_monthly_totals as expense_monthly, get_category_breakdown
from app.models.income import get_monthly_totals as income_monthly, get_source_breakdown
from app.models.budget import get_budgets
from app.models.goal import get_goals
from app.models.subscription import get_monthly_cost
from app.config.database import get_collection


def get_dashboard_data(user_id):
    now = datetime.utcnow()
    year, month = now.year, now.month

    expenses = get_collection('expenses')
    incomes = get_collection('incomes')

    from app.utils.helpers import get_month_range
    start, end = get_month_range(year, month)

    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    prev_start, prev_end = get_month_range(prev_year, prev_month)

    def agg_total(collection, user_id, start, end):
        # Use simple find instead of aggregation for mongomock compatibility
        docs = list(collection.find({'user_id': user_id, 'date': {'$gte': start, '$lte': end}}))
        return sum(doc.get('amount', 0) for doc in docs)

    curr_expense = agg_total(expenses, user_id, start, end)
    curr_income = agg_total(incomes, user_id, start, end)
    prev_expense = agg_total(expenses, user_id, prev_start, prev_end)
    prev_income = agg_total(incomes, user_id, prev_start, prev_end)

    def pct_change(curr, prev):
        if prev == 0:
            return 0
        return round(((curr - prev) / prev) * 100, 1)

    savings = curr_income - curr_expense

    # Use simple find for all-time totals
    all_expenses = list(expenses.find({'user_id': user_id}))
    all_incomes = list(incomes.find({'user_id': user_id}))
    total_expenses_all = sum(doc.get('amount', 0) for doc in all_expenses)
    total_income_all = sum(doc.get('amount', 0) for doc in all_incomes)
    total_balance = total_income_all - total_expenses_all

    cat_breakdown = get_category_breakdown(user_id, year, month)

    recent_expenses = list(expenses.find({'user_id': user_id}).sort('date', -1).limit(5))
    for e in recent_expenses:
        e['_id'] = str(e['_id'])
        if isinstance(e.get('date'), datetime):
            e['date_str'] = e['date'].strftime('%d %b')

    recent_incomes = list(incomes.find({'user_id': user_id}).sort('date', -1).limit(3))
    for i in recent_incomes:
        i['_id'] = str(i['_id'])
        if isinstance(i.get('date'), datetime):
            i['date_str'] = i['date'].strftime('%d %b')

    health_score = calculate_health_score(curr_income, curr_expense, savings)

    monthly_exp = expense_monthly(user_id, year)
    monthly_inc = income_monthly(user_id, year)

    return {
        'monthly_income': round(curr_income, 2),
        'monthly_expenses': round(curr_expense, 2),
        'savings': round(savings, 2),
        'total_balance': round(total_balance, 2),
        'income_change': pct_change(curr_income, prev_income),
        'expense_change': pct_change(curr_expense, prev_expense),
        'category_breakdown': cat_breakdown,
        'recent_expenses': recent_expenses,
        'recent_incomes': recent_incomes,
        'health_score': health_score,
        'monthly_expense_data': list(monthly_exp.values()),
        'monthly_income_data': list(monthly_inc.values()),
        'subscription_cost': get_monthly_cost(user_id),
        'budget_count': len(get_budgets(user_id)),
        'goal_count': len(get_goals(user_id, include_completed=False)),
        'top_category': cat_breakdown[0]['_id'] if cat_breakdown else 'N/A',
    }


def calculate_health_score(income, expenses, savings):
    if income == 0:
        return 0
    savings_rate = (savings / income) * 100
    if savings_rate >= 30:
        score = 90 + min(10, (savings_rate - 30) / 3)
    elif savings_rate >= 20:
        score = 75 + (savings_rate - 20) * 1.5
    elif savings_rate >= 10:
        score = 55 + (savings_rate - 10) * 2
    elif savings_rate >= 0:
        score = 30 + savings_rate * 2.5
    else:
        score = max(0, 30 + savings_rate)
    return round(min(100, max(0, score)))


def get_analytics_data(user_id, year=None, month=None):
    now = datetime.utcnow()
    year = year or now.year
    month = month or now.month

    monthly_expenses = expense_monthly(user_id, year)
    monthly_incomes = income_monthly(user_id, year)
    cat_breakdown = get_category_breakdown(user_id, year, month)
    src_breakdown = get_source_breakdown(user_id, year, month)
    budgets = get_budgets(user_id, year, month)

    months_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    cashflow = []
    for i in range(1, 13):
        cashflow.append({
            'month': months_labels[i-1],
            'income': monthly_incomes.get(i, 0),
            'expense': monthly_expenses.get(i, 0),
            'savings': monthly_incomes.get(i, 0) - monthly_expenses.get(i, 0),
        })

    return {
        'cashflow': cashflow,
        'category_breakdown': cat_breakdown,
        'source_breakdown': src_breakdown,
        'budgets': budgets,
        'year': year,
        'month': month,
    }
