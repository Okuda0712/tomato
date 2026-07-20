// static/script.js

// カテゴリリスト (kihyo.html用)
const CATEGORIES = [
    'タバココナジラミ',
    'オオタバコガ',
    'アザミウマ',
    'トマトキバガ',
    'トマト硫黄葉巻病',
    'トマト硫黄エソ病',
    'その他（施設・環境）'
];

// --- グローバル変数 ---
let currentStream = null; // カメラ起動中にストリームを保持
let isCameraActive = false; // カメラが現在起動しているか

document.addEventListener('DOMContentLoaded', () => {
    // ----------------------------------------------------
    // 1. 起票フォーム (kihyo.html) 関連ロジック
    // ----------------------------------------------------
    const form = document.getElementById('ticket-form'); 
    
    // フォーム関連要素が存在する場合のみ処理を実行 (kihyo.htmlの場合)
    if (form) {
        // [既存のカテゴリドロップダウン構築ロジックをここに維持]
        const categoryToggle = document.getElementById('category-toggle');
        const categoryMenu = document.getElementById('category-menu');
        const selectedCategory = document.getElementById('selected-category');
        const hiddenCategoryInput = document.getElementById('hidden-category-input'); 
        const dropdownArrow = categoryToggle ? categoryToggle.querySelector('.dropdown-arrow') : null;
        const fileUpload = document.getElementById('file-upload');
        const fileDisplay = document.getElementById('file-display');

        if (categoryMenu) {
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
            categoryToggle.addEventListener('click', (event) => {
                event.stopPropagation();
                const isShown = categoryMenu.classList.toggle('show');
                if (dropdownArrow) dropdownArrow.textContent = isShown ? '▲' : '▼';
            });
        }

        menuItems.forEach(item => {
            item.addEventListener('click', (event) => {
                event.stopPropagation();
                const selectedValue = item.dataset.value; 
                selectedCategory.textContent = selectedValue;
                selectedCategory.style.color = '#333';
                categoryMenu.classList.remove('show');
                if (dropdownArrow) dropdownArrow.textContent = '▼';
                if (hiddenCategoryInput) {
                    hiddenCategoryInput.value = selectedValue;
                }
            });
        });
        
        document.addEventListener('click', () => {
            if (categoryMenu && categoryMenu.classList.contains('show')) {
                categoryMenu.classList.remove('show');
                if (dropdownArrow) dropdownArrow.textContent = '▼';
            }
        });
        
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
        
        // --- フォーム送信ロジックの統合 (POST /api/tickets) ---
        form.addEventListener('submit', async (event) => {
            event.preventDefault(); 
            
            // ... [既存のフォームデータ取得、バリデーション、API送信ロジックをここに維持] ...
            
            const category = hiddenCategoryInput ? hiddenCategoryInput.value : ''; 
            const title = form.querySelector('input[name="title"]').value;
            const location = form.querySelector('input[name="location"]').value;
            const details = form.querySelector('textarea[name="details"]').value;
            const year = form.querySelector('input[name="year"]').value;
            const month = form.querySelector('input[name="month"]').value;
            const day = form.querySelector('input[name="day"]').value;
            const hour = form.querySelector('input[name="hour"]').value;
            const minute = form.querySelector('input[name="minute"]').value;
            const creatorName = form.querySelector('input[name="creator_name"]').value;
            
            // 2. 必須項目のバリデーション
            if (!category || !title || !details || !year || !month || !day || !hour || !minute || !creatorName) {
                alert('🚨 すべての必須項目を入力してください。（カテゴリ、件名、日付/時刻、事象の内容、作成者名）');
                return; 
            }

            const isDateValid = !isNaN(parseInt(year)) && year.length === 4 && 
                                 !isNaN(parseInt(month)) && !isNaN(parseInt(day)) && 
                                 !isNaN(parseInt(hour)) && !isNaN(parseInt(minute));
                                 
            if (!isDateValid) {
                alert('🚨 日付または時刻の形式が正しくありません。');
                return;
            }
            
            const event_timestamp_value = 
                `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')} ${hour.padStart(2, '0')}:${minute.padStart(2, '0')}:00`; 

            const dataToSend = {
                category: category,
                title: title,
                location: location,
                details: details,
                event_timestamp: event_timestamp_value,
                creator_name: creatorName
            };

            try {
                const response = await fetch('/api/tickets', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(dataToSend)
                });
                
                if (response.headers.get('content-type')?.includes('application/json')) {
                    const result = await response.json();
                    
                    if (response.ok) {
                        alert('✅ 起票が正常に作成されました！ ID: ' + result.id);
                        form.reset(); 
                        window.location.href = '/kanri'; 
                    } else {
                        alert('❌ 起票作成に失敗しました: ' + (result.error || '不明なサーバーエラー'));
                    }
                } else {
                    alert('🔴 サーバーから予期しない形式の応答がありました。サーバーログを確認してください。');
                }
                
            } catch (error) {
                console.error('通信エラー:', error);
                alert('🔴 サーバーとの通信中に問題が発生しました。ネットワークまたはAPI接続を確認してください。');
            }
        });
    }

    // ----------------------------------------------------
    // 2. カメラビュー (camera_view.html) 関連ロジック
    // ----------------------------------------------------
    const cameraSelect = document.getElementById('camera-select');
    const startButton = document.getElementById('start-camera-button');
    const videoElement = document.getElementById('camera-stream');
    const captureButton = document.getElementById('capture-button');

    // camera_view.htmlの要素が存在する場合のみカメラロジックを実行
    if (videoElement && cameraSelect) {
        // ページロード時の初期化
        listCameras(); 
        
        // カメラ起動/設定保存のボタンアクションをアタッチ
        startButton.addEventListener('click', handleStartButton);
        
        // 手動撮影ボタンのアクションをアタッチ
        captureButton.addEventListener('click', capturePhoto); 
    }
});

