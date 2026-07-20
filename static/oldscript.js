// static/script.js (kihyo.html用)

const CATEGORIES = [
    'タバココナジラミ',
    'オオタバコガ',
    'アザミウマ',
    'トマトキバガ',
    'トマト硫黄葉巻病',
    'トマト硫黄エソ病',
    'その他（施設・環境）'
];

document.addEventListener('DOMContentLoaded', () => {
    // ----------------------------------------------------
    // 1. UI 要素の取得とカテゴリ ドロップダウンのロジック
    // ----------------------------------------------------
    const categoryToggle = document.getElementById('category-toggle');
    const categoryMenu = document.getElementById('category-menu');
    const selectedCategory = document.getElementById('selected-category');
    // フォーム送信に必要な隠しフィールド
    const hiddenCategoryInput = document.getElementById('hidden-category-input'); 
    const filePlaceholderElement = document.querySelector('.file-placeholder'); 
    const dropdownArrow = categoryToggle ? categoryToggle.querySelector('.dropdown-arrow') : null;

    if (categoryMenu) {
        // カテゴリリストをドロップダウンメニューに挿入
        CATEGORIES.forEach(category => {
            const item = document.createElement('div');
            item.classList.add('dropdown-item');
            item.dataset.value = category;
            item.textContent = category;
            categoryMenu.appendChild(item);
        });
    }

    const menuItems = categoryMenu ? categoryMenu.querySelectorAll('.dropdown-item') : [];

    if (categoryToggle && categoryMenu) {
        // ドロップダウンの表示/非表示を切り替え
        categoryToggle.addEventListener('click', (event) => {
            event.stopPropagation();
            const isShown = categoryMenu.classList.toggle('show');
            if (dropdownArrow) dropdownArrow.textContent = isShown ? '▲' : '▼';
        });
    }

    // ドロップダウン項目の選択処理
    menuItems.forEach(item => {
        item.addEventListener('click', (event) => {
            event.stopPropagation();
            const selectedValue = item.dataset.value; 
            selectedCategory.textContent = selectedValue;
            selectedCategory.style.color = '#333'; // 選択後、文字色を通常に戻す
            categoryMenu.classList.remove('show');
            if (dropdownArrow) dropdownArrow.textContent = '▼';
            if (hiddenCategoryInput) {
                hiddenCategoryInput.value = selectedValue;
            }
        });
    });
    
    // ドロップダウン外をクリックしたときに閉じる処理
    document.addEventListener('click', () => {
        if (categoryMenu && categoryMenu.classList.contains('show')) {
            categoryMenu.classList.remove('show');
            if (dropdownArrow) dropdownArrow.textContent = '▼';
        }
    });

    // 添付資料のファイル名表示ロジック
    const fileUpload = document.getElementById('file-upload');
    const fileDisplay = document.getElementById('file-display');

    if (fileUpload && fileDisplay) {
        fileUpload.addEventListener('change', () => {
            if (fileUpload.files.length > 0) {
                fileDisplay.textContent = fileUpload.files[0].name;
                fileDisplay.style.color = '#333';
            } else {
                fileDisplay.textContent = 'ファイルが選択されていません';
                fileDisplay.style.color = '#888';
            }
        });
    }
    
    // ----------------------------------------------------
    // 2. フォーム送信ロジックの統合 (POST /api/tickets)
    // ----------------------------------------------------
    const form = document.getElementById('ticket-form'); 
        
    if (form) {
        form.addEventListener('submit', async (event) => {
            event.preventDefault(); 
            
            // 1. フォームデータの取得
            const category = hiddenCategoryInput ? hiddenCategoryInput.value : ''; 
            const title = form.querySelector('input[name="title"]').value;
            const location = form.querySelector('input[name="location"]').value;
            const details = form.querySelector('textarea[name="details"]').value;
            
            // 発生日時フィールドの値を取得
            const year = form.querySelector('input[name="year"]').value;
            const month = form.querySelector('input[name="month"]').value;
            const day = form.querySelector('input[name="day"]').value;
            const hour = form.querySelector('input[name="hour"]').value;
            const minute = form.querySelector('input[name="minute"]').value;
            
            // ★ 作成者名の取得 ★
            const creatorName = form.querySelector('input[name="creator_name"]').value;
            
            // 2. 必須項目のバリデーション
            if (!category || !title || !details || !year || !month || !day || !hour || !minute || !creatorName) {
                alert('🚨 すべての必須項目を入力してください。（カテゴリ、件名、日付/時刻、事象の内容、作成者名）');
                return; 
            }

            // 日付/時刻の値の形式チェック (簡易)
            const isDateValid = !isNaN(parseInt(year)) && year.length === 4 && 
                                 !isNaN(parseInt(month)) && !isNaN(parseInt(day)) && 
                                 !isNaN(parseInt(hour)) && !isNaN(parseInt(minute));
                                 
            if (!isDateValid) {
                alert('🚨 日付または時刻の形式が正しくありません。');
                return;
            }
            
            // 3. DB形式へのデータ整形
            const event_timestamp_value = 
                `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')} ${hour.padStart(2, '0')}:${minute.padStart(2, '0')}:00`; 

            // サーバーに送信するデータ
            const dataToSend = {
                category: category,
                title: title,
                location: location,
                details: details,
                event_timestamp: event_timestamp_value,
                // ★★★ 修正: creator_name を追加する ★★★
                creator_name: creatorName
            };

            // 4. Flask APIへのデータ送信 (POSTリクエスト)
            try {
                const response = await fetch('/api/tickets', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(dataToSend)
                });
                
                // サーバーが正常にJSONを返したか確認
                if (response.headers.get('content-type')?.includes('application/json')) {
                    const result = await response.json();
                    
                    if (response.ok) {
                        alert('✅ 起票が正常に作成されました！ ID: ' + result.id);
                        form.reset(); 
                        // 成功後、起票一覧ページへ遷移
                        window.location.href = '/kanri'; 
                    } else {
                        // サーバーから送られたエラー（外部キーエラー等）を正確に表示
                        alert('❌ 起票作成に失敗しました: ' + (result.error || '不明なサーバーエラー'));
                    }
                } else {
                    // JSONではない、予期しないレスポンスが来た場合 (例: 500エラーのHTMLページ)
                    alert('🔴 サーバーから予期しない形式の応答がありました。サーバーログを確認してください。');
                }
                
            } catch (error) {
                console.error('通信エラー:', error);
                alert('🔴 サーバーとの通信中に問題が発生しました。ネットワークまたはAPI接続を確認してください。');
            }
        });
    }
});

