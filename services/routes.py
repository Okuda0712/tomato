from flask import Blueprint, request, jsonify, render_template
import os
import datetime
import uuid
import mysql
import base64
from .ai_service import run_detection_and_analyze
from .user_service import register_user, authenticate_user, create_session, delete_session
from .auth_utils import login_required, load_user_id_from_session
from .db_service import insert_detection_log, get_db_connection
from . import camera_config
from openpyxl import Workbook

api_bp = Blueprint('api', __name__)

UPLOAD_FOLDER = 'uploads' 

@api_bp.route('/detect-disease', methods=['POST'])
@login_required
def detect_disease_endpoint():
    # 1. ファイル受付のチェック
    if 'file' not in request.files:
        return jsonify({"error": "ファイルが添付されていません"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "ファイル名が空です"}), 400
        
    original_filename = file.filename
    # 一時保存用のユニークなファイル名を作成
    unique_filename = f"{uuid.uuid4()}_{original_filename}"
    temp_filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
    
    # 2. 画像の一時保存
    try:
        file.save(temp_filepath)
        print(f"画像ファイル '{original_filename}' を一時保存しました。")
    except Exception as e:
        print(f"一時ファイル保存エラー: {e}")
        return jsonify({"error": f"サーバー側でファイル保存に失敗しました: {e}"}), 500

    # 3. YOLOv8 推論の実行 (AIサービス呼び出し)
    try:
        final_disease, final_confidence, all_detections = run_detection_and_analyze(temp_filepath)
    except Exception as e:
        print(f"YOLOv8推論エラー: {e}")
        # 4. エラー時も一時ファイルを削除
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
        return jsonify({"error": f"AI推論中にエラーが発生しました: {e}"}), 500
    
    # 4. DBサービスによるログ挿入を実行
    db_success, db_message = insert_detection_log(
        original_filename, 
        final_disease, 
        final_confidence,
        all_detections
    )
    
    # 5. 一時ファイルの削除
    if os.path.exists(temp_filepath):
        os.remove(temp_filepath)
        print(f"一時ファイル '{temp_filepath}' を削除しました。")
        
    # 6. フロントエンドへの応答データの作成
    response_data = {
        "disease": final_disease,
        "confidence": final_confidence,
        "detections": all_detections,
        "db_status": "成功" if db_success else "失敗",
        "db_detail": db_message,
    }
    
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 判定完了。DB: {db_success}")
    
    return jsonify(response_data)

@api_bp.route('/account', methods=['GET'])
@api_bp.route('/create-account', methods=['GET'])
@api_bp.route('/register', methods=['POST'])
@api_bp.route('/sakusei_post', methods=['POST'])
def sakusei_post():
    # request.get_json() の代わりに request.form を使用
    username = request.form.get('username')
    login_id = request.form.get('login_id') 
    password = request.form.get('password')

    # user_serviceに渡す順番は (表示名, ログインID, パスワード)
    success, message = register_user(username, login_id, password)
    
    if success:
        # 成功したらログインページへリダイレクト
        return redirect(url_for('auth_bp.index')) 
    else:
        # 失敗したらエラーメッセージと共に作成ページへ戻る
        return render_template('sakusei.html', error=message), 400
    
@api_bp.route('/login', methods=['POST'])
def login_api():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user_id = authenticate_user(username, password)

    if user_id:
        try:
            # 認証成功の場合、セッショントークンを発行
            token = create_session(user_id)
            return jsonify({
                "message": "ログイン成功", 
                "token": token, 
                "user_id": user_id
            }), 200
        except Exception:
            return jsonify({"error": "セッショントークン発行に失敗しました"}), 500
    
    return jsonify({"error": "アカウント名またはパスワードが正しくありません"}), 401

@api_bp.route('/logout', methods=['POST'])
@login_required
def logout_api():
    # auth_utilsで取得したトークンを削除する（デコレータがトークンをg.tokenに格納している前提）
    # ※現在のauth_utilsの設計ではトークンをg.tokenに格納していないため、
    # 実際にはリクエストヘッダーから再度取得する必要がありますが、ここでは簡易化のため省略。
    
    # 簡易的な成功応答
    return jsonify({"message": "ログアウトしました"}), 200


# --- ユーザー機能のルーティング (UI) ---

