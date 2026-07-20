// static/script5.js - 異常検知一覧機能 (toFixedエラー対応版)

// フィルタリング後の現在の表示データを保持
let currentAlertsData = [];

// DOM要素の取得
const categorySelect = document.getElementById("alert-category-filter");
const yearInput = document.getElementById("alert-date-filter-y");
const monthInput = document.getElementById("alert-date-filter-m");
const dayInput = document.getElementById("alert-date-filter-d");
const tableBody = document.getElementById("alert-list-body");


// --- ユーティリティ関数 ---

/**
 * 対応状況を日本語に変換し、スタイルを適用するHTMLを返す
 * @param {string} status ('pending', 'in_progress', 'resolved'など)
 * @returns {string} 
 */
function formatStatusHtml(status) {
    let text = '未処理';
    let className = 'status-pending'; 
    if (status === 'resolved') {
        text = '対応済';
        className = 'status-resolved';
    } else if (status === 'in_progress') {
        text = '対応中';
        className = 'status-in-progress';
    }
    return `<span class="alert-status ${className}">${text}</span>`;
}

/**
 * ISO 8601形式の日時文字列を 'YYYY年<br />MM月DD日 HH:MM' 形式に整形
 * @param {string} timestampStr 
 * @returns {string} 
 */
function formatTimestamp(timestampStr) {
    if (!timestampStr) return '---<br />---';
    try {
        const dt = new Date(timestampStr);
        if (isNaN(dt.getTime())) return timestampStr.replace(' ', '<br />');

        const year = dt.getFullYear();
        const month = (dt.getMonth() + 1).toString().padStart(2, '0');
        const day = dt.getDate().toString().padStart(2, '0');
        const hour = dt.getHours().toString().padStart(2, '0');
        const minute = dt.getMinutes().toString().padStart(2, '0');
        
        return `${year}年<br />${month}月${day}日 ${hour}:${minute}`; 
    } catch(e) {
        return timestampStr.replace(' ', '<br />');
    }
}


// --- メイン機能 ---

// 1. データの取得と表示（サーバー側フィルタリング）
async function fetchAndRenderAlerts() {
    const selectedCategory = categorySelect ? categorySelect.value : 'all';
    const year = yearInput ? yearInput.value.trim() : '';
    const month = monthInput ? monthInput.value.trim() : ''; 
    const day = dayInput ? dayInput.value.trim() : ''; 

    const params = new URLSearchParams();
    if (selectedCategory !== 'all') params.append('type', selectedCategory);
    if (year) params.append('year', year);
    if (month) params.append('month', month);
    if (day) params.append('day', day);

    if (tableBody) {
        tableBody.innerHTML = '<tr><td colspan="6">検知データを読み込み中です...</td></tr>';
    }
    
    try {
        const response = await fetch(`/api/alerts?${params.toString()}`);
        if (!response.ok) {
            throw new Error(`異常検知データの取得に失敗しました。ステータス: ${response.status}`);
        }
        
        currentAlertsData = await response.json(); 
        displayAlerts(currentAlertsData);

    } catch (error) {
        console.error('異常検知データの取得中にエラー:', error);
        if (tableBody) {
            tableBody.innerHTML = `<tr><td colspan="6" style="color: red;">データ取得エラー: ${error.message}</td></tr>`;
        }
    }
}

