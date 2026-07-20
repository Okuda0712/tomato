# services/timer_service.py (修正後 - camera_config.py連携版)

import time
import os
import datetime
import cv2  # OpenCV for camera access

# ★新規追加: カメラ設定を読み込むためのモジュール★
from . import camera_config

# --- 設定 ---
# 監視対象フォルダの定義
IMG_FOLDER = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'img'))

# 画像取り込み周期 (秒)
CAPTURE_INTERVAL = 60 # 60秒ごとに画像をキャプチャ

# --- カメラキャプチャロジック ---

def map_device_id_to_index(device_id: str) -> int:
    """
    （簡易実装）ブラウザのデバイスIDをOpenCVのインデックス(0, 1, 2...)にマッピングする
    
    NOTE: OpenCVはブラウザのデバイスIDを直接扱えません。ここでは、固定値の0を返しますが、
    複数のカメラ環境では、デバイスIDとインデックスを紐づける複雑なロジックが必要です。
    多くの環境では、外部USBカメラはインデックス0または1になるため、ここでは0をデフォルトとします。
    """
    # 実際には、デバイスIDリストをenumerateDevices()などで取得し、OpenCVインデックスと紐づける必要があります。
    return 0

def capture_fixed_camera():
    """
    設定された固定カメラIDに基づき、画像をキャプチャし、img/ フォルダに保存する。
    """
    # 1. 設定されたカメラIDを取得
    device_id = camera_config.get_fixed_camera_device_id()
    
    if device_id is None:
        print("⚠️ TIMER SKIP: 定期監視カメラが設定されていません。")
        return

    # 2. カメラインデックスへのマッピング（簡易）
    camera_index = map_device_id_to_index(device_id)

    # 3. カメラオブジェクトの初期化
    cap = cv2.VideoCapture(camera_index)
    
    # 接続確認
    if not cap.isOpened():
        print(f"❌ CAMERA ERROR: カメラ (インデックス {camera_index}) を開けませんでした。")
        return

    try:
        # 画像のキャプチャ
        time.sleep(0.5) # カメラのウォーミングアップ
        ret, frame = cap.read() 

        if ret:
            # 4. ファイル名を作成
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"fixed_cam_{timestamp}.jpg"
            destination_path = os.path.join(IMG_FOLDER, new_filename)
            
            # 5. 画像をimgフォルダに保存 (AI推論をトリガー)
            cv2.imwrite(destination_path, frame)
            
            print(f"📸 FIXED CAMERA: 画像を {new_filename} として img/ に保存しました。")
        else:
            print("❌ CAMERA ERROR: フレームを読み込めませんでした。")

    except Exception as e:
        print(f"❌ CAMERA CAPTURE ERROR: 画像キャプチャ中にエラー: {e}")
        
    finally:
        # 6. カメラを解放
        cap.release()

def start_capture_timer():
    """
    一定周期で capture_fixed_camera を実行するタイマーループ。
    """
    print(f"--- 定期画像取り込みサービスを開始しました (周期: {CAPTURE_INTERVAL}秒) ---")

    # imgフォルダが存在しない場合は作成
    if not os.path.exists(IMG_FOLDER):
        os.makedirs(IMG_FOLDER)

    while True:
        try:
            # 設定された固定カメラをキャプチャする関数を実行
            capture_fixed_camera() 
        except Exception as e:
            print(f"致命的なタイマーエラー: {e}")
            
        # 定義された周期で待機
        time.sleep(CAPTURE_INTERVAL)