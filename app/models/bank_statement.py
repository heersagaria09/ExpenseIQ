from datetime import datetime
from app.config.database import get_collection
from bson import ObjectId


def save_statement(user_id, year, month, filename, file_path, file_type='pdf'):
    stmts = get_collection('bank_statements')
    existing = stmts.find_one({'user_id': user_id, 'year': year, 'month': month})
    stmt = {
        'user_id': user_id,
        'year': year,
        'month': month,
        'filename': filename,
        'file_path': file_path,
        'file_type': file_type,
        'transactions': [],
        'summary': {},
        'parsed': False,
        'uploaded_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
    }
    if existing:
        stmts.update_one({'_id': existing['_id']}, {'$set': stmt})
        stmt['_id'] = str(existing['_id'])
    else:
        result = stmts.insert_one(stmt)
        stmt['_id'] = str(result.inserted_id)
    return stmt


def get_statement(user_id, year, month):
    stmts = get_collection('bank_statements')
    doc = stmts.find_one({'user_id': user_id, 'year': year, 'month': month})
    if doc:
        doc['_id'] = str(doc['_id'])
    return doc


def get_all_statements(user_id):
    stmts = get_collection('bank_statements')
    cursor = stmts.find({'user_id': user_id}).sort([('year', -1), ('month', -1)])
    items = []
    for doc in cursor:
        doc['_id'] = str(doc['_id'])
        items.append(doc)
    return items


def update_statement_data(stmt_id, transactions, summary):
    stmts = get_collection('bank_statements')
    stmts.update_one({'_id': ObjectId(stmt_id)}, {
        '$set': {'transactions': transactions, 'summary': summary, 'parsed': True, 'updated_at': datetime.utcnow()}
    })


def delete_statement(stmt_id, user_id):
    stmts = get_collection('bank_statements')
    result = stmts.delete_one({'_id': ObjectId(stmt_id), 'user_id': user_id})
    return result.deleted_count > 0


def get_statement_by_id(stmt_id, user_id):
    stmts = get_collection('bank_statements')
    try:
        doc = stmts.find_one({'_id': ObjectId(stmt_id), 'user_id': user_id})
        if doc:
            doc['_id'] = str(doc['_id'])
        return doc
    except Exception:
        return None
