from flask import Blueprint, jsonify, request, session, make_response
from services.db_config import get_db_connection, login_required
import mysql.connector
import datetime

ticket_api_bp = Blueprint('ticket_api_bp', __name__)

# API 1: 起票データ一覧を取得 (GET /tickets)
@ticket_api_bp.route('/tickets', methods=['GET'])
@login_required
def get_tickets():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "データベース接続エラー"}), 500 # [cite: 9]
    
    # ... (get_tickets のロジック全体をコピー) ...
    cursor = conn.cursor(dictionary=True)
    sql = """
    SELECT 
        t.id, t.category, t.title, t.location, t.details, t.event_timestamp, t.status, 
        COALESCE(u.name, t.creator_name_display) AS creator_name,
        t.creator_name_display  
    FROM tickets t
    LEFT JOIN users u ON t.creator_user_id = u.id
    ORDER BY t.created_at DESC
    """ # [cite: 7]
    
    try:
        cursor.execute(sql)
        tickets_data = cursor.fetchall()
        for ticket in tickets_data:
            if ticket['event_timestamp']:
                ticket['event_timestamp'] = ticket['event_timestamp'].isoformat() # [cite: 8]
        return jsonify(tickets_data)
    except mysql.connector.Error as e:
        print(f"起票データ取得データベースエラー: {e}")
        return jsonify({"error": "データ取得中にデータベースエラーが発生しました"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close() # [cite: 9]


# API 2: 新しい起票を作成 (POST /tickets)
@ticket_api_bp.route('/tickets', methods=['POST'])
@login_required
def create_ticket():
    # ... (create_ticket のロジック全体をコピー) ...
    # API 4: EXCEL表ダウンロードのルート
    @ticket_api_bp.route('/excel')
    @login_required 
    def excel_download():
        # ... (excel_download のロジック全体をコピー) ...
        # (長いので省略しますが、元のコードのAPI 4をそのまま移動します)
        pass # [cite: 14, 15]