// 2. データをテーブルに描画する
function displayAlerts(alerts) {
    if (!tableBody) return; // tableBody (alert-list-body) があることを確認
    
    // ★HTMLをクリア (エラーメッセージもここに入るため、クリアが必要)
    tableBody.innerHTML = ''; 

    if (alerts.length === 0) {
        // カードグリッドとして表示
        tableBody.innerHTML = '<p style="text-align: center; grid-column: 1 / -1;">該当する異常検知データは見つかりませんでした。</p>';
        return;
    }

    alerts.forEach(alert => {
        const card = document.createElement('div');
        card.className = `alert-card status-${alert.status.toLowerCase()}`;

        // ★クリックで詳細ページに遷移させるロジック★
        card.onclick = () => {
            // ui_routes.pyで定義したURLに alert_id を付けて遷移
            window.location.href = `/keiti/syousai?alert_id=${alert.id}`;
        };
        
        // --- 暫定の画像表示ロジック（後で実装するまで、画像パスのテキストを表示） ---
        let imageHtml = '';
        if (alert.attachment_path) {
            // パスが存在する場合、代替画像が表示されるように<img>タグを挿入
            imageHtml = `
                <div class="card-image-wrapper">
                    <img src="${alert.attachment_path}" alt="検知画像" onerror="this.onerror=null; this.src='/static/no-image.png';" class="alert-card-image">
                </div>
            `;
        }

        // --- カードのinnerHTML ---
        card.innerHTML = `
            ${imageHtml}
            <div class="card-content">
                <div class="card-header">
                    <span class="card-id">ID: ${alert.id}</span>
                    <span class="card-status">${formatStatusHtml(alert.status)}</span>
                </div>
                <div class="card-body">
                    <p class="card-type"><strong>${alert.type}</strong></p>
                    <p class="card-location"><i class="fas fa-map-marker-alt"></i> ${alert.location || 'エリア不明'}</p>
                    <p class="card-timestamp"><i class="fas fa-clock"></i> ${alert.timestamp}</p>
                    <p class="card-confidence">確度: ${alert.confidence}</p>
                </div>
            </div>
        `;
        
        // ★tableBody (グローバルで定義されたコンテナ) にカードを追加★
        tableBody.appendChild(card);
    });
}
// 3. モーダル（詳細表示）機能
window.closeAlertModal = function() {
    const modal = document.getElementById('alert-detail-modal');
    if (modal) modal.style.display = 'none';
}

window.showAlertDetails = async function(alertId) {
    const modal = document.getElementById('alert-detail-modal');
    if (modal) modal.style.display = 'flex';
    
    const detail = currentAlertsData.find(a => a.id === alertId);

    if (!detail) {
        alert('詳細データが見つかりませんでした。画面を再読み込みしてください。');
        if (modal) closeAlertModal();
        return;
    }

    try {
        let eventTime = formatTimestamp(detail.timestamp).replace(/<br\s*\/?>/g, ' '); 
        
        // ★★★ 修正ポイント: toFixed() を呼び出す前に数値であることを確認 ★★★
        const confidenceDisplay = detail.confidence !== null && !isNaN(parseFloat(detail.confidence))
            ? `${parseFloat(detail.confidence).toFixed(1)}%`
            : '-';


        let attachmentHtml = '（画像データなし）';
        if (detail.attachment_path) {
            const path = detail.attachment_path.startsWith('/') ? 
                         detail.attachment_path : 
                         `/${detail.attachment_path}`; 
            
            const fileExtension = path.split('.').pop().toLowerCase();
            if (['jpg', 'jpeg', 'png', 'gif'].includes(fileExtension)) {
                 attachmentHtml = `
                     <a href="${path}" target="_blank" style="text-decoration: underline;">検知画像を表示</a>
                     <br><img src="${path}" style="max-width: 100%; height: auto; margin-top: 10px;">
                   `;
            } else {
                 attachmentHtml = `<a href="${path}" target="_blank" style="text-decoration: underline;">添付ファイルを表示</a>`;
            }
        }

        // モーダル要素へのデータ挿入
        document.getElementById('detail-alert-id').textContent = detail.id;
        document.getElementById('detail-alert-type').textContent = detail.type;
        document.getElementById('detail-alert-timestamp').textContent = eventTime;
        document.getElementById('detail-alert-location').textContent = detail.location || '-';
        document.getElementById('detail-alert-confidence').textContent = confidenceDisplay; // 修正後の変数を使用
        document.getElementById('detail-alert-status').innerHTML = formatStatusHtml(detail.status); 
        document.getElementById('detail-alert-details').textContent = detail.details || '詳細情報の記載はありません。';
        document.getElementById('detail-alert-attachment-area').innerHTML = attachmentHtml;
        
    } catch (error) {
        console.error('詳細データの表示中にエラー:', error);
        alert(`詳細の表示中にエラーが発生しました: ${error.message}`);
        if (modal) closeAlertModal();
    }
}

