import os
from datetime import datetime
from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from app.models.bank_statement import (save_statement, get_statement, get_all_statements,
                                    update_statement_data, delete_statement, get_statement_by_id)
from app.models.expense import create_expense
from app.models.income import create_income
from app.models.notification import get_unread_count
from app.services.statement_parser import extract_text_from_pdf, parse_transactions_from_text, parse_csv_statement, auto_categorize_transaction
from app.utils.constants import MONTHS

statement_bp = Blueprint('statement', __name__)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated


@statement_bp.route('/bank-statements')
@login_required
def index():
    user_id = session['user_id']
    unread = get_unread_count(user_id)
    all_stmts = get_all_statements(user_id)
    stmt_map = {(s['year'], s['month']): s for s in all_stmts}
    now = datetime.utcnow()
    return render_template('bank_statements.html',
                           user_name=session.get('user_name', 'User'),
                           user_email=session.get('user_email', ''),
                           unread_count=unread,
                           statements=all_stmts,
                           stmt_map=stmt_map,
                           months=MONTHS,
                           current_year=now.year,
                           current_month=now.month,
                           years=list(range(now.year, now.year - 4, -1)))


@statement_bp.route('/api/statements/upload', methods=['POST'])
@login_required
def upload_statement():
    user_id = session['user_id']
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'}), 400
    file = request.files['file']
    year = int(request.form.get('year', datetime.utcnow().year))
    month = int(request.form.get('month', datetime.utcnow().month))
    password = request.form.get('password', '')
    if not file.filename:
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in ['pdf', 'csv', 'xlsx']:
        return jsonify({'success': False, 'message': 'Only PDF and CSV files allowed'}), 400
    upload_dir = os.path.join('static', 'uploads', 'statements', user_id)
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"stmt_{year}_{month:02d}_{int(datetime.utcnow().timestamp())}.{ext}"
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)
    stmt = save_statement(user_id, year, month, filename, file_path, ext)
    transactions = []
    summary = {}
    if ext == 'pdf':
        text, err = extract_text_from_pdf(file_path, password if password else None)
        if err:
            # Delete the uploaded file if parsing failed
            try:
                os.remove(file_path)
            except:
                pass
            return jsonify({'success': False, 'message': err}), 400
        if text:
            result = parse_transactions_from_text(text)
            transactions = result.get('transactions', [])
            summary = result.get('summary', {})
    elif ext in ['csv', 'xlsx']:
        result, err = parse_csv_statement(file_path)
        if result:
            transactions = result.get('transactions', [])
            summary = result.get('summary', {})
    for txn in transactions:
        txn['category'] = auto_categorize_transaction(txn.get('description', ''))
    if transactions:
        update_statement_data(stmt['_id'], transactions, summary)
        # Also save transactions to expenses/incomes collections for dashboard integration
        for txn in transactions:
            try:
                # Parse date from transaction
                txn_date = datetime.utcnow()
                if txn.get('date'):
                    try:
                        # Try to parse various date formats
                        date_str = str(txn['date'])
                        for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%d %b %Y', '%Y-%m-%d', '%d/%m/%y', '%d-%m-%y']:
                            try:
                                txn_date = datetime.strptime(date_str, fmt)
                                break
                            except:
                                continue
                    except:
                        pass
                
                if txn.get('type') == 'debit':
                    # Save as expense
                    create_expense(user_id, {
                        'title': txn.get('description', 'Bank Transaction')[:100],
                        'amount': txn.get('amount', 0),
                        'category': txn.get('category', 'Others'),
                        'date': txn_date,
                        'notes': f'Imported from bank statement - {MONTHS[month-1]} {year}',
                        'is_recurring': False,
                    })
                elif txn.get('type') == 'credit':
                    # Save as income
                    create_income(user_id, {
                        'title': txn.get('description', 'Bank Credit')[:100],
                        'amount': txn.get('amount', 0),
                        'source': txn.get('category', 'Bank'),
                        'date': txn_date,
                        'notes': f'Imported from bank statement - {MONTHS[month-1]} {year}',
                        'is_recurring': False,
                    })
            except Exception as e:
                # Continue with other transactions even if one fails
                pass
    return jsonify({'success': True, 'message': f'Statement uploaded for {MONTHS[month-1]} {year}. Transactions added to Dashboard.',
                    'data': {'stmt_id': stmt['_id'], 'transactions': len(transactions), 'summary': summary}})


@statement_bp.route('/api/statements/<year>/<month>')
@login_required
def get_stmt(year, month):
    user_id = session['user_id']
    stmt = get_statement(user_id, int(year), int(month))
    if not stmt:
        return jsonify({'success': False, 'message': 'No statement found'}), 404
    if isinstance(stmt.get('uploaded_at'), datetime):
        stmt['uploaded_str'] = stmt['uploaded_at'].strftime('%d %b %Y')
    return jsonify({'success': True, 'data': stmt})


@statement_bp.route('/api/statements/all')
@login_required
def list_statements():
    user_id = session['user_id']
    stmts = get_all_statements(user_id)
    for s in stmts:
        if isinstance(s.get('uploaded_at'), datetime):
            s['uploaded_str'] = s['uploaded_at'].strftime('%d %b %Y')
        s.pop('transactions', None)
    return jsonify({'success': True, 'data': stmts})


@statement_bp.route('/api/statements/<stmt_id>', methods=['DELETE'])
@login_required
def remove_statement(stmt_id):
    user_id = session['user_id']
    stmt = get_statement_by_id(stmt_id, user_id)
    if stmt and os.path.exists(stmt.get('file_path', '')):
        try:
            os.remove(stmt['file_path'])
        except Exception:
            pass
    if delete_statement(stmt_id, user_id):
        return jsonify({'success': True, 'message': 'Statement deleted'})
    return jsonify({'success': False, 'message': 'Statement not found'}), 404


@statement_bp.route('/api/statements/<stmt_id>/analyze', methods=['POST'])
@login_required
def analyze_statement(stmt_id):
    user_id = session['user_id']
    stmt = get_statement_by_id(stmt_id, user_id)
    if not stmt:
        return jsonify({'success': False, 'message': 'Statement not found'}), 404
    month_name = MONTHS[stmt.get('month', 1) - 1]
    file_path = stmt.get('file_path', '')
    if not os.path.exists(file_path):
        return jsonify({'success': False, 'message': 'Statement file not found'}), 404
    password = request.json.get('password', None) if request.is_json else None
    text, err = extract_text_from_pdf(file_path, password)
    if not text:
        return jsonify({'success': False, 'message': err or 'Could not read statement file'}), 400
    from app.services.gemini_service import analyze_bank_statement
    analysis, err = analyze_bank_statement(text, month_name)
    if err:
        return jsonify({'success': False, 'message': f'AI analysis failed: {err}'}), 503
    return jsonify({'success': True, 'data': {'analysis': analysis, 'month': month_name}})


