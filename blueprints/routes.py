# services/routes.py トップ付近のインポート文
from flask import Blueprint, request, jsonify, render_template # render_templateを維持
import os
import datetime
import uuid
# AI/DBサービスを相対インポート
from .ai_service import run_detection_and_analyze
from .db_service import insert_detection_log
# ★ 新規追加・修正: 認証に必要なモジュール ★
from .user_service import register_user, authenticate_user, create_session, delete_session
from .auth_utils import login_required, load_user_id_from_session

from .ai_service import run_detection_and_analyze
from .db_service import insert_detection_log, get_db_connection

# Blueprintの定義
api_bp = Blueprint('api', __name__)

# --- 設定 ---
# UPLOAD_FOLDERは app.py 側で作成済み
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
# services/routes.py の register_user_api 関数を修正

@api_bp.route('/register', methods=['POST'])
def register_user_api():
    data = request.get_json()
    
    # ★修正点 1: login_id の取得を追加する
    username = data.get('username')
    login_id = data.get('login_id') # ★追加: ログインIDを取得
    password = data.get('password')

    # ★修正点 2: user_service に3つの引数を正しい順番で渡す
    # 順番: (表示名, ログインID, パスワード)
    success, message = register_user(username, login_id, password) 
    if success:
        return jsonify({"message": message}), 201
    return jsonify({"error": message}), 400

#----------------------------------------------------
# ログインAPIも login_id を使うように修正
#----------------------------------------------------

@api_bp.route('/login', methods=['POST'])
def login_api():
    data = request.get_json()
    # ★修正点: login_id を取得し、authenticate_user に渡す
    login_id = data.get('login_id') 
    password = data.get('password')

    # authenticate_user の引数順: (ログインID, パスワード)
    user_id = authenticate_user(login_id, password) 

    if user_id:
        # ... (セッショントークン発行ロジックは省略) ...
        # return jsonify(...)
        pass # 仮
    
    return jsonify({"error": "ログインIDまたはパスワードが正しくありません"}), 401

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
    """
    API 4: EXCEL表ダウンロードのルート (/api/excel)
    NOTE: DB接続ロジック（get_db_connection）が必要です。
    """
    # ★★★ 修正箇所: DB接続、データ取得、Excel生成ロジックが必要 ★★★

    conn = get_db_connection() # db_serviceからインポートされていると仮定
    if conn is None:
        return "データベース接続エラー", 500

    cursor = conn.cursor()
    # 仮のSQL: ticketsテーブルからデータを取得
    sql = "SELECT id, category, title, event_timestamp, location, details, status, creator_name_display FROM tickets ORDER BY created_at DESC"
    
    try:
        cursor.execute(sql)
        records = cursor.fetchall()
        
        wb = Workbook()
        ws = wb.active 
        ws.title = "起票データ一覧" 

        headers = ["ID", "カテゴリ", "件名", "発生日時", "発生場所", "事象の内容", "ステータス", "作成者"] 
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
        
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# ※注意: Openpyxlやdatetime、get_db_connectionのインポートが必要です。

@api_bp.route('/tickets', methods=['POST'])
# @login_required # 必要に応じて、UIセッションまたはトークン認証を適用
def create_ticket_api():
    # ユーザーがログインしている前提で、セッションからユーザーIDを取得
    # NOTE: UIから呼ばれるため、FlaskセッションからユーザーIDを取得する必要があります
    creator_id = load_user_id_from_session() # auth_utilsからインポートしていると仮定
    
    data = request.get_json() # JavaScriptから送信されたJSONデータを受け取る
    
    # 必須データのチェック
    if not all(key in data for key in ['category', 'title', 'details', 'event_timestamp', 'creator_name']):
        return jsonify({"error": "必須データが不足しています（カテゴリ、件名、内容、日時、作成者名）"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "サーバー接続エラー: データベースに接続できませんでした"}), 500

    cursor = conn.cursor()
    
    sql = """
    INSERT INTO tickets (category, title, event_timestamp, location, details, creator_user_id, creator_name_display)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    try:
        # datetimeオブジェクトに変換 (必要に応じて)
        # JSから送信された event_timestamp をそのまま使用するか、DBが要求する形式に変換
        
        cursor.execute(sql, (
            data['category'],
            data['title'],
            data['event_timestamp'], # 日時形式が正しくないとDBエラーになる可能性あり
            data.get('location', ''), 
            data['details'],
            creator_id, # Flaskセッションから取得したID
            data['creator_name'] 
        ))

        conn.commit()
        return jsonify({"message": "起票が正常に作成されました", "id": cursor.lastrowid}), 201
        
    except Exception as e:
        conn.rollback()
        print(f"起票作成予期せぬエラー: {e}")
        return jsonify({"error": f"起票作成中に予期せぬエラーが発生しました: {e}"}), 500
        
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

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