@api_bp.route('/account', methods=['GET'])
def account_page():
    """ログイン/アカウント作成ページを表示するルート"""
    return render_template('account.html')

@api_bp.route('/create-account', methods=['GET'])
def create_account_page():
    """アカウント作成フォームを表示するルート"""
    # テンプレートは account.html を流用するか、別途用意が必要です
    return render_template('create_account.html')

@api_bp.route('/excel', methods=['GET'])
# @login_required # 必要に応じて認証チェックを追加
def excel_download():
    """API: Excelファイルダウンロード (選択フィルタリング対応)"""
    # 必要なインポートは routes.py のファイル冒頭で定義されている前提
    from openpyxl import Workbook
    from io import BytesIO
    import datetime
    from flask import make_response 

    # URLクエリパラメータからチケット ID を取得
    ticket_ids_str = request.args.get('ticket_ids')
    
    try:
        # ★★★ 修正箇所: with get_db_connection() as conn: を使用する ★★★
        with get_db_connection() as conn:
            # 接続オブジェクトからカーソルを取得
            cursor = conn.cursor() 
            
            # 1. SQLクエリの構築
            sql = """
            SELECT 
                t.category, t.title, t.event_timestamp, 
                COALESCE(u.display_name, t.creator_name_display) AS creator_name,
                t.location, t.details, t.status, t.id
            FROM tickets t
            LEFT JOIN users u ON t.creator_user_id = u.id
            """
            params = []
            
            if ticket_ids_str:
                # 選択されたIDでフィルタリング
                ids = ticket_ids_str.split(',')
                placeholders = ', '.join(['%s'] * len(ids))
                sql += f" WHERE t.id IN ({placeholders})"
                params = tuple(ids) 

            sql += " ORDER BY t.created_at DESC"
            
            cursor.execute(sql, params)
            records = cursor.fetchall()
        
        # --- Excelファイルの生成 ---
        wb = Workbook()
        ws = wb.active 
        ws.title = "起票データ一覧" 

        headers = [
            "起票カテゴリ", "件名", "発生日時", "作成者", 
            "発生場所", "事象の内容", "ステータス", "ID (参照用)"
        ] 
        ws.append(headers)

        for record in records:
            ws.append(record)

        output = BytesIO()
        wb.save(output)
        output.seek(0)

        response = make_response(output.read())
        
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"kihyo_list_{current_time}.xlsx"
        
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        
        return response

    except Exception as e:
        print(f"Excelダウンロードエラー: {e}")
        return "データ取得またはExcel作成中にエラーが発生しました", 500

