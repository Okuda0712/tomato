from flask import Blueprint, render_template, request, redirect, url_for, session
from services.db_config import get_db_connection, login_required

# 認証サービスは直接使用せず、Flaskセッションのみをチェックします。
# auth_routes.py が認証ロジックを担当するため、user_serviceのインポートは不要です。

# UI用のBlueprintを定義
ui_bp = Blueprint('ui_bp', __name__)

# --- UI画面表示ルート (認証チェックあり) ---

# 認証チェックヘルパー関数
def is_logged_in():
    """セッションにユーザーIDが存在するかをチェックする"""
    return 'user_id' in session

@ui_bp.route('/home')
def home_index():
    """
    ホーム画面 (kihyo.html / kannri.html の戻るボタンの遷移先)。
    認証がなければログイン画面へリダイレクト。
    """
    if not is_logged_in():
        # 認証がなければ auth_bp のログインルートへリダイレクト
        return redirect(url_for('auth_bp.index')) 
    
    # 既存のHTMLファイルとの整合性を取るため、ここでは起票一覧（kannri.html）をホーム画面として利用します
    return render_template('kannri.html', username=session.get('user_name', 'User'))

@ui_bp.route('/kihyo')
def kihyo_index():
    """起票作成画面 (kihyo.html)"""
    if not is_logged_in(): 
        return redirect(url_for('auth_bp.index'))
    
    # ★修正: alert_idをクエリパラメータとして受け取る★
    alert_id = request.args.get('alert_id', type=int) 
    
    # テンプレートに alert_id を渡す (今回は使用しないが、URLをクリーンに保つため)
    return render_template('kihyo.html', alert_id=alert_id)

@ui_bp.route('/kanri')
def kannri_index():
    """起票一覧画面 (kannri.html)"""
    if not is_logged_in(): 
        return redirect(url_for('auth_bp.index'))
    return render_template('kannri.html')

@ui_bp.route('/keiti')
def keiti_index():
    """異常検知一覧画面 (keiti.html)"""
    if not is_logged_in(): 
        return redirect(url_for('auth_bp.index'))
    return render_template('keiti.html') 

@ui_bp.route('/settei')
def settei_index(): 
    """アカウント設定画面/一覧画面 (settei.html)"""
    if not is_logged_in(): 
        return redirect(url_for('auth_bp.index'))
    user_name = session.get('user_name', 'ユーザー')
    return render_template('settei.html', user_name=user_name)

# --- 特殊・認証不要なルート ---

@ui_bp.route('/kanryo')
def kannryou_index(): 
    """
    アカウント作成完了画面 (kannryou.html)。
    このページ自体は認証を必須としない。
    """
    return render_template('kannryou.html')

@ui_bp.route('/syosai')
def syosai_index():
    """レポートダッシュボード画面 (syosai.html)"""
    if not is_logged_in(): 
        return redirect(url_for('auth_bp.index'))
    # syosai.html がない場合、ダミーとして別のテンプレートを使用するか、
    # テンプレートファイルを用意してください。
    return render_template('syosai.html')


# NOTE: index, sakusei, logout ルートは auth_routes.py に移管しました。
# ui_bp.index は廃止し、ui_bp内の未認証リダイレクト先を auth_bp.index に統一します。

# blueprints/ui_routes.py

# ... (既存のインポート) ...

@ui_bp.route('/keiti/syousai')
@login_required
def syousai_index():
    # ★alert_idをクエリパラメータとして受け取る
    alert_id = request.args.get('alert_id', type=int)
    if alert_id is None:
        # IDがなければ一覧へリダイレクト
        return redirect(url_for('ui_bp.keiti_index'))
        
    return render_template('syousai.html', alert_id=alert_id)

# blueprints/ui_routes.py (追加)

@ui_bp.route('/camera')
@login_required # ログイン必須
def camera_page():
    """デモ用カメラページを表示するルート"""
    if not is_logged_in(): 
        return redirect(url_for('auth_bp.index'))
    
    return render_template('camera_view.html')

@ui_bp.route('/dashboard')
def dashboard_index():
    """ダッシュボード画面 (集計とサマリー)"""
    if not is_logged_in(): 
        return redirect(url_for('auth_bp.index'))
    
    # templates/dashboard.html が必要です
    return render_template('dashboard.html')