// static/script.js (追記)

// グローバル変数
let videoStream = null;

// --- Webカメラの起動 ---
window.startCamera = async function() {
    const video = document.getElementById('camera-stream');
    const startButton = document.getElementById('start-camera-button');

    try {
        videoStream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = videoStream;
        video.play();
        startButton.textContent = 'シャッターを切る';
        startButton.onclick = capturePhoto; // ボタンの動作を撮影に切り替え

    } catch (err) {
        alert('カメラへのアクセスが拒否されました。ブラウザの権限を確認してください。');
        console.error("Camera access error: ", err);
    }
}

// --- 写真撮影と送信 ---
window.capturePhoto = function() {
    const video = document.getElementById('camera-stream');
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    
    // 映像をキャンバスに描画
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // 画像データをBase64形式で取得
    const imageDataUrl = canvas.toDataURL('image/jpeg'); // JPEG形式で取得

    // 撮影後、ストリームを停止
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
    }
    
    // APIに送信
    sendPhotoToServer(imageDataUrl);
}

// --- サーバーへ画像を送信 ---
async function sendPhotoToServer(imageDataUrl) {
    // 撮影中はボタンを無効化
    const startButton = document.getElementById('start-camera-button');
    startButton.disabled = true;
    startButton.textContent = '送信中...';

    try {
        const response = await fetch('/api/capture_and_save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image_data: imageDataUrl })
        });
        
        const result = await response.json();

        if (response.ok) {
            alert(`✅ 撮影成功！推論を開始します。ファイル名: ${result.filename}`);
        } else {
            alert('❌ 撮影失敗: ' + (result.error || 'サーバーエラー'));
        }
    } catch (error) {
        alert('🔴 サーバーとの通信エラーが発生しました。');
    } finally {
        // ボタンを元に戻す
        startButton.disabled = false;
        startButton.textContent = 'カメラを起動';
        startButton.onclick = startCamera; 
    }
}