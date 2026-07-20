// static/script3.js - レポートダッシュボード機能（全グラフ統合版）

// Chart.js インスタンスを保持するグローバル変数
let pieChartInstance = null;
let barChartInstance = null;
let timelineChartInstance = null;

// DOM要素の取得
const categorySelect = document.getElementById('category-select');
const yearInput = document.getElementById("date-filter-y");
const monthInput = document.getElementById("date-filter-m");
const dayInput = document.getElementById("date-filter-d");

// --- フィルターグラフ（円グラフ・棒グラフ）関連 ---

async function fetchAndDrawFilteredCharts() {
    const type = categorySelect ? categorySelect.value : '全体';
    const year = yearInput ? yearInput.value.trim() : '';
    const month = monthInput ? monthInput.value.trim() : '';
    const day = dayInput ? dayInput.value.trim() : '';
    
    const params = new URLSearchParams();
    if (type !== '全体') params.append('type', type);
    if (year) params.append('year', year);
    if (month) params.append('month', month);
    if (day) params.append('day', day);

    try {
        const response = await fetch(`/api/alerts/summary/filtered?${params.toString()}`);
        const data = await response.json();

        if (data.error) { throw new Error(data.error); }

        const totalAlerts = data.total_alerts || 0;
        const filteredAlerts = data.filtered_alerts || 0;
        const locationSummary = data.location_summary || [];

        let occurrenceRate = (totalAlerts > 0) ? (filteredAlerts / totalAlerts) * 100 : 0.0;
        
        // カウンターの更新
        if (document.getElementById('total-count')) { document.getElementById('total-count').textContent = totalAlerts; }
        if (document.getElementById('filtered-count')) { document.getElementById('filtered-count').textContent = filteredAlerts; }
        if (document.getElementById('occurrence-rate')) { document.getElementById('occurrence-rate').textContent = `${occurrenceRate.toFixed(1)}%`; }

        // グラフの描画
        drawPieChart(filteredAlerts, totalAlerts - filteredAlerts, type);
        drawBarChart(locationSummary);

    } catch (error) {
        console.error("フィルターグラフデータ取得エラー:", error);
    }
}

function drawPieChart(filteredCount, othersCount, filterType) {
    const ctx = document.getElementById('pieChart');
    if (!ctx) return;
    if (pieChartInstance) { pieChartInstance.destroy(); }

    const total = filteredCount + othersCount;
    const labels = total > 0 ? 
        [`${filterType} (${filteredCount}件)`, `その他 (${othersCount}件)`] : 
        ['データなし'];
    const data = total > 0 ? [filteredCount, othersCount] : [1];

    pieChartInstance = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: ['rgba(59, 130, 246, 0.8)', 'rgba(209, 213, 219, 0.8)'],
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.label || '';
                            if (context.parsed !== null && total > 0) {
                                const percentage = (context.parsed / total * 100).toFixed(1);
                                label += ` (${percentage}%)`;
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
}

function drawBarChart(locationSummary) {
    const ctx = document.getElementById('barChart');
    if (!ctx) return;
    if (barChartInstance) { barChartInstance.destroy(); }

    const labels = locationSummary.map(item => item.location || '不明');
    const counts = locationSummary.map(item => item.count);
    
    if (counts.length === 0) { labels.push('データなし'); counts.push(0); }

    barChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '検知件数',
                data: counts,
                backgroundColor: 'rgba(16, 185, 129, 0.7)',
                borderColor: 'rgba(16, 185, 129, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: '件数' },
                    ticks: { stepSize: 1 }
                },
                x: {
                    title: { display: true, text: '発生場所' }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

// --- 時系列グラフ（折れ線グラフ）関連 ---

const TIMELINE_API_URL = '/api/alerts/summary/timeline';

async function fetchAndDrawTimelineChart() {
    const ctx = document.getElementById('timelineChart');
    if (!ctx) return;
    if (timelineChartInstance) { timelineChartInstance.destroy(); }

    try {
        const response = await fetch(TIMELINE_API_URL);
        if (!response.ok) { throw new Error(`データ取得失敗: ${response.status}`); }
        
        const data = await response.json();

        const labels = data.map(item => item.date_label);
        const counts = data.map(item => item.count);

        timelineChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: '検知件数 (is_pest_disease=1)',
                    data: counts,
                    borderColor: 'rgba(239, 68, 68, 0.8)',
                    backgroundColor: 'rgba(239, 68, 68, 0.2)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: { display: true, text: '日付' },
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45,
                            callback: function(val, index) {
                                return index % 3 === 0 ? this.getLabelForValue(val) : null;
                            }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: '検知件数' },
                        ticks: { stepSize: 1 }
                    }
                },
                plugins: {
                    legend: { position: 'top' },
                    title: {
                        display: true,
                        text: '過去30日間の害虫/病気検知件数'
                    }
                }
            }
        });

    } catch (error) {
        console.error("時系列グラフデータ取得エラー:", error);
        if (ctx) ctx.innerHTML = '<p style="color: red; text-align: center;">時系列データの読み込みエラーが発生しました。</p>';
    }
}

// --- イベントリスナーと初期ロード ---

function setupAllEventListeners() {
    if (categorySelect) {
        categorySelect.addEventListener('change', fetchAndDrawFilteredCharts);
    }
    
    const allDateInputs = [yearInput, monthInput, dayInput].filter(i => i);
    allDateInputs.forEach(input => {
        input.addEventListener('input', (e) => {
            e.target.value = e.target.value.replace(/[^0-9]/g, '');
            fetchAndDrawFilteredCharts();
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    setupAllEventListeners();
    fetchAndDrawFilteredCharts();
    fetchAndDrawTimelineChart();
});