// ----------------------------------------------------
// 新規機能: カメラ選択、固定設定、手動撮影
// ----------------------------------------------------

/**
 * 接続されているすべてのビデオデバイスを取得し、ドロップダウンに追加する。
 */
async function listCameras() {
    const cameraSelect = document.getElementById('camera-select');
    const startButton = document.getElementById('start-camera-button');

    try {
        // ユーザーにメディアアクセスを要求 (一度だけ許可が必要)
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        stream.getTracks().forEach(track => track.stop()); // 許可を得たらストリームはすぐに停止
        
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(device => device.kind === 'videoinput');
        
        cameraSelect.innerHTML = ''; // リストをクリア
        
        if (videoDevices.length === 0) {
            cameraSelect.innerHTML = '<option>カメラが見つかりません</option>';
            startButton.disabled = true;
            return;
        }

        videoDevices.forEach((device, index) => {
            const option = document.createElement('option');
            option.value = device.deviceId;
            option.text = device.label || `カメラ (${index + 1})`;
            cameraSelect.appendChild(option);
        });
        
        cameraSelect.selectedIndex = 0;

    } catch (err) {
        console.error("カメラの検出エラー:", err);
        cameraSelect.innerHTML = '<option>アクセスが拒否されました</option>';
        startButton.disabled = true;
    }
}


/**
 * 「カメラを起動/設定保存」ボタンのメインハンドラ
 */
async function handleStartButton() {
    if (!isCameraActive) {
        // 起動していない場合はカメラを起動
        startCameraStream();
    } else {
        // 起動済みの場合は設定を保存 (ストリームは維持)
        saveCameraSetting();
    }
}


/**
 * 選択したカメラのストリームを開始する
 */
