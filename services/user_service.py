import bcrypt
import os
import binascii
import datetime
from typing import Optional, Dict, Any, Tuple
# db_serviceは同じパッケージ内にあると仮定
from .db_service import get_db_connection 

# ----------------------------------------------------
# 認証ユーティリティ
# ----------------------------------------------------

def hash_password(password: str) -> str:
    """
    平文パスワードをbcryptでハッシュ化する。
    DBに保存するため、バイト列からUTF-8文字列にデコードする。
    """
    # bcryptで安全にハッシュ化（saltも自動生成）
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password: str, hashed_password: str) -> bool:
    """
    平文パスワードとハッシュ値を比較する。
    ログイン失敗の主な原因がここでのエンコード不一致なので、両方を明示的にエンコード。
    """
    try:
        # 両方をバイト列にエンコードしてから比較する
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        # ハッシュ値が不正な形式の場合（DBから取得した値がおかしい場合）
        print("❌ パスワードハッシュが不正な形式です。")
        return False

# ----------------------------------------------------
# ユーザー登録・ログインサービス
# ----------------------------------------------------

def register_user(username: str, login_id: str, password: str) -> Tuple[bool, str]:
    """
    新しいユーザーを登録する。
    引数の順番: (表示名, ログインID, パスワード)
    """
    # 1. パスワードをハッシュ化
    hashed_pw = hash_password(password)

    # 2. 現在のタイムスタンプを生成 (NOT NULL制約対策)
    # NOTE: current_timeは未使用だが、コードのロジックとして残すことは問題ない
    current_time = datetime.datetime.now() 

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # 3. ログインIDの重複チェック
                sql_check = "SELECT id FROM users WHERE login_id = %s"
                cursor.execute(sql_check, (login_id,))
                if cursor.fetchone():
                    return False, "そのログインIDは既に使用されています。"
                
                # 4. 新しいユーザーをデータベースに挿入
                # カラム名: login_id, display_name, password_hash, created_at
                sql = """
                INSERT INTO users (login_id, display_name, password_hash, created_at) 
                VALUES (%s, %s, %s, NOW()) 
                """
                
                # ★修正箇所★: SQLにNOW()を使用しているため、
                # Python変数から current_time を削除し、パラメータ数を3つに修正。
                # 変数の内容: (ログインIDの値, 表示名の値, ハッシュ)
                # SQLの期待: (login_id, display_name, password_hash)
                # この順番で値を渡すことで、データが正しくマッピングされます。
                cursor.execute(sql, (login_id, username, hashed_pw)) 
                
                conn.commit()
            return True, "ユーザー登録が完了しました。ログインIDとパスワードでログインしてください。"
    
    except Exception as e:
        print(f"ユーザー登録エラー: {e}")
        return False, "データベースエラーにより登録に失敗しました。"
        
def authenticate_user(login_id: str, password: str) -> Optional[int]:
    """
    ログインIDと平文パスワードを受け取り、認証を行う。
    成功した場合は user_id を、失敗した場合は None を返す。
    """
    # ★防御的チェック: login_idが空の場合は処理を中断する (ui_routesで捕捉されるはずだが念のため)
    if not login_id:
        return None

    try:
        with get_db_connection() as conn:
            # 1. 辞書カーソルを使用するように明示的に指定
            with conn.cursor(dictionary=True) as cursor: 
                
                # 2. ログインIDでユーザーレコードを取得
                sql = "SELECT id, password_hash FROM users WHERE login_id = %s"
                cursor.execute(sql, (login_id,))
                user_record = cursor.fetchone() 
                
                if user_record is None:
                    # ユーザーが見つからない
                    print(f"認証失敗: ログインID '{login_id}' がDBで見つかりません。")
                    return None
                
                # 3. パスワードを比較
                hashed_password = user_record['password_hash']
                user_id = user_record['id']
                
                # check_password関数は、渡された値のエンコードも処理する
                if check_password(password, hashed_password):
                    # 認証成功
                    print(f"認証成功: User ID {user_id}")
                    return user_id
                else:
                    # パスワード不一致
                    print(f"認証失敗: パスワードが不一致です。")
                    return None
                    
    except Exception as e:
        # DBクエリ実行時など、予期せぬエラーが発生した場合
        print(f"認証処理中に予期せぬエラーが発生しました: {e}")
        return None
    
# ----------------------------------------------------
# セッショントークン管理サービス
# ----------------------------------------------------

def create_session(user_id: int) -> str:
    """
    認証成功後、新しいセッショントークンを生成し、DBに保存する。
    """
    # 32バイトのランダムなバイト列を生成し、16進数の文字列に変換
    token = binascii.hexlify(os.urandom(32)).decode('utf-8')
    # トークンの有効期限を24時間後に設定
    expires_at = datetime.datetime.now() + datetime.timedelta(days=1)

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # セッショントークンを sessions テーブルに挿入
                sql = "INSERT INTO sessions (session_token, user_id, expires_at) VALUES (%s, %s, %s)"
                cursor.execute(sql, (token, user_id, expires_at))
                conn.commit()
            return token
    except Exception as e:
        print(f"セッション作成エラー: {e}")
        # セッション作成失敗は致命的なので、エラーを再送出する
        raise

def get_user_by_session_token(token: str) -> Optional[Dict[str, Any]]:
    """
    セッショントークンを検証し、有効であればユーザー情報を返す。
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor: # 辞書カーソルを使用
                # トークンを検索し、有効期限が切れていないかチェック
                sql = """
                SELECT user_id 
                FROM sessions 
                WHERE session_token = %s AND expires_at > NOW()
                """
                cursor.execute(sql, (token,))
                session_record = cursor.fetchone()

                if session_record:
                    # トークンが有効であれば、user_idを返す
                    return {'user_id': session_record['user_id']}
                else:
                    return None # トークン無効または期限切れ
    except Exception as e:
        print(f"セッション検証エラー: {e}")
        return None

def delete_session(token: str) -> None:
    """
    ログアウト時にセッショントークンを削除する。
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                sql = "DELETE FROM sessions WHERE session_token = %s"
                cursor.execute(sql, (token,))
                conn.commit()
    except Exception as e:
        print(f"セッション削除エラー: {e}")
        pass