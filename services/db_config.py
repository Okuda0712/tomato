import mysql.connector
from flask import redirect, url_for, session, request
from functools import wraps

# MySQL接続情報の設定
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root', 
    'password': '', # パスワードを設定
    'database': 'farm_management_db'
} # [cite: 2]

# DB接続関数
def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"データベース接続エラー: {err} [cite: 3]")
        return None

# ログインチェックデコレーター
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # ログイン状態が解除されていたら、ログインページへリダイレクト
            return redirect(url_for('ui_bp.index', next=request.url)) # ★Blueprint名を使用
        return f(*args, **kwargs)
    return decorated_function # [cite: 4]