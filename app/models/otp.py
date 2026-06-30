from datetime import datetime, timedelta
from app.config.database import get_collection


def save_otp(mobile, otp, purpose='login'):
    otps = get_collection('otps')
    otps.delete_many({'mobile': str(mobile), 'purpose': purpose})
    doc = {
        'mobile': str(mobile).strip(),
        'otp': str(otp),
        'purpose': purpose,
        'attempts': 0,
        'verified': False,
        'expires_at': datetime.utcnow() + timedelta(minutes=10),
        'created_at': datetime.utcnow(),
    }
    otps.insert_one(doc)
    return doc


def verify_otp(mobile, otp, purpose='login'):
    otps = get_collection('otps')
    doc = otps.find_one({'mobile': str(mobile).strip(), 'purpose': purpose, 'verified': False})
    if not doc:
        return False, 'OTP not found or already used'
    if datetime.utcnow() > doc['expires_at']:
        return False, 'OTP has expired'
    if doc.get('attempts', 0) >= 5:
        return False, 'Too many attempts'
    otps.update_one({'_id': doc['_id']}, {'$inc': {'attempts': 1}})
    if doc['otp'] != str(otp):
        return False, 'Invalid OTP'
    otps.update_one({'_id': doc['_id']}, {'$set': {'verified': True}})
    return True, 'OTP verified'


def cleanup_expired():
    otps = get_collection('otps')
    otps.delete_many({'expires_at': {'$lt': datetime.utcnow()}})
