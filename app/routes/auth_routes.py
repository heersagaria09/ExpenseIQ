import os
import random
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, current_app, make_response
from app.config.settings import Config
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, decode_token
from app.models.user import create_user, find_user_by_email, find_user_by_id, find_user_by_mobile, find_user_by_username, update_user, email_exists, mobile_exists, username_exists
from app.models.otp import save_otp, verify_otp
from app.utils.helpers import hash_password, check_password, is_valid_mobile, is_valid_email, generate_otp
from app.utils.validators import validate_signup, validate_login

# Simple in-memory rate limiter (per-IP). Resets after window seconds.
from time import time
LOGIN_ATTEMPTS = {}
RATE_WINDOW = 15 * 60  # 15 minutes
RATE_MAX = 10

auth_bp = Blueprint('auth', __name__)


def send_otp_sms(mobile, otp):
    fast2sms_key = os.environ.get('FAST2SMS_API_KEY', '')
    if fast2sms_key:
        try:
            import requests
            url = "https://www.fast2sms.com/dev/bulkV2"
            payload = {
                "route": "otp",
                "variables_values": otp,
                "flash": 0,
                "numbers": mobile,
            }
            headers = {"authorization": fast2sms_key}
            requests.post(url, json=payload, headers=headers, timeout=10)
            return True
        except Exception:
            pass
    return False


@auth_bp.route('/login')
def login_page():
    return render_template('login.html')


@auth_bp.route('/signup')
def signup_page():
    return render_template('signup.html')


@auth_bp.route('/signup', methods=['POST'])
def signup_form():
    # Support non-AJAX form submission: create account, flash message, redirect to login
    data = request.form.to_dict()
    errors = validate_signup(data)
    if errors:
        # flash first error and redirect back to signup
        from flask import flash
        flash(errors[0], 'error')
        return redirect(url_for('auth.signup_page'))
    if email_exists(data['email']):
        from flask import flash
        flash('Email already registered', 'error')
        return redirect(url_for('auth.signup_page'))
    if username_exists(data['username']):
        from flask import flash
        flash('Username already taken', 'error')
        return redirect(url_for('auth.signup_page'))
    if data.get('mobile') and mobile_exists(data['mobile']):
        from flask import flash
        flash('Mobile number already registered', 'error')
        return redirect(url_for('auth.signup_page'))
    # create user
    user = create_user({
        'full_name': data.get('full_name') or data.get('name', ''),
        'username': data.get('username', ''),
        'email': data.get('email', ''),
        'mobile': data.get('mobile', ''),
        'password_hash': hash_password(data.get('password', '')),
        'is_verified': False,
    })
    from flask import flash
    flash('Account created successfully. Please log in to continue.', 'success')
    return redirect(url_for('auth.login_page'))


@auth_bp.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.get_json()
    errors = validate_signup(data)
    if errors:
        return jsonify({'success': False, 'message': errors[0], 'errors': errors}), 400
    if email_exists(data['email']):
        return jsonify({'success': False, 'message': 'Email already registered'}), 400
    if username_exists(data['username']):
        return jsonify({'success': False, 'message': 'Username already taken'}), 400
    if data.get('mobile') and mobile_exists(data['mobile']):
        return jsonify({'success': False, 'message': 'Mobile number already registered'}), 400
    user = create_user({
        'full_name': data['full_name'],
        'username': data['username'],
        'email': data['email'],
        'mobile': data.get('mobile', ''),
        'password_hash': hash_password(data['password']),
        'is_verified': False,
    })
    # Do not auto-login the user after signup. Require explicit login.
    return jsonify({
        'success': True,
        'message': 'Account created successfully. Please log in to continue.',
        'user': {'id': user['_id'], 'name': user['full_name'], 'email': user['email']},
        'redirect': '/login'
    }), 201


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    # rate limiting per IP
    ip = request.remote_addr or 'anon'
    info = LOGIN_ATTEMPTS.get(ip, {'count': 0, 'ts': time()})
    if time() - info['ts'] > RATE_WINDOW:
        info = {'count': 0, 'ts': time()}
    if info['count'] >= RATE_MAX:
        return jsonify({'success': False, 'message': 'Too many login attempts. Please try again later.'}), 429
    errors = validate_login(data)
    if errors:
        return jsonify({'success': False, 'message': errors[0]}), 400
    identifier = data.get('identifier') or data.get('email') or data.get('mobile', '')
    user = None
    if is_valid_mobile(identifier):
        user = find_user_by_mobile(identifier)
    if not user and is_valid_email(identifier):
        user = find_user_by_email(identifier)
    if not user:
        user = find_user_by_username(identifier)
    if not user or not check_password(data['password'], user.get('password_hash', '')):
        # increment failed attempts
        info['count'] = info.get('count', 0) + 1
        info['ts'] = time()
        LOGIN_ATTEMPTS[ip] = info
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
    update_user(user['_id'], {'last_login': datetime.utcnow()})
    # successful login -> reset attempts
    if ip in LOGIN_ATTEMPTS:
        LOGIN_ATTEMPTS.pop(ip, None)
    access_token = create_access_token(identity=user['_id'])
    refresh_token = create_refresh_token(identity=user['_id'])
    session['user_id'] = user['_id']
    session['user_name'] = user['full_name']
    session['user_email'] = user['email']
    remember = bool(request.json.get('remember')) if request.is_json else False
    if remember:
        session.permanent = True
    resp = make_response(jsonify({
        'success': True,
        'message': 'Login successful',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {'id': user['_id'], 'name': user['full_name'], 'email': user['email']},
        'redirect': '/dashboard'
    }))
    if remember:
        resp.set_cookie('refresh_token', refresh_token, httponly=True, secure=not current_app.config.get('DEBUG', True), samesite='Lax', max_age=30*24*3600)
    return resp


