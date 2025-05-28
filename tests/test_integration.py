import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# テスト対象のモジュールへのパスを追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.analyzer import SEOAnalyzer
from src.analyzers.content_analyzer import ContentAnalyzer
from src.analyzers.link_analyzer import LinkAnalyzer
from src.analyzers.technical_analyzer import TechnicalAnalyzer
from src.analyzers.keyword_analyzer import KeywordAnalyzer
from src.analyzers.ads_analyzer import AdsAnalyzer
from src.analyzers.mobile_analyzer import MobileAnalyzer
from src.analyzers.pagespeed_analyzer import PageSpeedAnalyzer
from src.api.search_console_api import SearchConsoleAnalyzer
from src.api.analytics_api import AnalyticsAnalyzer

class TestIntegration(unittest.TestCase):
    """SEOマスターパッケージの統合テスト"""

    def setUp(self):
        """テスト前の準備"""
        self.test_url = "https://example.com"
        # モックHTMLレスポンスを用意
        with open(os.path.join(os.path.dirname(__file__), 'test_data', 'mock_html.html'), 'w') as f:
            f.write("""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta name="description" content="This is a test page for SEO analysis">
                <title>Test Page for SEO Analysis</title>
                <link rel="canonical" href="https://example.com">
                <link rel="stylesheet" href="styles.css">
                <script src="script.js"></script>
            </head>
            <body>
                <header>
                    <h1>Welcome to Test Page</h1>
                    <nav>
                        <ul>
                            <li><a href="/">Home</a></li>
                            <li><a href="/about">About</a></li>
                            <li><a href="/contact">Contact</a></li>
                        </ul>
                    </nav>
                </header>
                <main>
                    <section>
                        <h2>About Our Services</h2>
                        <p>This is a paragraph about our services. We provide excellent services for our customers.</p>
                        <p>Keywords: SEO, analysis, testing, integration</p>
                        <img src="image1.jpg" alt="Service Image">
                    </section>
                    <section>
                        <h2>Our Products</h2>
                        <p>Check out our amazing products. They are the best in the market.</p>
                        <ul>
                            <li>Product 1</li>
                            <li>Product 2</li>
                            <li>Product 3</li>
                        </ul>
                        <a href="https://external-link.com">External Link</a>
                    </section>
                </main>
                <footer>
                    <p>&copy; 2025 Test Company</p>
                </footer>
            </body>
            </html>
            """)
        
        # テスト用ディレクトリの作成
        os.makedirs(os.path.join(os.path.dirname(__file__), 'test_data'), exist_ok=True)

    def tearDown(self):
        """テスト後のクリーンアップ"""
        # テスト用ファイルの削除
        mock_html_path = os.path.join(os.path.dirname(__file__), 'test_data', 'mock_html.html')
        if os.path.exists(mock_html_path):
            os.remove(mock_html_path)

    @patch('requests.get')
    def test_content_analyzer(self, mock_get):
        """ContentAnalyzerのテスト"""
        # requestsのモック設定
        mock_response = MagicMock()
        with open(os.path.join(os.path.dirname(__file__), 'test_data', 'mock_html.html'), 'r') as f:
            mock_response.text = f.read()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # ContentAnalyzerのテスト
        analyzer = ContentAnalyzer(self.test_url)
        result = analyzer.analyze()

        # 結果の検証
        self.assertIsNotNone(result)
        self.assertIn('word_count', result)
        self.assertIn('paragraph_count', result)
        self.assertIn('image_count', result)
        self.assertIn('heading_count', result)
        self.assertIn('headings', result)
        
        # 期待される値の検証
        self.assertTrue(result['word_count'] > 0)
        self.assertTrue(result['paragraph_count'] > 0)
        self.assertEqual(result['image_count'], 1)  # モックHTMLには1つの画像がある
        self.assertTrue(result['heading_count'] >= 3)  # h1, h2が少なくとも3つある

    @patch('requests.get')
    def test_link_analyzer(self, mock_get):
        """LinkAnalyzerのテスト"""
        # requestsのモック設定
        mock_response = MagicMock()
        with open(os.path.join(os.path.dirname(__file__), 'test_data', 'mock_html.html'), 'r') as f:
            mock_response.text = f.read()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # LinkAnalyzerのテスト
        analyzer = LinkAnalyzer(self.test_url)
        result = analyzer.analyze()

        # 結果の検証
        self.assertIsNotNone(result)
        self.assertIn('internal_links', result)
        self.assertIn('external_links', result)
        self.assertIn('broken_links', result)
        
        # 期待される値の検証
        self.assertTrue(len(result['internal_links']) >= 3)  # 少なくとも3つの内部リンクがある
        self.assertTrue(len(result['external_links']) >= 1)  # 少なくとも1つの外部リンクがある

    @patch('requests.get')
    def test_technical_analyzer(self, mock_get):
        """TechnicalAnalyzerのテスト"""
        # requestsのモック設定
        mock_response = MagicMock()
        with open(os.path.join(os.path.dirname(__file__), 'test_data', 'mock_html.html'), 'r') as f:
            mock_response.text = f.read()
        mock_response.status_code = 200
        mock_response.headers = {
            'Content-Type': 'text/html; charset=UTF-8',
            'Server': 'nginx',
            'X-Powered-By': 'PHP/7.4.3'
        }
        mock_get.return_value = mock_response

        # TechnicalAnalyzerのテスト
        analyzer = TechnicalAnalyzer(self.test_url)
        result = analyzer.analyze()

        # 結果の検証
        self.assertIsNotNone(result)
        self.assertIn('checks', result)
        self.assertTrue(len(result['checks']) > 0)
        
        # 各チェック項目の構造を検証
        for check in result['checks']:
            self.assertIn('name', check)
            self.assertIn('passed', check)
            self.assertIn('description', check)

    @patch('requests.get')
    def test_keyword_analyzer(self, mock_get):
        """KeywordAnalyzerのテスト"""
        # requestsのモック設定
        mock_response = MagicMock()
        with open(os.path.join(os.path.dirname(__file__), 'test_data', 'mock_html.html'), 'r') as f:
            mock_response.text = f.read()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # KeywordAnalyzerのテスト
        analyzer = KeywordAnalyzer(self.test_url)
        result = analyzer.analyze()

        # 結果の検証
        self.assertIsNotNone(result)
        self.assertIn('top_keywords', result)
        self.assertIn('keyword_density', result)
        self.assertTrue(len(result['top_keywords']) > 0)
        self.assertTrue(len(result['keyword_density']) > 0)
        
        # キーワードの構造を検証
        for keyword in result['top_keywords']:
            self.assertIn('text', keyword)
            self.assertIn('count', keyword)
            self.assertTrue(keyword['count'] > 0)

    @patch('requests.get')
    def test_ads_analyzer(self, mock_get):
        """AdsAnalyzerのテスト"""
        # requestsのモック設定
        mock_response = MagicMock()
        with open(os.path.join(os.path.dirname(__file__), 'test_data', 'mock_html.html'), 'r') as f:
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
        
        # スコアの範囲を検証
        self.assertTrue(0 <= result['ad_score'] <= 100)

    @patch('requests.get')
    def test_mobile_analyzer(self, mock_get):
        """MobileAnalyzerのテスト"""
        # requestsのモック設定
        mock_response = MagicMock()
        with open(os.path.join(os.path.dirname(__file__), 'test_data', 'mock_html.html'), 'r') as f:
            mock_response.text = f.read()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # MobileAnalyzerのテスト
        analyzer = MobileAnalyzer(self.test_url)
        result = analyzer.analyze()

        # 結果の検証
        self.assertIsNotNone(result)
        self.assertIn('mobile_friendly_score', result)
        self.assertIn('mobile_friendly_status', result)
        self.assertIn('summary', result)
        self.assertIn('viewport', result)
        self.assertIn('responsive_design', result)
        self.assertIn('touch_elements', result)
        self.assertIn('font_size', result)
        self.assertIn('content_width', result)
        
        # スコアの範囲を検証
        self.assertTrue(0 <= result['mobile_friendly_score'] <= 100)
        
        # ビューポート設定の検証
        self.assertIn('status', result['viewport'])
        self.assertIn('has_viewport', result['viewport'])
        self.assertTrue(result['viewport']['has_viewport'])  # モックHTMLにはビューポートメタタグがある

    @patch('requests.get')
    def test_pagespeed_analyzer(self, mock_get):
        """PageSpeedAnalyzerのテスト"""
        # requestsのモック設定
        mock_response = MagicMock()
        with open(os.path.join(os.path.dirname(__file__), 'test_data', 'mock_html.html'), 'r') as f:
            mock_response.text = f.read()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # PageSpeedAnalyzerのテスト
        analyzer = PageSpeedAnalyzer(self.test_url)
        result = analyzer.analyze()

        # 結果の検証
        self.assertIsNotNone(result)
        self.assertIn('page_speed_score', result)
        self.assertIn('speed_rating', result)
        self.assertIn('estimated_load_time', result)
        self.assertIn('page_size', result)
        self.assertIn('resources_count', result)
        self.assertIn('render_blocking', result)
        self.assertIn('image_optimization', result)
        self.assertIn('minification', result)
        self.assertIn('caching', result)
        
        # スコアの範囲を検証
        self.assertTrue(0 <= result['page_speed_score'] <= 100)
        
        # ページサイズの検証
        self.assertIn('total_size_kb', result['page_size'])
        self.assertIn('js_size_kb', result['page_size'])
        self.assertIn('css_size_kb', result['page_size'])
        self.assertIn('images_size_kb', result['page_size'])
        self.assertIn('fonts_size_kb', result['page_size'])

    @patch('requests.get')
    def test_search_console_analyzer(self, mock_get):
        """SearchConsoleAnalyzerのテスト"""
        # requestsのモック設定
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # SearchConsoleAnalyzerのテスト
        analyzer = SearchConsoleAnalyzer(self.test_url)
        result = analyzer.analyze()

        # 結果の検証
        self.assertIsNotNone(result)
        self.assertIn('search_performance', result)
        self.assertIn('index_coverage', result)
        self.assertIn('mobile_usability', result)
        self.assertIn('recommendations', result)
        
        # 検索パフォーマンスの検証
        self.assertIn('rating', result['search_performance'])
        self.assertIn('summary', result['search_performance'])
        self.assertIn('trends', result['search_performance'])
        self.assertIn('top_queries', result['search_performance'])
        self.assertIn('top_pages', result['search_performance'])
        self.assertIn('device_data', result['search_performance'])

    @patch('requests.get')
    def test_analytics_analyzer(self, mock_get):
        """AnalyticsAnalyzerのテスト"""
        # requestsのモック設定
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # AnalyticsAnalyzerのテスト
        analyzer = AnalyticsAnalyzer(self.test_url)
        result = analyzer.analyze()

        # 結果の検証
        self.assertIsNotNone(result)
        self.assertIn('traffic', result)
        self.assertIn('engagement', result)
        self.assertIn('pages', result)
        self.assertIn('events', result)
        self.assertIn('recommendations', result)
        
        # トラフィックデータの検証
        self.assertIn('rating', result['traffic'])
        self.assertIn('summary', result['traffic'])
        self.assertIn('trends', result['traffic'])
        self.assertIn('top_sources', result['traffic'])
        self.assertIn('devices', result['traffic'])

    @patch('requests.get')
    def test_seo_analyzer_integration(self, mock_get):
        """SEOAnalyzer統合テスト"""
        # requestsのモック設定
        mock_response = MagicMock()
        with open(os.path.join(os.path.dirname(__file__), 'test_data', 'mock_html.html'), 'r') as f:
            mock_response.text = f.read()
        mock_response.status_code = 200
        mock_response.headers = {
            'Content-Type': 'text/html; charset=UTF-8',
            'Server': 'nginx',
            'X-Powered-By': 'PHP/7.4.3'
        }
        mock_get.return_value = mock_response

        # SEOAnalyzerのテスト
        analyzer = SEOAnalyzer(self.test_url)
        result = analyzer.analyze()

        # 結果の検証
        self.assertIsNotNone(result)
        self.assertIn('url', result)
        self.assertIn('timestamp', result)
        self.assertIn('overall_score', result)
        self.assertIn('content_score', result)
        self.assertIn('technical_score', result)
        self.assertIn('link_score', result)
        self.assertIn('keyword_score', result)
        self.assertIn('meta_info', result)
        self.assertIn('content_analysis', result)
        self.assertIn('keyword_analysis', result)
        self.assertIn('link_analysis', result)
        self.assertIn('technical_analysis', result)
        self.assertIn('recommendations', result)
        
        # スコアの範囲を検証
        self.assertTrue(0 <= result['overall_score'] <= 100)
        self.assertTrue(0 <= result['content_score'] <= 100)
        self.assertTrue(0 <= result['technical_score'] <= 100)
        self.assertTrue(0 <= result['link_score'] <= 100)
        self.assertTrue(0 <= result['keyword_score'] <= 100)

    @patch('requests.get')
    def test_comprehensive_analysis(self, mock_get):
        """総合分析のテスト"""
        # requestsのモック設定
        mock_response = MagicMock()
        with open(os.path.join(os.path.dirname(__file__), 'test_data', 'mock_html.html'), 'r') as f:
            mock_response.text = f.read()
        mock_response.status_code = 200
        mock_response.headers = {
            'Content-Type': 'text/html; charset=UTF-8',
            'Server': 'nginx',
            'X-Powered-By': 'PHP/7.4.3'
        }
        mock_get.return_value = mock_response

        # 総合分析のテスト（メインスクリプトの関数をモック）
        from main import run_comprehensive_analysis
        result = run_comprehensive_analysis(self.test_url)

        # 結果の検証
        self.assertIsNotNone(result)
        self.assertIn('url', result)
        self.assertIn('timestamp', result)
        self.assertIn('comprehensive_score', result)
        self.assertIn('comprehensive_rating', result)
        self.assertIn('detailed_results', result)
        self.assertIn('recommendations', result)
        
        # 詳細結果の検証
        self.assertIn('seo', result['detailed_results'])
        self.assertIn('mobile', result['detailed_results'])
        self.assertIn('pagespeed', result['detailed_results'])
        
        # スコアの範囲を検証
        self.assertTrue(0 <= result['comprehensive_score'] <= 100)

if __name__ == '__main__':
    unittest.main()
