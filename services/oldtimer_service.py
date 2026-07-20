# services/timer_service.py (新規作成)

import time
import os
import shutil
import random
import datetime

# --- 設定 ---
# 監視対象フォルダとダミー画像フォルダの定義
IMG_FOLDER = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'img'))
# ダミー画像が存在するフォルダを仮定 (例: project_root/dummy_images/)
DUMMY_IMAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dummy_images'))

# 画像取り込み周期 (秒)
CAPTURE_INTERVAL = 60 # 60秒ごとに画像をコピー

# --- タイマーロジック ---

def simulate_camera_capture():
    """
    ダミー画像を img/ フォルダにコピーし、AI推論をトリガーする。
    """
    if not os.path.exists(DUMMY_IMAGE_DIR):
        print(f"❌ ERROR: ダミー画像フォルダが見つかりません: {DUMMY_IMAGE_DIR}")
        return

    # 1. ダミー画像のリストを取得
    image_files = [f for f in os.listdir(DUMMY_IMAGE_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if not image_files:
        print("💡 WARNING: ダミー画像フォルダに画像ファイルがありません。")
        return

    # 2. ランダムに1枚の画像を選択
    selected_filename = random.choice(image_files)
    source_path = os.path.join(DUMMY_IMAGE_DIR, selected_filename)
    
    # 3. コピー先のファイル名をユニークにする (推論ハンドラが on_created イベントを確実に検知するため)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    new_filename = f"cam_capture_{timestamp}_{selected_filename}"
    destination_path = os.path.join(IMG_FOLDER, new_filename)
    
    try:
        # 4. 画像をimgフォルダにコピーし、推論をトリガー
        shutil.copy(source_path, destination_path)
        print(f"📸 CAMERA SIM: 画像を {new_filename} として img/ にコピーしました。")
    except Exception as e:
        print(f"❌ CAMERA SIM ERROR: ファイルコピー中にエラー: {e}")

def start_capture_timer():
    """
    一定周期で simulate_camera_capture を実行するタイマーループ。
    """
    print(f"--- 定期画像取り込みサービスを開始しました (周期: {CAPTURE_INTERVAL}秒) ---")
    
    # ダミー画像フォルダの存在を確認
    if not os.path.exists(DUMMY_IMAGE_DIR):
        print("🚨 CRITICAL: ダミー画像フォルダが存在しません。推論をトリガーできません。")
        return

    # 初回実行
    simulate_camera_capture()

    # 以降、指定されたインターバルで実行
    while True:
        try:
            time.sleep(CAPTURE_INTERVAL)
            simulate_camera_capture()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"TIMER ERROR: 予期せぬエラー: {e}")
            time.sleep(60) # エラー後、1分待機してから再試行