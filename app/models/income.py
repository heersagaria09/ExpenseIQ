from datetime import datetime
from app.config.database import get_collection
from bson import ObjectId


def create_income(user_id, data):
    incomes = get_collection('incomes')
    income = {
        'user_id': user_id,
        'title': data.get('title', '').strip(),
        'amount': float(data.get('amount', 0)),
        'source': data.get('source', 'Others'),
        'date': data.get('date', datetime.utcnow()),
        'notes': data.get('notes', ''),
        'is_recurring': data.get('is_recurring', False),
        'recurring_frequency': data.get('recurring_frequency', ''),
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
    }
    result = incomes.insert_one(income)
    income['_id'] = str(result.inserted_id)
    return income


def get_incomes(user_id, filters=None, page=1, per_page=20):
    incomes = get_collection('incomes')
    query = {'user_id': user_id}
    if filters:
        if filters.get('source'):
            query['source'] = filters['source']
        if filters.get('start_date') and filters.get('end_date'):
            query['date'] = {'$gte': filters['start_date'], '$lte': filters['end_date']}
        if filters.get('search'):
            query['title'] = {'$regex': filters['search'], '$options': 'i'}
    total = incomes.count_documents(query)
    cursor = incomes.find(query).sort('date', -1).skip((page-1)*per_page).limit(per_page)
    items = []
    for doc in cursor:
        doc['_id'] = str(doc['_id'])
        if isinstance(doc.get('date'), datetime):
            doc['date_str'] = doc['date'].strftime('%d %b %Y')
        items.append(doc)
    return {'items': items, 'total': total, 'page': page, 'pages': (total + per_page - 1) // per_page}


def get_income_by_id(income_id, user_id):
    incomes = get_collection('incomes')
    try:
        doc = incomes.find_one({'_id': ObjectId(income_id), 'user_id': user_id})
        if doc:
            doc['_id'] = str(doc['_id'])
        return doc
    except Exception:
        return None


def update_income(income_id, user_id, data):
    incomes = get_collection('incomes')
    data['updated_at'] = datetime.utcnow()
    result = incomes.update_one({'_id': ObjectId(income_id), 'user_id': user_id}, {'$set': data})
    return result.modified_count > 0


def delete_income(income_id, user_id):
    incomes = get_collection('incomes')
    result = incomes.delete_one({'_id': ObjectId(income_id), 'user_id': user_id})
    return result.deleted_count > 0


def get_monthly_income(user_id, year, month):
    from app.utils.helpers import get_month_range
    incomes = get_collection('incomes')
    start, end = get_month_range(year, month)
    cursor = incomes.find({'user_id': user_id, 'date': {'$gte': start, '$lte': end}})
    total = 0
    items = []
    for doc in cursor:
        doc['_id'] = str(doc['_id'])
        if isinstance(doc.get('date'), datetime):
            doc['date_str'] = doc['date'].strftime('%d %b %Y')
        total += doc.get('amount', 0)
        items.append(doc)
    return {'items': items, 'total': total}


def get_source_breakdown(user_id, year, month):
    from app.utils.helpers import get_month_range
    incomes = get_collection('incomes')
    start, end = get_month_range(year, month)
    # Use simple find instead of aggregation for mongomock compatibility
    docs = list(incomes.find({'user_id': user_id, 'date': {'$gte': start, '$lte': end}}))
    breakdown = {}
    for doc in docs:
        source = doc.get('source', 'Others')
        amount = doc.get('amount', 0)
        if source not in breakdown:
            breakdown[source] = {'total': 0, 'count': 0}
        breakdown[source]['total'] += amount
        breakdown[source]['count'] += 1
    # Convert to list and sort
    result = [{'_id': k, 'total': v['total'], 'count': v['count']} for k, v in breakdown.items()]
    result.sort(key=lambda x: x['total'], reverse=True)
    return result


def get_monthly_totals(user_id, year):
    incomes = get_collection('incomes')
    # Use simple find instead of aggregation for mongomock compatibility
    docs = list(incomes.find({
        'user_id': user_id,
        'date': {'$gte': datetime(year, 1, 1), '$lte': datetime(year, 12, 31, 23, 59, 59)}
    }))
    monthly = {i: 0 for i in range(1, 13)}
    for doc in docs:
        month = doc.get('date').month if isinstance(doc.get('date'), datetime) else 1
        monthly[month] += doc.get('amount', 0)
    return monthly
