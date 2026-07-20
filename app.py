# app.py (修正後)

import os
import threading
import time 
import shutil # ★追加: ファイルの移動用★
import json # ★追加: DBにJSONを保存するため★
from services.timer_service import start_capture_timer
from watchdog.observers import Observer 
from watchdog.events import FileSystemEventHandler 

from flask import Flask # ★★★ この行が不足していました ★★★
from blueprints.auth_routes import auth_bp # ★この行が必須★
from blueprints.ui_routes import ui_bp
from services.routes import api_bp
# ... 既存のインポート ...
from services.ai_service import load_models, run_detection_and_analyze 
from services.db_service import insert_individual_alert # ★この行を修正/追加★

# AIサービス、モデルロード関数をインポート
#from services.ai_service import load_models, run_detection_and_analyze 

IMG_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img'))

# Flaskアプリケーションの初期化 (これで NameError が解消される)
app = Flask(__name__, static_folder='static')

app.secret_key = 'your_very_secret_key_for_farm_app_2025'

# 1. 認証/ログインルートの登録 (これがメインの '/' ルートになります)
app.register_blueprint(auth_bp, url_prefix='/') 

# 2. 認証後UIルートの登録 
app.register_blueprint(ui_bp, url_prefix='/') 

# 3. APIルートの登録 
app.register_blueprint(api_bp, url_prefix='/api')

# --- AIモデルの初期ロード (サーバー起動時に実行) ---
try:
    load_models() 
except ConnectionError as e:
    print(f"致命的エラー: AIモデルロード失敗: {e}")
except Exception as e:
    print(f"致命的エラー: AIモデルロード中に予期せぬエラー: {e}")

# ... (Blueprint登録はそのまま) ...

STATIC_ALERTS_DIR = os.path.join(app.root_path, 'static', 'alerts')
if not os.path.exists(STATIC_ALERTS_DIR):
    os.makedirs(STATIC_ALERTS_DIR)


# --- ファイル監視ロジック (ImageHandlerとstart_file_watcher) ---

class ImageHandler(FileSystemEventHandler):
    """ファイルがimgフォルダに追加されたときに実行されるハンドラ"""
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            time.sleep(2)
            print(f"新しくファイルが追加されました: {event.src_path}")
            
            temp_filepath = event.src_path # 処理対象のオリジナルパス
            web_path = None
            
            try:
                camera_id = "Camera_01"
                location_info = "ハウスA-エリア1"
                
                # 1. AI推論の実行
                final_disease, final_confidence, all_detections = run_detection_and_analyze(temp_filepath)
                print(f"推論結果概要: {final_disease}, 確信度: {final_confidence}, 総検出数: {len(all_detections)}")
                
                # --- ★★★ ここから変更 ★★★ ---
                
                # 2. 確信度チェック: 75% (0.75)以上の場合のみ処理を続行
                if final_confidence >= 0.75 and all_detections:
                    
                    print(f"✅ 確信度が75%以上の検出結果を確認しました ({final_confidence:.2f})。ファイルを保存し、DBに登録します。")
                    
                    # ファイル名の設定
                    filename = os.path.basename(temp_filepath)
                    final_dest_path = os.path.join(STATIC_ALERTS_DIR, filename)
                    web_path = f"/static/alerts/{filename}"

                    try:
                        shutil.copy(temp_filepath, final_dest_path) 
                        print(f"✅ 画像を公開フォルダへコピーしました: {web_path}")
                    except Exception as e:
                        print(f"❌ 画像ファイルコピーエラー: {e}")
                        web_path = None 
                    
                    for detection in all_detections:
                        
                        # --- ★★★ ここが重要: 個別検出結果のフィルタリング ★★★
                        detection_confidence = detection.get('confidence', 0.0) # 確信度を取得
                        
                        if detection_confidence < 0.75:
                            print(f"   ⚠️ 個別の確信度が75%未満 ({detection_confidence:.2f}) のため、このアラートはDB登録をスキップします。")
                            continue # 次の detection へ
                        # --- ★★★ 修正終了 ★★★

                        detection_summary = {
                            # ... (省略: detection_summaryの構築) ...
                        }
                        
                        db_success, db_message = insert_individual_alert(
                            detection, 
                            web_path, 
                            location_info 
                        )                        
                        print(f"DBログ挿入結果 ({detection['disease']}): {db_message}")
                else:
                    print(f"⚠️ 確信度が75%未満 ({final_confidence:.2f})、または検出結果がなかったため、ファイル保存とDB登録をスキップします。")
                    
            except Exception as e:
                print(f"推論中にエラーが発生しました: {e}")

def start_file_watcher():
    """ファイル監視スレッドを起動する"""
    if not os.path.exists(IMG_FOLDER):
        os.makedirs(IMG_FOLDER) 
        
    event_handler = ImageHandler()
    observer = Observer()
    observer.schedule(event_handler, IMG_FOLDER, recursive=False)
    observer.start()
    print(f"--- ファイル監視を開始しました: {IMG_FOLDER} ---") 
    try:
        while True:
            time.sleep(1) 
    except KeyboardInterrupt:
        observer.stop()
        observer.join()

# app.py の if __name__ == '__main__': ブロック内の修正
if __name__ == '__main__':
    # ...
    
    # ファイル監視を別スレッドで開始
    watcher_thread = threading.Thread(target=start_file_watcher)
    watcher_thread.daemon = True 
    watcher_thread.start()

    timer_thread = threading.Thread(target=start_capture_timer)
    timer_thread.daemon = True 
    timer_thread.start()
    
    # 開発サーバーの起動
    app.run(debug=True, port=5000, use_reloader=False) # use_reloader=False推奨