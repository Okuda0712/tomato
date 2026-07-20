document.addEventListener('DOMContentLoaded', () => {
    const changeButtons = document.querySelectorAll('.change-button');
    const formRows = document.querySelectorAll('.change-form-row');

    changeButtons.forEach(button => {
        button.addEventListener('click', () => {
            const accountId = button.dataset.account;
            const targetFormRow = document.querySelector(`.change-form-row[data-form="${accountId}"]`);
            
            if (!targetFormRow) return;

            // 1. 他の開いているフォームをすべて閉じる
            formRows.forEach(form => {
                if (form !== targetFormRow) {
                    form.classList.add('hidden');
                }
            });

            // 2. 対象のフォームの表示/非表示を切り替える
            const isHidden = targetFormRow.classList.contains('hidden');
            targetFormRow.classList.toggle('hidden');
            
            // 3. フォームが開かれた場合、その位置を調整する (オーバーレイ表示のため)
            if (!isHidden) {
                // クリックされたボタンの親の行 (アカウント名が表示されている行) を取得
                const clickedRow = button.closest('tr');
                
                // クリックされた行の高さ（tdの高さ）を取得
                const rowHeight = clickedRow.offsetHeight;
                
                // フォームの content 要素を取得
                const formContent = targetFormRow.querySelector('.change-form-content');

                // フォームコンテンツの上端が、クリックされた行の下の罫線に密着するように設定
                // top: 行の高さ - 1px (罫線分)
                formContent.style.top = `${rowHeight - 1}px`;
            }
        });
    });
});