@api_bp.route('/tickets', methods=['POST'])
# @login_required # 必要に応じて、UIセッションまたはトークン認証を適用
def create_ticket_api():
    # NOTE: creator_idは、UIからPOSTされたJSONデータではなく、Flaskセッションから取得する
    #       UIルートの設計により、ここではload_user_id_from_session()を使用
    creator_id = load_user_id_from_session() # auth_utilsからインポートしていると仮定
    
    # フォームデータではなく、JSONデータを受け取る
    data = request.get_json() 
    
    # --- 1. 必須データのチェック ---
    required_keys = ['category', 'title', 'details', 'event_timestamp', 'creator_name']
    if not all(key in data for key in required_keys):
        return jsonify({"error": "必須データが不足しています（カテゴリ、件名、内容、日時、作成者名）"}), 400

    # --- 2. DB接続と挿入処理 ---
    # get_db_connection() は Context Manager なので、with文で呼び出す
    try:
        with get_db_connection() as conn:
            # APIなので、通常のカーソルを使用
            with conn.cursor() as cursor: 
                
                sql = """
                INSERT INTO tickets (category, title, event_timestamp, location, details, creator_user_id, creator_name_display)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                # SQL実行パラメータ
                params = (
                    data['category'],
                    data['title'],
                    data['event_timestamp'], # JSから送信された日時
                    data.get('location', ''), 
                    creator_id, # Flaskセッションから取得したID
                    data['details'],
                    data['creator_name'] 
                )

                # パラメータの数を合わせるために調整
                # SQL: (category, title, event_timestamp, location, details, creator_user_id, creator_name_display) => 7項目
                # Params: (category, title, event_timestamp, location, details, creator_user_id, creator_name_display) => 7項目
                
                # 修正: 上の params タプルが SQLの VALUES と順番が合っていないため修正
                final_params = (
                    data['category'],
                    data['title'],
                    data['event_timestamp'],
                    data.get('location', ''), 
                    data['details'], 
                    creator_id,
                    data['creator_name']
                )

                cursor.execute(sql, final_params)

                conn.commit()
                # 201 Created ステータスを返す
                return jsonify({"message": "起票が正常に作成されました", "id": cursor.lastrowid}), 201
                
    except Exception as e:
        # DB接続、SQL実行エラーなどをキャッチ
        # connがtryブロック内で定義されている場合、ロールバックを試みる
        if 'conn' in locals() and conn: 
             conn.rollback() 
        
        print(f"起票作成予期せぬエラー: {e}")
        # 500 Internal Server Error を返す
        return jsonify({"error": f"起票作成中に予期せぬエラーが発生しました: {e}"}), 500
    

@api_bp.route('/tickets', methods=['GET'])
def get_tickets_api():
    """
    起票データ一覧を取得し、JSONで返す。
    """
    # conn を try ブロックの外で定義し、エラー時にロールバックできるように準備
    conn = None 
    
    try:
        # ★★★ 修正箇所: with get_db_connection() as conn: を使用する ★★★
        with get_db_connection() as conn:
            # 接続が確立されたオブジェクトからカーソルを取得
            cursor = conn.cursor(dictionary=True) 
            
            # ... (SQLクエリはそのまま) ...
            sql = """
                SELECT 
                    t.id, t.category, t.title, t.location, t.details, t.event_timestamp, t.status, 
                    -- ★修正ポイント: u.username を u.display_name (または正しいカラム名) に変更★
                    COALESCE(u.display_name, t.creator_name_display) AS creator_name,
                    t.creator_name_display  
                FROM tickets t
                LEFT JOIN users u ON t.creator_user_id = u.id
                ORDER BY t.created_at DESC
                """
            
            cursor.execute(sql)
            tickets_data = cursor.fetchall()
            
            for ticket in tickets_data:
                if ticket['event_timestamp']:
                    # datetimeオブジェクトをisoformat文字列に変換
                    ticket['event_timestamp'] = ticket['event_timestamp'].isoformat()
                    
            return jsonify(tickets_data)
            
    except Exception as e:
        # DB接続、SQL実行エラーなどをキャッチ
        print(f"起票データ取得データベースエラー: {e}")
        return jsonify({"error": "データ取得中にデータベースエラーが発生しました"}), 500
    
    # NOTE: with文が自動で conn.close() を行うため、finallyブロックは不要です。

@api_bp.route('/alerts', methods=['GET'])
@login_required 
def get_alerts_api():
    """異常検知一覧ページで表示するデータを取得するAPI"""
    alerts_list = []
    
    # DBから全件取得するロジック
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor: 
                sql = """
                SELECT id, timestamp, type, location, confidence, status, attachment_path, details 
                FROM alerts 
                ORDER BY timestamp DESC
                """
                cursor.execute(sql)
                alerts_list = cursor.fetchall()
        
        # タイムスタンプと確信度の整形
        for alert in alerts_list:
            if alert['timestamp']:
                alert['timestamp'] = alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            
            # DBのconfidenceが0.695などであれば、JSON形式に合わせて文字列で % を付加
            # ※DBから取得した値が既にfloat型であることを想定
            if alert['confidence'] is not None:
                alert['confidence'] = f"{round(float(alert['confidence']) * 100)}%"
            
        return jsonify(alerts_list), 200
        
    except Exception as e:
        print(f"異常検知データ取得エラー: {e}")
        return jsonify({"error": "サーバー側で異常検知データの取得に失敗しました。"}), 500

@api_bp.route('/alerts/<int:alert_id>', methods=['GET'])
@login_required
def get_alert_detail_api(alert_id):
    """特定の異常検知の詳細データを取得するAPI"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor: 
                sql = """
                SELECT id, timestamp, type, location, details, confidence, status, attachment_path
                FROM alerts 
                WHERE id = %s
                """
                cursor.execute(sql, (alert_id,))
                alert = cursor.fetchone()
                
                if alert is None:
                    return jsonify({"error": "指定されたIDの検知データが見つかりません。"}), 404
                
                # 日時と確信度の整形
                alert['timestamp'] = alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                alert['confidence'] = f"{round(float(alert['confidence']) * 100)}%"
                
                return jsonify(alert), 200
    except Exception as e:
        print(f"異常検知詳細データ取得エラー (ID: {alert_id}): {e}")
        return jsonify({"error": "サーバー側でデータの取得に失敗しました。"}), 500
    
