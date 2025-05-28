/**
 * SEOマスターツール JavaScript
 * 結果ページの動作を制御するスクリプト
 */

document.addEventListener('DOMContentLoaded', function() {
    // 詳細セクションの表示切り替え機能（総合分析用）
    window.toggleSection = function(sectionId) {
        const section = document.getElementById(sectionId);
        if (section) {
            // 現在の表示状態を確認
            const isVisible = section.style.display !== 'none';
            
            // すべてのセクションを非表示にする
            const allSections = document.querySelectorAll('.detailed-section');
            allSections.forEach(s => {
                s.style.display = 'none';
            });
            
            // クリックされたセクションの表示を切り替える
            if (!isVisible) {
                section.style.display = 'block';
                
                // スクロール位置を調整
                section.scrollIntoView({ behavior: 'smooth' });
            }
        }
    };
    
    // グラフやチャートの初期化（必要に応じて）
    initializeCharts();
    
    // 結果データの詳細表示の折りたたみ機能
    const expandButtons = document.querySelectorAll('.expand-button');
    expandButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                const isExpanded = targetElement.classList.contains('expanded');
                
                if (isExpanded) {
                    targetElement.classList.remove('expanded');
                    this.innerHTML = '<i class="fas fa-chevron-down"></i> 詳細を表示';
                } else {
                    targetElement.classList.add('expanded');
                    this.innerHTML = '<i class="fas fa-chevron-up"></i> 詳細を隠す';
                }
            }
        });
    });
});

// グラフやチャートの初期化関数
function initializeCharts() {
    // この関数は将来的にグラフライブラリを使用する場合に拡張可能
    console.log('Charts initialized');
}

// データテーブルのソート機能
function sortTable(tableId, columnIndex) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    let rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    switching = true;
    dir = "asc";
    
    while (switching) {
        switching = false;
        rows = table.rows;
        
        for (i = 1; i < (rows.length - 1); i++) {
            shouldSwitch = false;
            x = rows[i].getElementsByTagName("TD")[columnIndex];
            y = rows[i + 1].getElementsByTagName("TD")[columnIndex];
            
            // 数値としての比較を試みる
            const xContent = x.innerHTML.toLowerCase();
            const yContent = y.innerHTML.toLowerCase();
            
            let xValue = parseFloat(xContent);
            let yValue = parseFloat(yContent);
            
            // パースできない場合は文字列として比較
            if (isNaN(xValue) || isNaN(yValue)) {
                if (dir == "asc") {
                    if (xContent > yContent) {
                        shouldSwitch = true;
                        break;
                    }
                } else if (dir == "desc") {
                    if (xContent < yContent) {
                        shouldSwitch = true;
                        break;
                    }
                }
            } else {
                // 数値として比較
                if (dir == "asc") {
                    if (xValue > yValue) {
                        shouldSwitch = true;
                        break;
                    }
                } else if (dir == "desc") {
                    if (xValue < yValue) {
                        shouldSwitch = true;
                        break;
                    }
                }
            }
        }
        
        if (shouldSwitch) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
            switchcount++;
        } else {
            if (switchcount == 0 && dir == "asc") {
                dir = "desc";
                switching = true;
            }
        }
    }
    
    // ソート方向インジケータの更新
    const headers = table.getElementsByTagName("TH");
    for (i = 0; i < headers.length; i++) {
        // 既存のソートインジケータを削除
        headers[i].classList.remove("sort-asc", "sort-desc");
    }
    
    // 新しいソートインジケータを追加
    headers[columnIndex].classList.add(dir === "asc" ? "sort-asc" : "sort-desc");
}

// 印刷機能
function printResults() {
    window.print();
}

// PDFエクスポート機能（将来的な実装のためのプレースホルダー）
function exportToPDF() {
    alert('PDF出力機能は近日公開予定です。');
}
