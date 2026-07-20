# blueprints/auth_routes.py (新規作成)

from flask import Blueprint, render_template, request, redirect, url_for, session
# 認証サービス、ユーティリティをインポート
from services.user_service import authenticate_user, register_user 
from services.auth_utils import login_required 

# 認証関連のBlueprintを定義
auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/', methods=['GET', 'POST'])
def index():
    error = None
    # user_id は POST リクエストでのみ使用されるため、ここで初期化は不要。

    # 1. 既にログインしている場合はホーム画面へリダイレクト (GET)
    if 'user_id' in session:
        # 認証後の画面へリダイレクト
        return redirect(url_for('ui_bp.home_index')) 

    # 2. ログイン処理 (POST)
    if request.method == 'POST':
        # フォームデータ取得
        login_id = request.form.get('login_id') 
        password = request.form.get('password')
        
        # データの空チェック
        if not login_id or not password:
            error = "ログインIDとパスワードを入力してください。"
            return render_template('index.html', error=error), 401 
        
        # 認証サービスの呼び出し
        user_id = authenticate_user(login_id, password) 

        if user_id:
            # 認証成功
            session['user_id'] = user_id
            session['user_name'] = login_id
            return redirect(url_for('ui_bp.home_index')) 
        else:
            # 認証失敗
            error = "ログインIDまたはパスワードが正しくありません。"
            return render_template('index.html', error=error), 401
            
    # 3. ログイン画面の表示 (GET)
    return render_template('index.html', error=None)

@auth_bp.route('/sakusei', methods=['GET'])
def sakusei_index():
    """
    sakusei.html (アカウント作成フォーム) の表示。
    """
    return render_template('sakusei.html')

@auth_bp.route('/sakusei', methods=['POST'])
def sakusei_post():
    # ★修正点 1: request.form からデータを取得する
    username = request.form.get('username')   # sakusei.html の name="username"
    login_id = request.form.get('login_id')   # sakusei.html の name="login_id"
    password = request.form.get('password')   # sakusei.html の name="password"
    
    # ★修正点 2: user_service に引数を正しい順番で渡す
    # 順番: (表示名, ログインID, パスワード)
    success, message = register_user(username, login_id, password)
    
    if success:
        # 成功したらログインページへリダイレクト
        return redirect(url_for('ui_bp.kannryou_index')) 
    else:
        # 失敗したらエラーメッセージと共に作成ページへ戻る
        return render_template('sakusei.html', error=message), 400

@auth_bp.route('/logout', methods=['POST', 'GET']) # GETも許可し、aタグでのアクセスにも対応
@login_required # ログアウトはログイン後に実行可能
def logout():
    """
    UIからのログアウト処理。
    """
    # セッションから情報を削除
    session.pop('user_id', None)
    session.pop('user_name', None)
    
    # ログインページへリダイレクト
    return redirect(url_for('auth_bp.index'))

@auth_bp.route('/login-demo', methods=['GET'])
def login_demo():
    """
    管理者アカウントでの強制ログイン (デモ用)。
    GETリクエストを受け付けます。
    """
    # 元のapppyui.txtにあったデモ用の強制ログインロジックを再現
    session.pop('user_id', None)
    session.pop('user_name', None)
        
    session['user_id'] = 1 
    session['user_name'] = '管理者アカウント（デモ）'
    
    # ログイン後、UIのメイン画面へリダイレクト
    return redirect(url_for('ui_bp.home_index'))