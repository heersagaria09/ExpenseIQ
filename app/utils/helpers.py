import re
import random
import string
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, session, redirect, url_for
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
import bcrypt


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))


def is_valid_mobile(mobile):
    return bool(re.match(r'^[6-9]\d{9}$', str(mobile).strip()))


def is_valid_email(email):
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))


def format_currency(amount):
    return f"₹{amount:,.2f}"


def get_month_range(year, month):
    from calendar import monthrange
    start = datetime(year, month, 1)
    end = datetime(year, month, monthrange(year, month)[1], 23, 59, 59)
    return start, end


def jwt_required_custom(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('auth.login_page'))
    return decorated


def success_response(data=None, message='Success', status=200):
    resp = {'success': True, 'message': message}
    if data is not None:
        resp['data'] = data
    return jsonify(resp), status


def error_response(message='Error', status=400, errors=None):
    resp = {'success': False, 'message': message}
    if errors:
        resp['errors'] = errors
    return jsonify(resp), status


def paginate(collection, query, page=1, per_page=20, sort_field='created_at', sort_dir=-1):
    from bson import ObjectId
    total = collection.count_documents(query)
    cursor = collection.find(query).sort(sort_field, sort_dir).skip((page-1)*per_page).limit(per_page)
    items = []
    for doc in cursor:
        doc['_id'] = str(doc['_id'])
        items.append(doc)
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    }
