import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# テスト対象のモジュールへのパスを追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.analyzers.content_analyzer import ContentAnalyzer

class TestContentAnalyzer(unittest.TestCase):
    """ContentAnalyzerの単体テスト"""

    def setUp(self):
        """テスト前の準備"""
        self.test_url = "https://example.com"
        # テスト用ディレクトリの作成
        os.makedirs(os.path.join(os.path.dirname(__file__), 'test_data'), exist_ok=True)
        
        # モックHTMLを作成
        with open(os.path.join(os.path.dirname(__file__), 'test_data', 'content_test.html'), 'w') as f:
            f.write("""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Content Analyzer Test</title>
                <meta name="description" content="Test page for content analyzer">
            </head>
            <body>
                <h1>Main Heading</h1>
                <p>This is the first paragraph with some content about SEO analysis.</p>
                <h2>Subheading 1</h2>
                <p>This is the second paragraph with more details about content analysis.</p>
                <p>This paragraph contains keywords like <strong>SEO</strong>, <strong>content</strong>, and <strong>analysis</strong>.</p>
                <h2>Subheading 2</h2>
                <p>Here's another paragraph with information about heading structure.</p>
                <ul>
                    <li>List item 1</li>
                    <li>List item 2</li>
                    <li>List item 3</li>
                </ul>
                <h3>Smaller heading</h3>
                <p>Final paragraph with some concluding text.</p>
                <img src="image1.jpg" alt="Test Image 1">
                <img src="image2.jpg" alt="Test Image 2">
            </body>
            </html>
            """)

    def tearDown(self):
        """テスト後のクリーンアップ"""
        # テスト用ファイルの削除
        test_file = os.path.join(os.path.dirname(__file__), 'test_data', 'content_test.html')
        if os.path.exists(test_file):
            os.remove(test_file)

    @patch('requests.get')
    def test_analyze_content(self, mock_get):
        """コンテンツ分析の基本機能テスト"""
        # requestsのモック設定
        mock_response = MagicMock()
        with open(os.path.join(os.path.dirname(__file__), 'test_data', 'content_test.html'), 'r') as f:
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
        self.assertTrue(result['word_count'] > 50)  # 少なくとも50単語はある
        self.assertEqual(result['paragraph_count'], 5)  # 5つの段落がある
        self.assertEqual(result['image_count'], 2)  # 2つの画像がある
        self.assertEqual(result['heading_count'], 4)  # 4つの見出しがある (h1, h2, h2, h3)
        
        # 見出し構造の検証
        self.assertEqual(len(result['headings']), 4)
        self.assertEqual(result['headings'][0]['level'], 1)
        self.assertEqual(result['headings'][0]['text'], 'Main Heading')
        self.assertEqual(result['headings'][1]['level'], 2)
        self.assertEqual(result['headings'][1]['text'], 'Subheading 1')
        self.assertEqual(result['headings'][2]['level'], 2)
        self.assertEqual(result['headings'][2]['text'], 'Subheading 2')
        self.assertEqual(result['headings'][3]['level'], 3)
        self.assertEqual(result['headings'][3]['text'], 'Smaller heading')

    @patch('requests.get')
    def test_content_quality_score(self, mock_get):
        """コンテンツ品質スコアのテスト"""
        # requestsのモック設定
        mock_response = MagicMock()
        with open(os.path.join(os.path.dirname(__file__), 'test_data', 'content_test.html'), 'r') as f:
            mock_response.text = f.read()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # ContentAnalyzerのテスト
        analyzer = ContentAnalyzer(self.test_url)
        result = analyzer.analyze()

        # コンテンツ品質スコアの検証
        self.assertIn('content_quality_score', result)
        self.assertTrue(0 <= result['content_quality_score'] <= 100)
        
        # スコアの計算ロジックの検証
        # 十分な単語数、適切な段落数、画像の存在、適切な見出し構造があるため、
        # スコアは少なくとも60以上であるべき
        self.assertTrue(result['content_quality_score'] >= 60)

    @patch('requests.get')
    def test_readability_analysis(self, mock_get):
        """読みやすさ分析のテスト"""
        # requestsのモック設定
        mock_response = MagicMock()
        with open(os.path.join(os.path.dirname(__file__), 'test_data', 'content_test.html'), 'r') as f:
            mock_response.text = f.read()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # ContentAnalyzerのテスト
        analyzer = ContentAnalyzer(self.test_url)
        result = analyzer.analyze()

        # 読みやすさ分析の検証
        self.assertIn('readability', result)
        self.assertIn('score', result['readability'])
        self.assertIn('grade_level', result['readability'])
        self.assertIn('assessment', result['readability'])
        
        # 読みやすさスコアの範囲検証
        self.assertTrue(0 <= result['readability']['score'] <= 100)

    @patch('requests.get')
    def test_keyword_extraction(self, mock_get):
        """キーワード抽出のテスト"""
        # requestsのモック設定
        mock_response = MagicMock()
        with open(os.path.join(os.path.dirname(__file__), 'test_data', 'content_test.html'), 'r') as f:
            mock_response.text = f.read()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # ContentAnalyzerのテスト
        analyzer = ContentAnalyzer(self.test_url)
        result = analyzer.analyze()

        # キーワード抽出の検証
        self.assertIn('keywords', result)
        self.assertTrue(len(result['keywords']) > 0)
        
        # 期待されるキーワードの検証
        keywords = [kw.lower() for kw in result['keywords']]
        self.assertTrue('seo' in keywords or 'analysis' in keywords or 'content' in keywords)

    @patch('requests.get')
    def test_error_handling(self, mock_get):
        """エラーハンドリングのテスト"""
        # 404エラーのモック設定
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # ContentAnalyzerのテスト
        analyzer = ContentAnalyzer(self.test_url)
        result = analyzer.analyze()

        # エラー時の結果の検証
        self.assertIsNotNone(result)
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'Failed to fetch URL: 404')

if __name__ == '__main__':
    unittest.main()
