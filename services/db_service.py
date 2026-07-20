import mysql.connector
from contextlib import contextmanager
import datetime # ★追加: insert_detection_log が使用するため★
from typing import Optional # 型ヒント用に必要であれば追加
import json
from typing import Dict, List, Any, Tuple

# MySQL接続情報の設定
DB_CONFIG = {
    'host': 'localhost',
    'user': 'wp', 
    'password': 'wp', 
    'database': 'farm_management_db'
}

# DB接続関数 (Context Manager)
@contextmanager
def get_db_connection():
    """MySQLデータベースへの接続を確立し、with文で自動的にクローズする"""
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        # 接続オブジェクトを返す。カーソルは呼び出し側で dictionary=True を指定する
        yield conn
    except mysql.connector.Error as err:
        print(f"データベース接続エラー: {err}")
        # raise (Context Managerの外にエラーを伝播させる)
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()

# AI検出ログ挿入関数
def insert_detection_log(detection_data):
    """
    AI検出結果をデータベースのログテーブルに挿入する。
    """
    # ... (DB接続ロジック) ...
    
    try:
        # with get_db_connection() as conn: ... を使用する
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # detection_logs テーブルへの挿入 (users_service.py のDB構造に基づいた仮のテーブル)
            sql = """
            INSERT INTO detection_logs 
            (timestamp, disease_type, confidence, image_path, model_name)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            disease_type = detection_data.get('disease', 'Unknown')
            confidence = detection_data.get('confidence', 0.0)
            image_path = detection_data.get('src_path', '')
            model_name = detection_data.get('model', 'Integrated') # モデル名は 'Integrated' を使用
            
            cursor.execute(sql, (timestamp, disease_type, confidence, image_path, model_name))
            conn.commit()
            return True, "検出ログを正常に挿入しました。"
            
    except Exception as e:
        # ... (エラー処理) ...
        return False, f"DBエラー: {e}"        
        
    # 提供された insert_detection_log のロジック部分を再度埋め込みます (インポート不足解消版)
    conn = None
    try:
        conn = next(get_db_connection()) # Context Managerから接続を取得
        cursor = conn.cursor()
        
        sql = """INSERT INTO detection_logs (timestamp, disease_type, confidence, image_path, model_name)
                 VALUES (%s, %s, %s, %s, %s)"""
        
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        disease_type = detection_data.get('disease', 'Unknown')
        confidence = detection_data.get('confidence', 0.0)
        image_path = detection_data.get('src_path', '')
        model_name = detection_data.get('model', 'default')

        cursor.execute(sql, (timestamp, disease_type, confidence, image_path, model_name))
        conn.commit()
        return True, "検出ログを正常に挿入しました。"
        
    except mysql.connector.Error as e:
        if conn: conn.rollback()
        print(f"検出ログ挿入データベースエラー: {e}")
        return False, f"DBエラー: {e}"
        
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

    
def insert_individual_alert(detection_data: Dict[str, Any], image_path: str,location: str) -> Tuple[bool, str]:
    """
    単一の検出結果（all_detectionsリストの要素）を alerts テーブルに記録する。
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # --- 1. データの準備とマッピング ---
            disease_type = detection_data.get('disease', 'Unknown')
            confidence = detection_data.get('confidence', 0.0)
            
            # details カラムには、この検出結果（バウンディングボックス情報を含む）全体をJSON文字列として保存
            details_json = json.dumps(detection_data) 
            
            # disease/pest の文字列が含まれるかでフラグを判定
            is_pest_disease = 1 if "disease" in disease_type.lower() or "pest" in disease_type.lower() else 0
            
            # --- 2. SQLの実行 ---
            sql = """
            INSERT INTO alerts (timestamp, type, location, details, confidence, status, attachment_path, is_pest_disease)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
            """

            params = (
                datetime.datetime.now(),
                disease_type,
                location,  # 固定値または、必要に応じて引数から受け取る
                details_json,
                confidence,
                'pending',         # 対応状況の初期値
                image_path,
                1 if "disease" in detection_data.get('disease', '').lower() or "pest" in detection_data.get('disease', '').lower() else 0            )

            cursor.execute(sql, params)
            conn.commit()
            return True, f"alerts に '{disease_type}' を正常に記録。"
            
    except Exception as e:
        print(f"個別アラート挿入エラー: {e}")
        return False, f"DBエラーによりアラート記録に失敗しました: {e}"