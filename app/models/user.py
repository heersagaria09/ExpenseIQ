from datetime import datetime
from app.config.database import get_collection
from bson import ObjectId


def create_user(data):
    users = get_collection('users')
    user = {
        'full_name': data.get('full_name', ''),
        'username': data.get('username', '').lower().strip(),
        'email': data.get('email', '').lower().strip(),
        'mobile': data.get('mobile', ''),
        'password_hash': data.get('password_hash', ''),
        'google_id': data.get('google_id', ''),
        'avatar': data.get('avatar', ''),
        'is_verified': data.get('is_verified', False),
        'is_active': True,
        'theme': 'dark',
        'currency': 'INR',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'last_login': None,
    }
    result = users.insert_one(user)
    user['_id'] = str(result.inserted_id)
    return user


def find_user_by_email(email):
    users = get_collection('users')
    user = users.find_one({'email': email.lower().strip()})
    if user:
        user['_id'] = str(user['_id'])
    return user


def find_user_by_id(user_id):
    users = get_collection('users')
    try:
        user = users.find_one({'_id': ObjectId(user_id)})
        if user:
            user['_id'] = str(user['_id'])
        return user
    except Exception:
        return None


def find_user_by_mobile(mobile):
    users = get_collection('users')
    user = users.find_one({'mobile': str(mobile).strip()})
    if user:
        user['_id'] = str(user['_id'])
    return user


def find_user_by_username(username):
    users = get_collection('users')
    user = users.find_one({'username': str(username).lower().strip()})
    if user:
        user['_id'] = str(user['_id'])
    return user


def find_user_by_google_id(google_id):
    users = get_collection('users')
    user = users.find_one({'google_id': google_id})
    if user:
        user['_id'] = str(user['_id'])
    return user


def update_user(user_id, data):
    users = get_collection('users')
    data['updated_at'] = datetime.utcnow()
    users.update_one({'_id': ObjectId(user_id)}, {'$set': data})


def email_exists(email):
    users = get_collection('users')
    return users.count_documents({'email': email.lower().strip()}) > 0


def username_exists(username):
    users = get_collection('users')
    return users.count_documents({'username': str(username).lower().strip()}) > 0


def mobile_exists(mobile):
    users = get_collection('users')
    return users.count_documents({'mobile': str(mobile).strip()}) > 0
