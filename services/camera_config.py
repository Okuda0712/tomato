# services/camera_config.py (新規作成)

# ★定期監視カメラのデバイスIDを保持するグローバル変数★
# デフォルトではNone (設定なし)
FIXED_CAMERA_DEVICE_ID = None

def set_fixed_camera_device_id(device_id: str | None):
    """
    定期監視カメラとして使用するデバイスIDを設定する。
    """
    global FIXED_CAMERA_DEVICE_ID
    FIXED_CAMERA_DEVICE_ID = device_id
    print(f"📷 GLOBAL CONFIG: 定期監視カメラIDが '{FIXED_CAMERA_DEVICE_ID}' に設定されました。")

def get_fixed_camera_device_id() -> str | None:
    """
    現在設定されている定期監視カメラのデバイスIDを取得する。
    """
    return FIXED_CAMERA_DEVICE_ID

# NOTE: 本番環境では、この設定はデータベースまたは永続的な設定ファイルに保存する必要があります。