import os
import json
import atexit
import threading
from datetime import datetime

_client = None
_db = None
_using_mock = False
_save_lock = threading.Lock()

PERSIST_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
PERSIST_FILE = os.path.join(PERSIST_DIR, 'mockdb.json')


def _json_serial(obj):
    if isinstance(obj, datetime):
        return {'__datetime__': obj.isoformat()}
    raise TypeError(f'Not serializable: {type(obj)}')


def _json_deserial(dct):
    if '__datetime__' in dct:
        return datetime.fromisoformat(dct['__datetime__'])
    return dct


def save_mock_db():
    if not _using_mock or _db is None:
        return
    with _save_lock:
        try:
            os.makedirs(PERSIST_DIR, exist_ok=True)
            data = {}
            for col_name in _db.list_collection_names():
                docs = []
                for doc in _db[col_name].find({}):
                    doc['_id'] = str(doc['_id'])
                    docs.append(doc)
                data[col_name] = docs
            tmp = PERSIST_FILE + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(data, f, default=_json_serial, ensure_ascii=False)
            os.replace(tmp, PERSIST_FILE)
        except Exception as e:
            print(f'[WARN] Mock DB save error: {e}')


def _load_mock_db():
    if not os.path.exists(PERSIST_FILE):
        return
    try:
        with open(PERSIST_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f, object_hook=_json_deserial)
        from bson import ObjectId
        for col_name, docs in data.items():
            col = _db[col_name]
            for doc in docs:
                try:
                    doc['_id'] = ObjectId(doc['_id'])
                except Exception:
                    pass
                col.replace_one({'_id': doc['_id']}, doc, upsert=True)
        print(f'[OK] Mock DB loaded ({sum(len(v) for v in data.values())} documents)')
    except Exception as e:
        print(f'[WARN] Mock DB load error: {e}')


def _periodic_save(interval=30):
    def run():
        import time
        while _using_mock:
            time.sleep(interval)
            save_mock_db()
    t = threading.Thread(target=run, daemon=True)
    t.start()


def get_db():
    global _client, _db, _using_mock
    if _db is not None:
        return _db

    mongo_uri = os.environ.get('MONGO_URI', '').strip() or os.environ.get('MONGODB_URI', '').strip()

    if mongo_uri:
        try:
            import certifi
            from pymongo import MongoClient
            _client = MongoClient(
                mongo_uri,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=5000
            )
            _client.admin.command('ping')
            _db = _client[os.environ.get('DB_NAME', 'expenseiq')]
            print('[OK] MongoDB connected successfully')
            return _db
        except Exception as e:
            print(f'[WARN] MongoDB connection failed: {e}')

    try:
        import mongomock
        _client = mongomock.MongoClient()
        _db = _client['expenseiq']
        _using_mock = True
        _load_mock_db()
        atexit.register(save_mock_db)
        _periodic_save(30)
        print('[INFO] Using local file-backed database (set MONGO_URI or MONGODB_URI for cloud storage)')
    except ImportError:
        raise RuntimeError('No database available. Run: pip install mongomock')

    return _db


def get_collection(name):
    return get_db()[name]