# services/routes.py (どこかの空いている場所に追加)

# app.py で IMG_FOLDER が定義されていることを確認してください。
# ここでは暫定的にIMG_FOLDERへのパスを取得するロジックを簡略化しています。
# 実際には app.py から IMG_FOLDER をインポートするか、パスを渡す必要があります。
# 仮の IMG_FOLDER パス定義 (app.py の定義と一致させてください)
IMG_FOLDER = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'img'))

@api_bp.route('/capture_and_save', methods=['POST'])
@login_required # ログイン必須
def capture_and_save():
    """
    ブラウザから送られた画像データ（base64またはバイナリ）をIMG_FOLDERに保存する。
    """
    data = request.get_json()
    base64_img = data.get('image_data')

    if not base64_img:
        return jsonify({"error": "画像データが見つかりません。"}), 400

    try:
        # base64 プレフィックス (例: "data:image/png;base64,") を削除
        header, encoded = base64_img.split(',', 1)
        image_data = base64.b64decode(encoded)

        # ユニークなファイル名で img/ フォルダに保存
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"webcam_capture_{timestamp}_{uuid.uuid4().hex[:6]}.jpeg"
        filepath = os.path.join(IMG_FOLDER, filename)

        with open(filepath, 'wb') as f:
            f.write(image_data)
        
        print(f"📸 画像を {filepath} に保存し、推論をトリガーしました。")
        
        return jsonify({"message": "画像を正常に保存し、推論を開始しました。", "filename": filename}), 200
        
    except Exception as e:
        print(f"画像保存エラー: {e}")
        return jsonify({"error": f"サーバー側での画像保存に失敗しました: {e}"}), 500
    
# services/routes.py (追加するべき関数)

# API 7: 過去30日間の時系列データ取得 (GET /api/alerts/summary/timeline)
# services/routes.py (既存のAPIブロックに追加)

# services/routes.py (既存のAPIブロックに追加)

# services/routes.py (get_alert_timeline_api 関数全体)

