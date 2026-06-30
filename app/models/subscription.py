from datetime import datetime, timedelta
from app.config.database import get_collection
from bson import ObjectId


def create_subscription(user_id, data):
    subs = get_collection('subscriptions')
    sub = {
        'user_id': user_id,
        'name': data.get('name', '').strip(),
        'category': data.get('category', 'Others'),
        'amount': float(data.get('amount', 0)),
        'billing_cycle': data.get('billing_cycle', 'Monthly'),
        'next_renewal': data.get('next_renewal'),
        'website': data.get('website', ''),
        'notes': data.get('notes', ''),
        'is_active': True,
        'auto_renewal': data.get('auto_renewal', True),
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
    }
    result = subs.insert_one(sub)
    sub['_id'] = str(result.inserted_id)
    return sub


def get_subscriptions(user_id, active_only=False):
    subs = get_collection('subscriptions')
    query = {'user_id': user_id}
    if active_only:
        query['is_active'] = True
    cursor = subs.find(query).sort('name', 1)
    items = []
    now = datetime.utcnow()
    for doc in cursor:
        doc['_id'] = str(doc['_id'])
        if doc.get('next_renewal'):
            renewal = doc['next_renewal']
            if isinstance(renewal, datetime):
                days_left = (renewal - now).days
                doc['days_until_renewal'] = days_left
                doc['renewal_soon'] = days_left <= 7
                doc['renewal_str'] = renewal.strftime('%d %b %Y')
        items.append(doc)
    return items


def get_subscription_by_id(sub_id, user_id):
    subs = get_collection('subscriptions')
    try:
        doc = subs.find_one({'_id': ObjectId(sub_id), 'user_id': user_id})
        if doc:
            doc['_id'] = str(doc['_id'])
        return doc
    except Exception:
        return None


def update_subscription(sub_id, user_id, data):
    subs = get_collection('subscriptions')
    data['updated_at'] = datetime.utcnow()
    result = subs.update_one({'_id': ObjectId(sub_id), 'user_id': user_id}, {'$set': data})
    return result.modified_count > 0


def delete_subscription(sub_id, user_id):
    subs = get_collection('subscriptions')
    result = subs.delete_one({'_id': ObjectId(sub_id), 'user_id': user_id})
    return result.deleted_count > 0


def get_monthly_cost(user_id):
    subs = get_collection('subscriptions')
    cursor = subs.find({'user_id': user_id, 'is_active': True})
    total = 0
    for doc in cursor:
        amount = doc.get('amount', 0)
        cycle = doc.get('billing_cycle', 'Monthly')
        if cycle == 'Monthly':
            total += amount
        elif cycle == 'Quarterly':
            total += amount / 3
        elif cycle == 'Half-Yearly':
            total += amount / 6
        elif cycle == 'Yearly':
            total += amount / 12
    return round(total, 2)
