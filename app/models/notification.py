from datetime import datetime
from app.config.database import get_collection
from bson import ObjectId


def create_notification(user_id, title, message, notif_type='system', link=''):
    notifs = get_collection('notifications')
    notif = {
        'user_id': user_id,
        'title': title,
        'message': message,
        'type': notif_type,
        'link': link,
        'is_read': False,
        'created_at': datetime.utcnow(),
    }
    result = notifs.insert_one(notif)
    notif['_id'] = str(result.inserted_id)
    return notif


def get_notifications(user_id, unread_only=False, page=1, per_page=20):
    notifs = get_collection('notifications')
    query = {'user_id': user_id}
    if unread_only:
        query['is_read'] = False
    total = notifs.count_documents(query)
    cursor = notifs.find(query).sort('created_at', -1).skip((page-1)*per_page).limit(per_page)
    items = []
    for doc in cursor:
        doc['_id'] = str(doc['_id'])
        if isinstance(doc.get('created_at'), datetime):
            doc['time_str'] = doc['created_at'].strftime('%d %b %Y %I:%M %p')
        items.append(doc)
    return {'items': items, 'total': total, 'unread': notifs.count_documents({'user_id': user_id, 'is_read': False})}


def mark_read(notif_id, user_id):
    notifs = get_collection('notifications')
    notifs.update_one({'_id': ObjectId(notif_id), 'user_id': user_id}, {'$set': {'is_read': True}})


def mark_all_read(user_id):
    notifs = get_collection('notifications')
    notifs.update_many({'user_id': user_id, 'is_read': False}, {'$set': {'is_read': True}})


def delete_notification(notif_id, user_id):
    notifs = get_collection('notifications')
    notifs.delete_one({'_id': ObjectId(notif_id), 'user_id': user_id})


def get_unread_count(user_id):
    notifs = get_collection('notifications')
    return notifs.count_documents({'user_id': user_id, 'is_read': False})
