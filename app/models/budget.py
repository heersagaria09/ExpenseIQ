from datetime import datetime
from app.config.database import get_collection
from bson import ObjectId


def create_budget(user_id, data):
    budgets = get_collection('budgets')
    now = datetime.utcnow()
    budget = {
        'user_id': user_id,
        'category': data.get('category', ''),
        'amount': float(data.get('amount', 0)),
        'month': int(data.get('month', now.month)),
        'year': int(data.get('year', now.year)),
        'alert_threshold': float(data.get('alert_threshold', 80)),
        'notes': data.get('notes', ''),
        'created_at': now,
        'updated_at': now,
    }
    existing = budgets.find_one({'user_id': user_id, 'category': budget['category'],
                                  'month': budget['month'], 'year': budget['year']})
    if existing:
        budgets.update_one({'_id': existing['_id']}, {'$set': {'amount': budget['amount'], 'updated_at': now}})
        budget['_id'] = str(existing['_id'])
    else:
        result = budgets.insert_one(budget)
        budget['_id'] = str(result.inserted_id)
    return budget


def get_budgets(user_id, year=None, month=None):
    budgets = get_collection('budgets')
    now = datetime.utcnow()
    query = {'user_id': user_id, 'year': year or now.year, 'month': month or now.month}
    cursor = budgets.find(query).sort('category', 1)
    items = []
    for doc in cursor:
        doc['_id'] = str(doc['_id'])
        items.append(doc)
    return items


def get_budget_by_id(budget_id, user_id):
    budgets = get_collection('budgets')
    try:
        doc = budgets.find_one({'_id': ObjectId(budget_id), 'user_id': user_id})
        if doc:
            doc['_id'] = str(doc['_id'])
        return doc
    except Exception:
        return None


def update_budget(budget_id, user_id, data):
    budgets = get_collection('budgets')
    data['updated_at'] = datetime.utcnow()
    result = budgets.update_one({'_id': ObjectId(budget_id), 'user_id': user_id}, {'$set': data})
    return result.modified_count > 0


def delete_budget(budget_id, user_id):
    budgets = get_collection('budgets')
    result = budgets.delete_one({'_id': ObjectId(budget_id), 'user_id': user_id})
    return result.deleted_count > 0
