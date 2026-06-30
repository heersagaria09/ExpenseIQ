import re
from app.utils.helpers import is_valid_email, is_valid_mobile

USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9._-]{3,20}$')

def is_valid_username(username):
    return bool(USERNAME_REGEX.match(str(username).strip()))


def validate_signup(data):
    errors = []
    if not data.get('full_name') or len(data['full_name'].strip()) < 2:
        errors.append('Full name must be at least 2 characters')
    if not data.get('username') or not is_valid_username(data['username']):
        errors.append('Username must be 3-20 characters and can include letters, numbers, dots, or underscores')
    if not data.get('email') or not is_valid_email(data['email']):
        errors.append('Valid email address is required')
    if not data.get('mobile') or not is_valid_mobile(data['mobile']):
        errors.append('Valid 10-digit mobile number is required')
    if not data.get('password') or len(data['password']) < 6:
        errors.append('Password must be at least 6 characters')
    if data.get('password') != data.get('confirm_password'):
        errors.append('Passwords do not match')
    return errors


def validate_login(data):
    identifier = data.get('identifier') or data.get('email') or data.get('mobile')
    errors = []
    if not identifier:
        errors.append('Email, username, or mobile number is required')
    if not data.get('password'):
        errors.append('Password is required')
    return errors


def validate_expense(data):
    errors = []
    if not data.get('title') or not data['title'].strip():
        errors.append('Title is required')
    try:
        amount = float(data.get('amount', 0))
        if amount <= 0:
            errors.append('Amount must be greater than 0')
    except (ValueError, TypeError):
        errors.append('Valid amount is required')
    if not data.get('category'):
        errors.append('Category is required')
    return errors


def validate_income(data):
    errors = []
    if not data.get('title') or not data['title'].strip():
        errors.append('Title is required')
    try:
        amount = float(data.get('amount', 0))
        if amount <= 0:
            errors.append('Amount must be greater than 0')
    except (ValueError, TypeError):
        errors.append('Valid amount is required')
    return errors


def validate_budget(data):
    errors = []
    if not data.get('category'):
        errors.append('Category is required')
    try:
        amount = float(data.get('amount', 0))
        if amount <= 0:
            errors.append('Budget amount must be greater than 0')
    except (ValueError, TypeError):
        errors.append('Valid budget amount is required')
    return errors


def validate_goal(data):
    errors = []
    if not data.get('title') or not data['title'].strip():
        errors.append('Goal title is required')
    try:
        target = float(data.get('target_amount', 0))
        if target <= 0:
            errors.append('Target amount must be greater than 0')
    except (ValueError, TypeError):
        errors.append('Valid target amount is required')
    return errors