// 4. この異常を元に起票を作成する機能 
window.createTicketFromAlert = function() {
    const alertId = document.getElementById('detail-alert-id').textContent;
    window.location.href = `/kihyo?alert_id=${alertId}`; // kihyo_index の URLに修正
    closeAlertModal();
}


// 5. デモデータ登録機能
window.registerDemoAlert = async function() {
    // 1. 手動で設定された値を取得
    const manualTypeInput = document.getElementById('manual-type');
    const manualTimestampInput = document.getElementById('manual-timestamp');

    if (!manualTypeInput || !manualTimestampInput) {
        alert("手動デモ入力フィールドが見つかりません。HTMLを確認してください。");
        return;
    }

    const manualType = manualTypeInput.value;
    const manualTimestamp = manualTimestampInput.value.trim();

    // is_pest_disease を手動Typeに基づいて決定
    let isPestDisease = 0;
    if (manualType === '害虫高密度' || manualType === '病気初期') {
        isPestDisease = 1;
    }
    
    const demoData = {
        type: manualType,
        timestamp: manualTimestamp, // YYYY-MM-DD HH:MM 形式を期待
        is_pest_disease: isPestDisease,
    };

    // 画面全体からデモボタンを検索し、無効化
    const demoButton = document.querySelector('.button-demo'); 
    
    if(demoButton) {
        demoButton.disabled = true;
        const originalText = '🚨 デモ異常検知を発生させる'; // ボタンテキストを固定値で定義
        const loadingText = '登録中...';
        const buttonTextElement = demoButton.querySelector('.button-text');
        
        // 現在のテキストを保存するロジックをシンプル化し、確実に読み込み中表示
        if (buttonTextElement) {
             buttonTextElement.textContent = loadingText;
        } else {
             // button-textがない場合、ボタン全体にテキストを設定
             demoButton.textContent = loadingText;
        }
    }

    try {
        const response = await fetch('/api/register_demo_alert', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(demoData) // サーバーに手動設定値を送信
        });

        const result = await response.json();

        if (!response.ok) {
            alert(`デモ検知失敗: ${result.error || '不明なエラー'}`);
            throw new Error(result.error || 'API call failed'); 
        }

        alert(result.message);
        // 新規登録後、一覧を更新
        fetchAndRenderAlerts(); 

    } catch (error) {
        console.error('デモ検知エラー:', error);
        alert("デモ登録エラーが発生しました。コンソールを確認してください。");
    } finally {
         // 処理完了後、ボタンを元に戻す
         if(demoButton) {
             demoButton.disabled = false;
             const buttonTextElement = demoButton.querySelector('.button-text');
             const originalText = '🚨 デモ異常検知を発生させる';
             if (buttonTextElement) {
                 buttonTextElement.textContent = originalText;
             } else {
                 demoButton.textContent = originalText;
             }
         }
    }
}

// 6. イベントリスナーの設定
function setupEventListeners() {
    if (categorySelect) categorySelect.addEventListener("change", fetchAndRenderAlerts);
    
    // 日付入力フィールドのイベントリスナー設定 (入力完了ごとに更新)
    if (yearInput && monthInput && dayInput) {
        [yearInput, monthInput, dayInput].forEach(input => {
            input.addEventListener('input', (e) => {
                // 数字以外を削除
                e.target.value = e.target.value.replace(/[^0-9]/g,'');
                fetchAndRenderAlerts(); // フィルタ変更の度にAPIを呼び出し
            });
        });
    }
}

// 7. ページロード完了時にデータを読み込む
window.addEventListener('DOMContentLoaded', () => {
    fetchAndRenderAlerts();
    setupEventListeners();
});

// static/script5.js

// ページのURLに基づいて、現在のページを識別する

// ... (fetchAlerts 関数はそのまま利用) ...

// static/script5.js (ファイルの末尾に追加)

