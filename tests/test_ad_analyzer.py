import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# テスト対象のモジュールへのパスを追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.analyzers.ads_analyzer import AdsAnalyzer

class TestAdsAnalyzer(unittest.TestCase):
    """AdsAnalyzerの単体テスト"""

    def setUp(self):
        """テスト前の準備"""
        self.test_url = "https://example.com"
        # テスト用ディレクトリの作成
        os.makedirs(os.path.join(os.path.dirname(__file__), 'test_data'), exist_ok=True)
        
        # モックHTMLを作成
        with open(os.path.join(os.path.dirname(__file__), 'test_data', 'ads_test.html'), 'w') as f:
            f.write("""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Ads Analyzer Test</title>
                <script async src="https://www.googletagmanager.com/gtag/js?id=G-12345"></script>
                <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
                <script>
                    (adsbygoogle = window.adsbygoogle || []).push({
                        google_ad_client: "ca-pub-1234567890",
                        enable_page_level_ads: true
                    });
                </script>
            </head>
            <body>
                <h1>Test Page with Ads</h1>
                <div class="content">
                    <p>This is a test page for ad analysis.</p>
                    
                    <!-- Google Ad -->
                    <ins class="adsbygoogle"
                        style="display:block"
                        data-ad-client="ca-pub-1234567890"
                        data-ad-slot="1234567890"
                        data-ad-format="auto"></ins>
                    
                    <p>More content here...</p>
                    
                    <!-- Facebook Ad -->
                    <div class="fb-ad" data-placementid="123456789" data-format="rectangle" data-testmode="true"></div>
                    
                    <p>Even more content...</p>
                    
                    <!-- Another Google Ad -->
                    <ins class="adsbygoogle"
                        style="display:inline-block;width:728px;height:90px"
                        data-ad-client="ca-pub-1234567890"
                        data-ad-slot="9876543210"></ins>
                </div>
                
                <div class="sidebar">
                    <!-- Twitter Ad -->
                    <div id="twitter-ad" class="twitter-ad-container" data-widget-id="123456"></div>
                </div>
                
                <footer>
                    <p>Footer content</p>
                </footer>
            </body>
            </html>
            """)

    def tearDown(self):
        """テスト後のクリーンアップ"""
        # テスト用ファイルの削除
        test_file = os.path.join(os.path.dirname(__file__), 'test_data', 'ads_test.html')
        if os.path.exists(test_file):
            os.remove(test_file)

    @patch('requests.get')
    def test_analyze_ads(self, mock_get):
        """広告分析の基本機能テスト"""
        # requestsのモック設定
        mock_response = MagicMock()
        with open(os.path.join(os.path.dirname(__file__), 'test_data', 'ads_test.html'), 'r') as f:
            mock_response.text = f.read()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # AdsAnalyzerのテスト
        analyzer = AdsAnalyzer(self.test_url)
        result = analyzer.analyze()

        # 結果の検証
        self.assertIsNotNone(result)
        self.assertIn('ad_score', result)
        self.assertIn('ad_count', result)
        self.assertIn('ad_networks', result)
        self.assertIn('ad_keywords', result)
        self.assertIn('ad_text_patterns', result)
        self.assertIn('ad_samples', result)
        self.assertIn('recommendations', result)
        
        # 広告数の検証
        self.assertTrue(result['ad_count'] >= 3)  # 少なくとも3つの広告がある
        
        # 広告ネットワークの検証
        networks = [network['name'].lower() for network in result['ad_networks']]
        self.assertTrue('google' in networks)  # Googleの広告が検出されるべき
        
        # スコアの範囲検証
        self.assertTrue(0 <= result['ad_score'] <= 100)

    @patch('requests.get')
    def test_ad_networks_detection(self, mock_get):
        """広告ネットワーク検出のテスト"""
        # requestsのモック設定
        mock_response = MagicMock()
        with open(os.path.join(os.path.dirname(__file__), 'test_data', 'ads_test.html'), 'r') as f:
            mock_response.text = f.read()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # AdsAnalyzerのテスト
        analyzer = AdsAnalyzer(self.test_url)
        result = analyzer.analyze()

        # 広告ネットワークの検証
        self.assertTrue(len(result['ad_networks']) >= 2)  # 少なくとも2つのネットワークがある
        
        # 各ネットワークの構造検証
        for network in result['ad_networks']:
            self.assertIn('name', network)
            self.assertIn('percentage', network)
            self.assertTrue(0 <= network['percentage'] <= 100)

    @patch('requests.get')
    def test_ad_samples_extraction(self, mock_get):
        """広告サンプル抽出のテスト"""
        # requestsのモック設定
        mock_response = MagicMock()
        with open(os.path.join(os.path.dirname(__file__), 'test_data', 'ads_test.html'), 'r') as f:
            mock_response.text = f.read()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # AdsAnalyzerのテスト
        analyzer = AdsAnalyzer(self.test_url)
        result = analyzer.analyze()

        # 広告サンプルの検証
        self.assertTrue(len(result['ad_samples']) > 0)
        
        # サンプルの構造検証
        for sample in result['ad_samples']:
            self.assertIn('type', sample)
            self.assertIn('network', sample)
            if 'headline' in sample:
                self.assertIsNotNone(sample['headline'])
            if 'description' in sample:
                self.assertIsNotNone(sample['description'])

    @patch('requests.get')
    def test_recommendations_generation(self, mock_get):
        """改善提案生成のテスト"""
        # requestsのモック設定
        mock_response = MagicMock()
        with open(os.path.join(os.path.dirname(__file__), 'test_data', 'ads_test.html'), 'r') as f:
            mock_response.text = f.read()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # AdsAnalyzerのテスト
        analyzer = AdsAnalyzer(self.test_url)
        result = analyzer.analyze()

        # 改善提案の検証
        self.assertTrue(len(result['recommendations']) > 0)
        for recommendation in result['recommendations']:
            self.assertIsInstance(recommendation, str)
            self.assertTrue(len(recommendation) > 0)

    @patch('requests.get')
    def test_error_handling(self, mock_get):
        """エラーハンドリングのテスト"""
        # 404エラーのモック設定
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # AdsAnalyzerのテスト
        analyzer = AdsAnalyzer(self.test_url)
        result = analyzer.analyze()

        # エラー時の結果の検証
        self.assertIsNotNone(result)
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'Failed to fetch URL: 404')

if __name__ == '__main__':
    unittest.main()
