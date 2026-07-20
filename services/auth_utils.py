# services/auth_utils.py (修正案)

from functools import wraps
from flask import session, redirect, url_for, request, jsonify, g
# .user_service から get_user_by_session_token をインポート
from .user_service import get_user_by_session_token 


# ----------------------------------------------------
# 認証デコレータ
# ----------------------------------------------------

def login_required(f):
    """
    UI画面用のセッションベース認証デコレータ。
    未ログインならログインページ('auth_bp.index')へリダイレクトする。
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Flaskセッションに 'user_id' が存在するかチェック
        if 'user_id' not in session:
            # ログイン状態が解除されていたら、ログインページへリダイレクト
            # Blueprint名 'auth_bp' を使ってリダイレクト
            return redirect(url_for('auth_bp.index')) 
        
        # 認証成功
        return f(*args, **kwargs)
    return decorated_function

def auth_api_required(f):
    """
    APIリクエスト用のトークンベース認証デコレータ。
    トークンが無効なら401エラーを返す。
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Authorizationヘッダーからトークンを取得
        auth_header = request.headers.get('Authorization')
        token = None
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({"error": "認証が必要です。", "reason": "Token not provided"}), 401

        # ユーザーサービスの関数を使ってトークンを検証
        user_info = get_user_by_session_token(token)

        if user_info is None:
            return jsonify({"error": "認証に失敗しました。", "reason": "Invalid or expired token"}), 401
        
        # 認証成功: ユーザーIDとトークンをgに格納
        g.user_id = user_info['user_id']
        g.token = token 
        
        return f(*args, **kwargs)
    return decorated_function

def load_user_id_from_session():
    """
    FlaskセッションからユーザーIDをロードする。
    セッションが存在しない場合はNoneを返す。
    """
    # UIのログイン時に session['user_id'] に格納した値を返す
    return session.get('user_id', None)