@auth_bp.route('/api/auth/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    mobile = str(data.get('mobile', '')).strip()
    purpose = data.get('purpose', 'login')
    if not is_valid_mobile(mobile):
        return jsonify({'success': False, 'message': 'Enter a valid 10-digit Indian mobile number'}), 400
    otp = generate_otp(6)
    save_otp(mobile, otp, purpose)
    sms_sent = send_otp_sms(mobile, otp)
    dev_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    response = {'success': True, 'message': 'OTP sent successfully'}
    if dev_mode or not sms_sent:
        response['dev_otp'] = otp
    return jsonify(response)


@auth_bp.route('/api/auth/verify-otp', methods=['POST'])
def verify_otp_route():
    data = request.get_json()
    mobile = str(data.get('mobile', '')).strip()
    otp = str(data.get('otp', '')).strip()
    purpose = data.get('purpose', 'login')
    full_name = data.get('full_name', '').strip()
    if not mobile or not otp:
        return jsonify({'success': False, 'message': 'Mobile and OTP are required'}), 400
    ok, msg = verify_otp(mobile, otp, purpose)
    if not ok:
        return jsonify({'success': False, 'message': msg}), 400
    user = find_user_by_mobile(mobile)
    if not user:
        if purpose == 'signup':
            if not full_name:
                return jsonify({'success': False, 'message': 'Full name required for signup'}), 400
            email = data.get('email', '').strip()
            username = data.get('username', '').strip()
            if email and email_exists(email):
                return jsonify({'success': False, 'message': 'Email already registered'}), 400
            if username and username_exists(username):
                return jsonify({'success': False, 'message': 'Username already taken'}), 400
            user = create_user({
                'full_name': full_name,
                'username': username,
                'email': email,
                'mobile': mobile,
                'is_verified': True,
            })
        elif purpose == 'login':
            return jsonify({'success': False, 'message': 'No account found with this mobile number. Please sign up first.'}), 404
    update_user(user['_id'], {'is_verified': True, 'last_login': datetime.utcnow()})
    access_token = create_access_token(identity=user['_id'])
    refresh_token = create_refresh_token(identity=user['_id'])
    session['user_id'] = user['_id']
    session['user_name'] = user.get('full_name', 'User')
    session['user_email'] = user.get('email', '')
    remember = bool(data.get('remember'))
    if remember:
        session.permanent = True
    resp = make_response(jsonify({
        'success': True,
        'message': 'Mobile verified successfully',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {'id': user['_id'], 'name': user.get('full_name'), 'mobile': mobile},
        'redirect': '/dashboard'
    }))
    if remember:
        resp.set_cookie('refresh_token', refresh_token, httponly=True, secure=not current_app.config.get('DEBUG', True), samesite='Lax', max_age=30*24*3600)
    return resp


@auth_bp.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    if not is_valid_email(email):
        return jsonify({'success': False, 'message': 'Valid email required'}), 400
    user = find_user_by_email(email)
    if not user:
        return jsonify({'success': True, 'message': 'If this email is registered, you will receive a reset link'})
    reset_token = generate_otp(8)
    save_otp(email, reset_token, 'password_reset')
    return jsonify({'success': True, 'message': 'Password reset instructions sent', 'dev_token': reset_token})


@auth_bp.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    token = data.get('token', '').strip()
    new_password = data.get('new_password', '')
    if len(new_password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
    ok, msg = verify_otp(email, token, 'password_reset')
    if not ok:
        return jsonify({'success': False, 'message': msg}), 400
    user = find_user_by_email(email)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    update_user(user['_id'], {'password_hash': hash_password(new_password)})
    return jsonify({'success': True, 'message': 'Password reset successfully'})


@auth_bp.route('/api/auth/google', methods=['POST'])
def google_auth():
    data = request.get_json()
    google_token = data.get('token', '')
    if not google_token:
        return jsonify({'success': False, 'message': 'Google token required'}), 400
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests
        client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
        if not client_id:
            return jsonify({'success': False, 'message': 'Google OAuth not configured'}), 500
        idinfo = id_token.verify_oauth2_token(google_token, google_requests.Request(), client_id)
        google_id = idinfo['sub']
        email = idinfo.get('email', '')
        full_name = idinfo.get('name', '')
        avatar = idinfo.get('picture', '')
        from app.models.user import find_user_by_google_id
        user = find_user_by_google_id(google_id)
        if not user:
            user = find_user_by_email(email)
            if user:
                update_user(user['_id'], {'google_id': google_id, 'avatar': avatar})
            else:
                user = create_user({'full_name': full_name, 'email': email, 'google_id': google_id, 'avatar': avatar, 'is_verified': True})
        update_user(user['_id'], {'last_login': datetime.utcnow()})
        access_token = create_access_token(identity=user['_id'])
        session['user_id'] = user['_id']
        session['user_name'] = user.get('full_name', full_name)
        session['user_email'] = email
        return jsonify({'success': True, 'access_token': access_token, 'user': {'id': user['_id'], 'name': user.get('full_name')}, 'redirect': '/dashboard'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Google authentication failed: {str(e)}'}), 400


@auth_bp.route('/google_callback')
def google_callback():
    return render_template('google_callback.html')


@auth_bp.route('/api/auth/change-password', methods=['POST'])
def change_password():
    if not session.get('user_id'):
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    data = request.get_json()
    user = find_user_by_id(session['user_id'])
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if not check_password(data.get('current_password', ''), user.get('password_hash', '')):
        return jsonify({'success': False, 'message': 'Current password is incorrect'}), 400
    new_pass = data.get('new_password', '')
    if len(new_pass) < 6:
        return jsonify({'success': False, 'message': 'New password must be at least 6 characters'}), 400
    update_user(user['_id'], {'password_hash': hash_password(new_pass)})
    return jsonify({'success': True, 'message': 'Password changed successfully'})


@auth_bp.route('/logout')
def logout():
    session.clear()
    resp = make_response(redirect(url_for('auth.login_page')))
    resp.set_cookie('refresh_token', '', expires=0)
    return resp


@auth_bp.route('/api/auth/config')
def auth_config():
    # Expose minimal, non-sensitive auth config to frontend
    return jsonify({
        'google_client_id': Config.GOOGLE_CLIENT_ID or ''
    })


@auth_bp.route('/api/auth/silent-save-credential', methods=['POST'])
def silent_save_credential():
    # This endpoint accepts credential form posts from a hidden iframe to
    # trigger browser password-save prompts without performing any action.
    # Do not store or log credentials here.
    return ('', 204)


@auth_bp.route('/api/auth/refresh', methods=['POST'])
def refresh_token_route():
    # Read refresh token from secure cookie or request body
    token = request.cookies.get('refresh_token') or (request.get_json() or {}).get('refresh_token')
    if not token:
        return jsonify({'success': False, 'message': 'Refresh token missing'}), 401
    try:
        decoded = decode_token(token)
        # Ensure token is a refresh token
        if decoded.get('type') != 'refresh':
            return jsonify({'success': False, 'message': 'Invalid token type'}), 401
        identity = decoded.get('sub') or decoded.get('identity')
        access = create_access_token(identity=identity)
        return jsonify({'success': True, 'access_token': access})
    except Exception:
        return jsonify({'success': False, 'message': 'Refresh failed'}), 401


@auth_bp.route('/api/auth/me')
def me():
    if not session.get('user_id'):
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    user = find_user_by_id(session['user_id'])
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    user.pop('password_hash', None)
    return jsonify({'success': True, 'data': user})
