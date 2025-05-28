/**
 * SEOマスターツール JavaScript
 * メインページの動作を制御するスクリプト
 */

document.addEventListener('DOMContentLoaded', function() {
    // ツール選択の処理
    const toolCards = document.querySelectorAll('.tool-card');
    const analysisTypeInput = document.getElementById('analysis_type');
    
    // 各機能説明カードの取得
    const featureCards = {
        'seo': document.getElementById('seo-features'),
        'ad': document.getElementById('ad-features'),
        'mobile': document.getElementById('mobile-features'),
        'pagespeed': document.getElementById('pagespeed-features'),
        'searchconsole': document.getElementById('searchconsole-features'),
        'analytics': document.getElementById('analytics-features'),
        'comprehensive': document.getElementById('comprehensive-features')
    };
    
    toolCards.forEach(card => {
        card.addEventListener('click', function() {
            // アクティブなカードのクラスを削除
            toolCards.forEach(c => c.classList.remove('active'));
            
            // クリックされたカードをアクティブにする
            this.classList.add('active');
            
            // 分析タイプを設定
            const toolType = this.getAttribute('data-tool');
            analysisTypeInput.value = toolType;
            
            // すべての機能カードを非表示にする
            Object.values(featureCards).forEach(card => {
                if (card) card.style.display = 'none';
            });
            
            // 選択された分析タイプの機能カードを表示する
            if (featureCards[toolType]) {
                featureCards[toolType].style.display = 'block';
            }
        });
    });
    
    // フォームのバリデーション
    const analysisForm = document.querySelector('.analysis-form form');
    
    if (analysisForm) {
        analysisForm.addEventListener('submit', function(event) {
            const urlInput = document.getElementById('url');
            const url = urlInput.value.trim();
            
            // URLの基本的な検証
            if (!url) {
                event.preventDefault();
                showError('URLを入力してください');
                return;
            }
            
            // URLの形式チェック
            if (!isValidUrl(url)) {
                event.preventDefault();
                showError('有効なURLを入力してください（例: https://example.com）');
                return;
            }
            
            // 分析タイプに応じたメッセージを表示
            const analysisType = analysisTypeInput.value;
            let loadingMessage = '分析中...';
            
            switch (analysisType) {
                case 'comprehensive':
                    loadingMessage = '総合分析中... (完了まで数分かかる場合があります)';
                    break;
                case 'mobile':
                    loadingMessage = 'モバイルフレンドリー分析中...';
                    break;
                case 'pagespeed':
                    loadingMessage = 'ページ速度分析中...';
                    break;
                case 'searchconsole':
                    loadingMessage = 'Search Console分析中...';
                    break;
                case 'analytics':
                    loadingMessage = 'Analytics分析中...';
                    break;
                case 'ad':
                    loadingMessage = '広告分析中...';
                    break;
                default:
                    loadingMessage = 'SEO分析中...';
            }
            
            // 分析開始時のローディング表示
            showLoading(loadingMessage);
        });
    }
    
    // URLの検証関数
    function isValidUrl(url) {
        try {
            const parsedUrl = new URL(url);
            return ['http:', 'https:'].includes(parsedUrl.protocol);
        } catch (e) {
            return false;
        }
    }
    
    // エラーメッセージの表示
    function showError(message) {
        // 既存のエラーメッセージを削除
        const existingError = document.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
        
        // 新しいエラーメッセージを作成
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `<p>${message}</p>`;
        
        // フォームの前に挿入
        analysisForm.parentNode.insertBefore(errorDiv, analysisForm);
    }
    
    // ローディング表示
    function showLoading(message) {
        // 送信ボタンを無効化
        const submitButton = document.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        submitButton.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${message}`;
        
        // フォーム全体を薄暗くする
        analysisForm.style.opacity = '0.7';
        analysisForm.style.pointerEvents = 'none';
    }
});
