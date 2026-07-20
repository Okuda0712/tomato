/**
 * script4.js - 起票一覧 (kannri.html) 用スクリプト
 * 選択機能、フィルタリング、描画ロジックを統合
 */

// グローバルなセットで選択されたIDを管理 (Excel出力用)
const selectedTicketIds = new Set(); 
// データ取得結果を保持
let currentTicketsData = [];

// DOM要素の取得
const categoryFilter = document.getElementById('category-filter');
const yearFilter = document.getElementById('date-filter-y');
const monthFilter = document.getElementById('date-filter-m');
const dayFilter = document.getElementById('date-filter-d');
const ticketListBody = document.getElementById('ticket-list-body');


document.addEventListener('DOMContentLoaded', () => {
    // ----------------------------------------------------------------------
    // 1. DOM要素の取得とイベントリスナーの設定
    // ----------------------------------------------------------------------
    
    // フィルター要素の変更時にデータを再ロードするイベントを設定
    // (デバウンス処理はここでは省略し、簡略化して記述)
    if (categoryFilter) categoryFilter.addEventListener('change', fetchTickets);
    
    if (yearFilter || monthFilter || dayFilter) {
        [yearFilter, monthFilter, dayFilter].forEach(element => {
            if (element) {
                // フィルタリング処理が重いため、changeイベントに限定
                element.addEventListener('change', fetchTickets); 
                element.addEventListener('input', fetchTickets); 
            }
        });
    }

    // 初回データロード
    fetchTickets();

    // ----------------------------------------------------------------------
    // 2. モーダルイベントリスナーの設定 (必要に応じてここに実装)
    // ----------------------------------------------------------------------
});


// ----------------------------------------------------------------------
// 3. データ取得と描画機能 (コアロジック)
// ----------------------------------------------------------------------

/**
 * APIから起票一覧データを取得し、テーブルを更新する
 */
async function fetchTickets() {
    if (!ticketListBody) return;
    ticketListBody.innerHTML = '<tr><td colspan="8">データを読み込み中です...</td></tr>'; // 8列に対応

    const apiUrl = '/api/tickets'; 

    try {
        const response = await fetch(apiUrl);
        if (!response.ok) {
            throw new Error(`HTTPエラー! ステータス: ${response.status}`);
        }
        
        const tickets = await response.json();
        currentTicketsData = tickets; // データ保持
        
        // クライアント側フィルタリングを実行 (HTMLのヘッダーに合わせた変数を使用)
        const category = categoryFilter ? categoryFilter.value : null;
        const year = yearFilter ? yearFilter.value : null;
        const month = monthFilter ? monthFilter.value : null;
        const day = dayFilter ? dayFilter.value : null;
        
        const filteredTickets = filterTicketsClientSide(tickets, category, year, month, day);

        renderTickets(filteredTickets);

    } catch (error) {
        console.error('起票データ取得エラー:', error);
        ticketListBody.innerHTML = `<tr><td colspan="8" class="error-message">データの取得に失敗しました。${error.message}</td></tr>`;
    }
}

/**
 * クライアント側でチケットをフィルタリングする (routes.pyのAPIがフィルタリングしない前提)
 */
function filterTicketsClientSide(tickets, category, year, month, day) {
    // [この関数は、routes.pyのAPIがフィルタリングロジックを持たない場合に必要です。
    //  サーバー側で実装済みであれば、この関数は削除可能です。]
    return tickets.filter(ticket => {
        let isMatch = true;

        // カテゴリフィルタ
        if (category && category !== 'all' && ticket.category !== category) {
            isMatch = false;
        }
        
        // 日付フィルタ (簡略化)
        if (isMatch && (year || month || day)) {
             const eventDate = new Date(ticket.event_timestamp); 
             if (year && eventDate.getFullYear() !== parseInt(year)) isMatch = false;
             if (month && (eventDate.getMonth() + 1) !== parseInt(month)) isMatch = false;
             if (day && eventDate.getDate() !== parseInt(day)) isMatch = false;
        }
        
        return isMatch;
    });
}


/**
 * 取得したデータをテーブルに描画する (Excel選択機能付き)
 */
function renderTickets(tickets) {
    if (!ticketListBody) return;
    
    if (tickets.length === 0) {
        ticketListBody.innerHTML = '<tr><td colspan="8">該当する起票データはありません。</td></tr>';
        return;
    }

    ticketListBody.innerHTML = ''; 

    tickets.forEach(ticket => {
        const row = ticketListBody.insertRow();
        row.className = 'ticket-row';
        row.dataset.ticketId = ticket.id; 
        
        // ★★★ 1. チェックボックス列の生成 (0番目のセル) ★★★
        const checkboxCell = row.insertCell(0); 
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'ticket-checkbox';
        checkbox.value = ticket.id; 
        
        // 選択状態を追跡するイベントリスナー
        checkbox.addEventListener('change', () => {
            if (checkbox.checked) {
                selectedTicketIds.add(ticket.id);
            } else {
                selectedTicketIds.delete(ticket.id);
            }
        });
        checkboxCell.appendChild(checkbox);

        // ★★★ 2. 残りのデータ列の追加 (insertCell(1) から開始) ★★★
        
        row.insertCell(1).textContent = ticket.id;                       // ID
        row.insertCell(2).textContent = ticket.category;                 // カテゴリー
        row.insertCell(3).textContent = ticket.title;                    // 件名
        
        // 発生日時
        const dateCell = row.insertCell(4);
        dateCell.textContent = formatTimestampForTable(ticket.event_timestamp);
        
        // 作成者 (COALESCEの結果)
        row.insertCell(5).textContent = ticket.creator_name || ticket.creator_name_display; 
        
        row.insertCell(6).textContent = ticket.location;                 // 場所
        
        // ステータスセル (HTML形式で挿入)
        const statusCell = row.insertCell(7);
        statusCell.innerHTML = formatStatusHtml(ticket.status);          // ステータス
    });
}


// ----------------------------------------------------------------------
// 4. Excel出力関数 (HTMLから onclick で呼ばれる)
// ----------------------------------------------------------------------

window.exportSelectedTickets = function() {
    if (selectedTicketIds.size === 0) {
        alert('出力する起票データを選択してください。');
        return;
    }

    // 選択されたIDをカンマ区切りの文字列に変換
    const idsString = Array.from(selectedTicketIds).join(',');
    
    // APIルートのURLを構築し、ブラウザをリダイレクトしてダウンロードをトリガー
    // NOTE: routes.pyの関数名は excel_download_api です
    const excelUrl = `${EXPORT_EXCEL_BASE_URL}?ticket_ids=${idsString}`;    
    window.location.href = excelUrl;
}


// --- ユーティリティ関数 (外部依存関数) ---

// ステータスをHTML形式で返す関数 (UI改善のため)
function formatStatusHtml(status) {
    if (!status) return '未定義';
    let text = status.charAt(0).toUpperCase() + status.slice(1);
    let className = status.toLowerCase(); 
    return `<span class="status-badge status-${className}">${text}</span>`;
}

// 日付表示用のヘルパー関数 
function formatTimestampForTable(timestampStr) {
    if (!timestampStr) return '';
    try {
        const dt = new Date(timestampStr);
        return dt.toLocaleString('ja-JP', {
            year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit'
        });
    } catch {
        return timestampStr;
    }
}