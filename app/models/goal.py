from datetime import datetime
from app.config.database import get_collection
from bson import ObjectId


def create_goal(user_id, data):
    goals = get_collection('goals')
    goal = {
        'user_id': user_id,
        'title': data.get('title', '').strip(),
        'category': data.get('category', 'Others'),
        'target_amount': float(data.get('target_amount', 0)),
        'current_amount': float(data.get('current_amount', 0)),
        'target_date': data.get('target_date'),
        'notes': data.get('notes', ''),
        'is_completed': False,
        'milestones': [],
        'contributions': [],
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
    }
    result = goals.insert_one(goal)
    goal['_id'] = str(result.inserted_id)
    return goal


def get_goals(user_id, include_completed=True):
    goals = get_collection('goals')
    query = {'user_id': user_id}
    if not include_completed:
        query['is_completed'] = False
    cursor = goals.find(query).sort('created_at', -1)
    items = []
    for doc in cursor:
        doc['_id'] = str(doc['_id'])
        if doc.get('target_amount', 0) > 0:
            doc['progress_pct'] = round((doc.get('current_amount', 0) / doc['target_amount']) * 100, 1)
        else:
            doc['progress_pct'] = 0
        items.append(doc)
    return items


def get_goal_by_id(goal_id, user_id):
    goals = get_collection('goals')
    try:
        doc = goals.find_one({'_id': ObjectId(goal_id), 'user_id': user_id})
        if doc:
            doc['_id'] = str(doc['_id'])
        return doc
    except Exception:
        return None


def update_goal(goal_id, user_id, data):
    goals = get_collection('goals')
    data['updated_at'] = datetime.utcnow()
    result = goals.update_one({'_id': ObjectId(goal_id), 'user_id': user_id}, {'$set': data})
    return result.modified_count > 0


def add_contribution(goal_id, user_id, amount):
    goals = get_collection('goals')
    try:
        goal = goals.find_one({'_id': ObjectId(goal_id), 'user_id': user_id})
        if not goal:
            return False
        new_amount = goal.get('current_amount', 0) + float(amount)
        is_completed = new_amount >= goal.get('target_amount', 0)
        contribution = {'amount': float(amount), 'date': datetime.utcnow()}
        goals.update_one({'_id': ObjectId(goal_id)}, {
            '$set': {'current_amount': new_amount, 'is_completed': is_completed, 'updated_at': datetime.utcnow()},
            '$push': {'contributions': contribution}
        })
        return True
    except Exception:
        return False


def delete_goal(goal_id, user_id):
    goals = get_collection('goals')
    result = goals.delete_one({'_id': ObjectId(goal_id), 'user_id': user_id})
    return result.deleted_count > 0