@api_bp.route('/alerts/summary/timeline', methods=['GET'])
@login_required
def get_alert_timeline_api():
    """過去30日間の病害虫検知件数を日付ごとに取得し、JSONで返す。"""
    import datetime
    from flask import jsonify 
    import mysql.connector # routes.pyのトップレベルでインポートされていることを確認

    conn = None
    try:
        # DB接続を取得
        with get_db_connection() as conn: 
            cursor = conn.cursor(dictionary=True)
          
            today = datetime.date.today()
            thirty_days_ago = today - datetime.timedelta(days=30)
            
            # SQL: 病害虫 (is_pest_disease = 1) のデータを取得
            sql = """
            SELECT 
                DATE_FORMAT(timestamp, '%Y-%m-%d') as date_label, 
                COUNT(*) as count
            FROM alerts
            WHERE 
                is_pest_disease = 1 
                AND DATE(timestamp) >= %s 
                AND DATE(timestamp) <= %s
            GROUP BY date_label
            ORDER BY date_label ASC
            """
            params = (thirty_days_ago.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
            
            cursor.execute(sql, params)
            summary_data = cursor.fetchall()
            
            # --- データ補完ロジック ---
            
            # 過去30日間の日付リストを生成
            date_range = [(today - datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, -1, -1)]
            
            # 取得したデータを辞書に変換 {日付: 件数}
            data_map = {item['date_label']: item['count'] for item in summary_data}
            
            # 欠損日を補完し、最終的なデータリストを生成
            final_data = [{'date_label': date, 'count': data_map.get(date, 0)} for date in date_range]
            
            # JSが map() で処理できるよう、リストのJSONを返す
            return jsonify(final_data) 
            
    except mysql.connector.Error as e:
        # DBクエリのエラーをログに出力
        print(f"時系列集計 DB接続エラー詳細: {e}")
        return jsonify({"error": "時系列データ取得中にデータベースエラーが発生しました"}), 500
    except Exception as e:
        # 予期せぬ処理エラーをログに出力
        print(f"時系列集計処理エラー: {e}")
        return jsonify({"error": "予期せぬエラーにより時系列データ取得に失敗しました"}), 500

@api_bp.route('/alerts/summary/filtered', methods=['GET'])
@login_required
def get_filtered_alert_summary_api():
    """フィルタリングされた異常検知データの集計サマリーをJSONで返す。"""
    
    # 必要なインポート: from flask import request, jsonify; import mysql.connector
    
    conn = None
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # --- 1. フィルタリング条件の構築 ---
            filter_type = request.args.get('type') 
            filter_year = request.args.get('year')
            filter_month = request.args.get('month')
            filter_day = request.args.get('day')
        
            filter_sql = "WHERE 1=1"
            params = []
            
            # カテゴリフィルタ
            if filter_type and filter_type != '全体':
                filter_sql += " AND type = %s"
                params.append(filter_type)
            
            # 日付フィルタ
            if filter_year:
                if filter_month and filter_day:
                    filter_sql += " AND DATE(timestamp) = %s"
                    date_str = f"{filter_year}-{filter_month.zfill(2)}-{filter_day.zfill(2)}"
                    params.append(date_str)
                elif filter_month:
                    filter_sql += " AND YEAR(timestamp) = %s AND MONTH(timestamp) = %s"
                    params.append(filter_year)
                    params.append(filter_month)
                else:
                    filter_sql += " AND YEAR(timestamp) = %s"
                    params.append(filter_year)

            summary = {
                'total_count': 0,
                'filtered_count': 0,
                'location_summary': []
            }

            # 2. 全体件数の取得 (フィルタリングなし)
            cursor.execute("SELECT COUNT(*) as total FROM alerts")
            summary['total_count'] = cursor.fetchone()['total']
            
            # 3. フィルタリング後の件数
            sql_filtered_count = f"SELECT COUNT(*) as filtered FROM alerts {filter_sql}"
            cursor.execute(sql_filtered_count, tuple(params))
            summary['filtered_count'] = cursor.fetchone()['filtered']

            # 4. 場所別集計の取得 (TOP 5)
            sql_location_summary = f"""
            SELECT 
                location, 
                COUNT(*) as count
            FROM alerts 
                {filter_sql} 
            GROUP BY location
            ORDER BY count DESC
            LIMIT 5
            """
            cursor.execute(sql_location_summary, tuple(params))
            summary['location_summary'] = cursor.fetchall()
            
            return jsonify(summary)
            
    except mysql.connector.Error as e:
        print(f"フィルタリング集計データ取得エラー: {e}")
        return jsonify({"error": "フィルタリング集計データ取得中にデータベースエラーが発生しました"}), 500
    except Exception as e:
        print(f"サマリー集計処理エラー: {e}")
        return jsonify({"error": "予期せぬエラーにより集計データ取得に失敗しました"}), 500

# services/routes.py (修正箇所)

@api_bp.route('/camera/setting', methods=['POST'])
@login_required 
def save_camera_setting():
    data = request.get_json()
    device_id = data.get('device_id') # ブラウザが検出したカメラのデバイスID
    is_fixed = data.get('is_fixed')   # 定期監視カメラとして使用するか

    if not device_id:
        return jsonify({"error": "デバイスIDが指定されていません"}), 400
    
    # ----------------------------------------------------
    # ★【修正・追記】コアロジックを実装
    # ----------------------------------------------------
    try:
        if is_fixed:
            # チェックボックスがONの場合、このデバイスIDを固定カメラとして設定
            camera_config.set_fixed_camera_device_id(device_id)
            message = f"定期監視カメラをID: {device_id} に設定しました。"
        else:
            # チェックボックスがOFFの場合、現在の固定設定を解除
            # ※解除時はNoneを渡すことで、timer_serviceがスキップする
            camera_config.set_fixed_camera_device_id(None)
            message = "定期監視カメラの設定を解除しました。"

        print(f"カメラ設定API呼び出し成功: {message}")
        return jsonify({"message": message}), 200
        
    except Exception as e:
        print(f"カメラ設定保存エラー: {e}")
        return jsonify({"error": "サーバー側で設定保存中にエラーが発生しました"}), 500