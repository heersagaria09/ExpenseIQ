from datetime import datetime
from app.config.database import get_collection
from bson import ObjectId


def create_expense(user_id, data):
    expenses = get_collection('expenses')
    expense = {
        'user_id': user_id,
        'title': data.get('title', '').strip(),
        'amount': float(data.get('amount', 0)),
        'category': data.get('category', 'Others'),
        'date': data.get('date', datetime.utcnow()),
        'notes': data.get('notes', ''),
        'is_recurring': data.get('is_recurring', False),
        'recurring_frequency': data.get('recurring_frequency', ''),
        'receipt_url': data.get('receipt_url', ''),
        'tags': data.get('tags', []),
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
    }
    result = expenses.insert_one(expense)
    expense['_id'] = str(result.inserted_id)
    return expense


def get_expenses(user_id, filters=None, page=1, per_page=20):
    expenses = get_collection('expenses')
    query = {'user_id': user_id}
    if filters:
        if filters.get('category'):
            query['category'] = filters['category']
        if filters.get('start_date') and filters.get('end_date'):
            query['date'] = {'$gte': filters['start_date'], '$lte': filters['end_date']}
        if filters.get('search'):
            query['title'] = {'$regex': filters['search'], '$options': 'i'}
    
    try:
        total = expenses.count_documents(query)
        cursor = expenses.find(query).sort('date', -1).skip((page-1)*per_page).limit(per_page)
        items = []
        for doc in cursor:
            doc['_id'] = str(doc['_id'])
            if isinstance(doc.get('date'), datetime):
                doc['date_str'] = doc['date'].strftime('%d %b %Y')
            # Ensure amount is a number
            doc['amount'] = float(doc.get('amount', 0))
            items.append(doc)
        return {'items': items, 'total': total, 'page': page, 'pages': (total + per_page - 1) // per_page}
    except Exception as e:
        print(f'Error in get_expenses: {e}')
        return {'items': [], 'total': 0, 'page': 1, 'pages': 0}


def get_expense_by_id(expense_id, user_id):
    expenses = get_collection('expenses')
    try:
        doc = expenses.find_one({'_id': ObjectId(expense_id), 'user_id': user_id})
        if doc:
            doc['_id'] = str(doc['_id'])
        return doc
    except Exception:
        return None


def update_expense(expense_id, user_id, data):
    expenses = get_collection('expenses')
    data['updated_at'] = datetime.utcnow()
    result = expenses.update_one({'_id': ObjectId(expense_id), 'user_id': user_id}, {'$set': data})
    return result.modified_count > 0


def delete_expense(expense_id, user_id):
    expenses = get_collection('expenses')
    result = expenses.delete_one({'_id': ObjectId(expense_id), 'user_id': user_id})
    return result.deleted_count > 0


def get_monthly_expenses(user_id, year, month):
    from app.utils.helpers import get_month_range
    expenses = get_collection('expenses')
    start, end = get_month_range(year, month)
    cursor = expenses.find({'user_id': user_id, 'date': {'$gte': start, '$lte': end}})
    total = 0
    items = []
    for doc in cursor:
        doc['_id'] = str(doc['_id'])
        if isinstance(doc.get('date'), datetime):
            doc['date_str'] = doc['date'].strftime('%d %b %Y')
        total += doc.get('amount', 0)
        items.append(doc)
    return {'items': items, 'total': total}


def get_category_breakdown(user_id, year, month):
    from app.utils.helpers import get_month_range
    expenses = get_collection('expenses')
    start, end = get_month_range(year, month)
    # Use simple find instead of aggregation for mongomock compatibility
    docs = list(expenses.find({'user_id': user_id, 'date': {'$gte': start, '$lte': end}}))
    breakdown = {}
    for doc in docs:
        category = doc.get('category', 'Others')
        amount = doc.get('amount', 0)
        if category not in breakdown:
            breakdown[category] = {'total': 0, 'count': 0}
        breakdown[category]['total'] += amount
        breakdown[category]['count'] += 1
    # Convert to list and sort
    result = [{'_id': k, 'total': v['total'], 'count': v['count']} for k, v in breakdown.items()]
    result.sort(key=lambda x: x['total'], reverse=True)
    return result


def get_monthly_totals(user_id, year):
    expenses = get_collection('expenses')
    # Use simple find instead of aggregation for mongomock compatibility
    docs = list(expenses.find({
        'user_id': user_id,
        'date': {'$gte': datetime(year, 1, 1), '$lte': datetime(year, 12, 31, 23, 59, 59)}
    }))
    monthly = {i: 0 for i in range(1, 13)}
    for doc in docs:
        month = doc.get('date').month if isinstance(doc.get('date'), datetime) else 1
        monthly[month] += doc.get('amount', 0)
    return monthly