async function startCameraStream() {
    const deviceId = document.getElementById('camera-select').value;
    const videoElement = document.getElementById('camera-stream');
    const startButton = document.getElementById('start-camera-button');
    
    // 既存のストリームを停止
    if (currentStream) {
        currentStream.getTracks().forEach(track => track.stop());
    }

    try {
        const constraints = {
            video: { deviceId: { exact: deviceId } }
        };
        currentStream = await navigator.mediaDevices.getUserMedia(constraints);
        videoElement.srcObject = currentStream;
        videoElement.play();
        
        isCameraActive = true;
        startButton.textContent = 'プレビュー中... (クリックで設定保存)';
        
        // 起動後、自動で設定保存APIも呼び出す (UIフィードバックを考慮し、ここでは手動設定を推奨)
        // saveCameraSetting(); 
        
    } catch (err) {
        console.error("カメラ起動エラー:", err);
        alert("選択されたカメラの起動に失敗しました。アクセス許可を確認してください。");
        isCameraActive = false;
        startButton.textContent = 'カメラを起動';
    }
}

/**
 * 選択されたカメラIDと固定設定をサーバーに送信する
 */
async function saveCameraSetting() {
    const deviceId = document.getElementById('camera-select').value;
    const isFixed = document.getElementById('fixed-camera-setting').checked;
    const statusMessage = document.getElementById('status-message');

    try {
        const response = await fetch('/api/camera/setting', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                device_id: deviceId, 
                is_fixed: isFixed,   
            })
        });

        if (response.ok) {
            statusMessage.textContent = `設定を保存しました。`;
            statusMessage.style.display = 'block';
            statusMessage.style.color = 'green';
            setTimeout(() => statusMessage.style.display = 'none', 3000);
        } else {
            const errorData = await response.json();
            statusMessage.textContent = `設定保存に失敗しました: ${errorData.error}`;
            statusMessage.style.display = 'block';
            statusMessage.style.color = 'red';
        }
    } catch (e) {
        console.error("設定保存API呼び出しエラー:", e);
        alert("サーバーとの通信エラーにより設定を保存できませんでした。");
    }
}


/**
 * ライブ映像から画像をキャプチャし、サーバーAPIに送信する (手動撮影)
 */
window.capturePhoto = function() {
    const videoElement = document.getElementById('camera-stream');
    const canvasElement = document.getElementById('camera-canvas');
    const feedback = document.getElementById('capture-feedback');
    const captureButton = document.getElementById('capture-button');

    if (!isCameraActive || !currentStream) {
        alert("カメラが起動していません。プレビューを開始してください。");
        return;
    }
    
    const context = canvasElement.getContext('2d');
    canvasElement.width = videoElement.videoWidth;
    canvasElement.height = videoElement.videoHeight;
    context.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);
    
    const imageDataURL = canvasElement.toDataURL('image/jpeg', 0.9); // JPEG、品質90%
    
    // APIに送信
    sendPhotoToServer(imageDataURL, feedback, captureButton);
}

/**
 * サーバーへ画像を送信 (手動撮影用)
 */
async function sendPhotoToServer(imageDataUrl, feedbackElement, buttonElement) {
    buttonElement.disabled = true;
    buttonElement.textContent = '送信中...';
    feedbackElement.style.display = 'block';
    feedbackElement.textContent = '画像を送信中...';
    feedbackElement.style.color = '#ffc107'; 

    try {
        const response = await fetch('/api/capture_and_save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image_data: imageDataUrl })
        });
        
        const result = await response.json();

        if (response.ok) {
            feedbackElement.textContent = `✅ 撮影成功！AI推論を開始しました。ファイル名: ${result.filename}`;
            feedbackElement.style.color = '#28a745';
        } else {
            feedbackElement.textContent = '❌ 撮影失敗: ' + (result.error || 'サーバーエラー');
            feedbackElement.style.color = '#dc3545';
        }
    } catch (error) {
        feedbackElement.textContent = '🔴 サーバーとの通信エラーが発生しました。';
        feedbackElement.style.color = '#dc3545';
    } finally {
        buttonElement.disabled = false;
        buttonElement.textContent = '手動で撮影';
        setTimeout(() => feedbackElement.style.display = 'none', 5000);
    }
}