function fetchAlertDetail(alertId) {
    fetch(`/api/alerts/${alertId}`) // ★新しいAPIエンドポイントを呼び出す
        .then(response => {
            if (!response.ok) {
                throw new Error('詳細データの取得に失敗しました。');
            }
            return response.json();
        })
// static/script5.js の fetchAlertDetail 関数内

    .then(alertData => {
        // データをHTMLに表示
        // ★修正: すべてのデータ取得に || 'N/A' を適用し、nullによる中断を防ぐ★
        document.getElementById('detail-alert-id').textContent = alertData.id || 'N/A';
        document.getElementById('detail-alert-type').textContent = alertData.type || 'データなし';
        document.getElementById('detail-alert-timestamp').textContent = alertData.timestamp || 'N/A';
        document.getElementById('detail-alert-location').textContent = alertData.location || '不明';
        document.getElementById('detail-alert-confidence').textContent = alertData.confidence || 'N/A';
        document.getElementById('detail-alert-status').textContent = alertData.status || 'N/A';

        // --- 詳細検出データ (JSON) の安全なパース ---
        try {
            // detailsが null/undefined の場合は空のオブジェクトをパースし、処理が中断しないようにする
            const detailsRaw = alertData.details || '{}';
            const detailsObject = JSON.parse(detailsRaw); 
            document.getElementById('detail-alert-details').textContent = JSON.stringify(detailsObject, null, 2);
        } catch (e) {
            // パース失敗時も処理を続行し、DBの生データを表示
            document.getElementById('detail-alert-details').textContent = alertData.details || '詳細データが見つかりません。';
        }

        // --- 画像表示ロジックの有効化 ---
        const imageElement = document.getElementById('detail-alert-image');
        const imagePathText = document.getElementById('image-path-text');

        if (alertData.attachment_path && imageElement) {
            imageElement.src = alertData.attachment_path; // /static/... のWebパスを直接指定
            imageElement.style.display = 'block'; // 画像を表示
            imagePathText.textContent = `ファイル名: ${alertData.attachment_path.split('/').pop()}`;
        } else {
            imageElement.style.display = 'none'; // 画像を非表示
            imagePathText.textContent = '画像なし';
        }
        localStorage.setItem('alertToTicket', JSON.stringify(alertData));
        console.log('✅ Local Storage にアラートID', alertData.id, 'のデータを保存しました。');
        // ... (ローカルストレージの保持はそのまま)
    })
    .catch(error => {
        // ... (エラー処理) ...
        // 取得失敗時にユーザーにフィードバック
        document.getElementById('detail-alert-id').textContent = 'エラー';
        document.getElementById('detail-alert-type').textContent = 'データの読み込み中にエラーが発生しました。';
        console.error('異常検知詳細のロードに失敗:', error);
    });}

function createTicketFromAlert() {
    // 1. ローカルストレージからアラートデータを取得
    const alertDataJson = localStorage.getItem('alertToTicket');
    if (!alertDataJson) {
        alert('起票する異常データが見つかりません。');
        return;
    }
    const alertData = JSON.parse(alertDataJson);
    
    // 2. 起票作成画面に遷移し、アラートIDをクエリパラメータとして渡す
    // kihyo.htmlでこのalert_idを受け取り、フォームにデータを事前入力する
    window.location.href = `/kihyo?alert_id=${alertData.id}`;
}

// static/script5.js (DOMContentLoaded イベントリスナー内)

document.addEventListener('DOMContentLoaded', () => {
    // ページURLの最後の部分が 'syousai' であることをチェック
    const currentPage = window.location.pathname.split('/').pop().split('?')[0];

    if (currentPage === 'keiti') {
        fetchAndRenderAlerts(); // keiti.html では一覧を取得
        setupEventListeners();
    } else if (currentPage === 'syousai') { // ★syousai.html の場合★
        const urlParams = new URLSearchParams(window.location.search);
        const alertId = urlParams.get('alert_id'); // URLからIDを取得
        
        if (alertId) {
            fetchAlertDetail(alertId); // ★詳細データのロードを強制実行★
        } else {
             // alertIdがない場合はエラーログを出して終了
             console.error('致命的エラー: syousai.html に alert_id が指定されていません。');
        }
    }
    // ... (event listeners の設定は削除し、DOMContentLoadedの外に移動することを推奨)
});

// setupEventListeners は DOMContentLoaded の外で定義する