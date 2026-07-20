/**
 * script_dashboard.js - ダッシュボード画面 (dashboard.html) 用スクリプト
 * 異常検知の時系列グラフとサマリー表示を管理
 */

document.addEventListener('DOMContentLoaded', () => {
    // ----------------------------------------------------------------------
    // DOM要素の取得
    // ----------------------------------------------------------------------
    const timelineChartCanvas = document.getElementById('timeline-chart');
    const totalAlertsSpan = document.getElementById('total-alerts');
    const filteredAlertsSpan = document.getElementById('filtered-alerts');
    const locationRankingList = document.getElementById('location-ranking');

    let timelineChartInstance = null; // Chart.js インスタンスを保持するための変数


    // ----------------------------------------------------------------------
    // データ取得と描画の開始
    // ----------------------------------------------------------------------
    fetchAndRenderDashboardData();

    // ----------------------------------------------------------------------
    // メインデータ取得・描画関数
    // ----------------------------------------------------------------------
    async function fetchAndRenderDashboardData() {
        // 時系列データを取得
        await fetchTimelineData();
        // サマリーデータを取得
        await fetchSummaryData();
    }

    /**
     * 時系列データを取得し、グラフを描画する
     */
    async function fetchTimelineData() {
        try {
            const response = await fetch('/api/alerts/summary/timeline');
            if (!response.ok) {
                // HTTPエラーの場合、エラーメッセージを表示して終了
                throw new Error(`HTTPエラー! ステータス: ${response.status}`);
            }
            const rawData = await response.json(); // 例: [{"date_label": "2025-11-10", "count": 5}, ...]
            
            // ★★★ 修正: rawData (リスト) を Chart.js が理解できる形式に変換 ★★★
            const labels = rawData.map(item => item.date_label); // 日付 (ラベル) の配列を生成
            const counts = rawData.map(item => item.count);       // 件数 (データ) の配列を生成
            
            // グラフ描画関数を、整形されたデータで呼び出す
            renderTimelineChart({ labels, counts });

        } catch (error) {
            console.error('時系列データ取得エラー:', error);
            if (timelineChartCanvas) {
                const ctx = timelineChartCanvas.getContext('2d');
                ctx.clearRect(0, 0, timelineChartCanvas.width, timelineChartCanvas.height);
                timelineChartCanvas.parentElement.innerHTML = '<p style="color: red;">グラフデータの読み込みに失敗しました。</p>';
            }
        }
    }

    /**
     * サマリーデータを取得し、表示を更新する
     */
    async function fetchSummaryData() {
        try {
            const response = await fetch('/api/alerts/summary/filtered'); // フィルタリングはAPI側で実装
            if (!response.ok) {
                throw new Error(`HTTPエラー! ステータス: ${response.status}`);
            }
            const data = await response.json(); // 例: { "total_count": 100, "filtered_count": 50, "location_summary": [{"location": "A棟", "count": 20}, ...] }

            if (totalAlertsSpan) totalAlertsSpan.textContent = data.total_count || '0';
            if (filteredAlertsSpan) filteredAlertsSpan.textContent = data.filtered_count || '0';
            
            renderLocationRanking(data.location_summary || []);

        } catch (error) {
            console.error('サマリーデータ取得エラー:', error);
            if (totalAlertsSpan) totalAlertsSpan.textContent = 'エラー';
            if (filteredAlertsSpan) filteredAlertsSpan.textContent = 'エラー';
            if (locationRankingList) locationRankingList.innerHTML = '<li style="color: red;">エリアランキングの読み込みに失敗しました。</li>';
        }
    }

    // ----------------------------------------------------------------------
    // グラフ描画関数
    // ----------------------------------------------------------------------

    /**
     * 時系列グラフを描画する
     * @param {object} data - { labels: string[], counts: number[] }
     */
    function renderTimelineChart(data) {
        if (!timelineChartCanvas) return;

        // 既存のChart.jsインスタンスがあれば破棄
        if (timelineChartInstance) {
            timelineChartInstance.destroy();
        }

        const ctx = timelineChartCanvas.getContext('2d');
        timelineChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels, // 日付の配列
                datasets: [{
                    label: '検知件数',
                    data: data.counts, // 各日の検知件数
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    fill: true,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false, // 親要素のサイズに合わせて調整
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: '日付'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: '件数'
                        },
                        ticks: {
                            // y軸の目盛りを整数に限定
                            callback: function(value) {
                                if (Number.isInteger(value)) {
                                    return value;
                                }
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                    }
                }
            }
        });
    }

    /**
     * エリア別ランキングを表示する
     * @param {Array<object>} locationSummary - [{"location": "A棟", "count": 20}, ...]
     */
    function renderLocationRanking(locationSummary) {
        if (!locationRankingList) return;

        locationRankingList.innerHTML = ''; // クリア

        if (locationSummary.length === 0) {
            locationRankingList.innerHTML = '<li>データがありません。</li>';
            return;
        }

        // 件数が多い順にソート (上位5件のみ表示)
        locationSummary.sort((a, b) => b.count - a.count)
                       .slice(0, 5)
                       .forEach((item, index) => {
            const listItem = document.createElement('li');
            listItem.innerHTML = `<strong>${index + 1}. ${item.location || '不明な場所'}</strong>: ${item.count} 件`;
            locationRankingList.appendChild(listItem);
        });
    }

}); // DOMContentLoaded 終了