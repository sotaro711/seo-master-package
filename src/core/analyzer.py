"""
SEOマスターパッケージのコアアナライザーモジュール
"""
import requests
from bs4 import BeautifulSoup
import tldextract
import time
from datetime import datetime

class SEOAnalyzer:
    """
    SEO分析の中核となるクラス。
    URLを受け取り、そのページのSEO関連の様々な側面を分析します。
    """
    
    def __init__(self, url):
        """
        SEOアナライザーを初期化します。
        
        Args:
            url (str): 分析対象のURL
        """
        self.url = url
        self.domain = self._extract_domain(url)
        self.html_content = self._fetch_content()
        self.soup = BeautifulSoup(self.html_content, 'html.parser')
        
        # 各種アナライザーの初期化
        from src.analyzers.content_analyzer import ContentAnalyzer
        from src.analyzers.link_analyzer import LinkAnalyzer
        from src.analyzers.technical_analyzer import TechnicalAnalyzer
        from src.analyzers.keyword_analyzer import KeywordAnalyzer

        self.content_analyzer = ContentAnalyzer(self.soup) # content_analyzer を初期化
        self.link_analyzer = LinkAnalyzer(self.soup, self.url, self.domain)
        self.technical_analyzer = TechnicalAnalyzer(self.url)
        self.keyword_analyzer = KeywordAnalyzer(self.soup, self)
    
    def analyze(self):
        """
        URLのSEO分析を実行します。
        
        Returns:
            dict: 分析結果を含む辞書
        """
        start_time = time.time()
        
        # 各アナライザーから結果を取得
        content_analysis = self.content_analyzer.analyze()
        link_analysis = self.link_analyzer.analyze()
        technical_analysis = self.technical_analyzer.analyze()
        keyword_analysis = self.keyword_analyzer.analyze_advanced()
        
        # 分析結果を統合
        results = {
            'url': self.url,
            'domain': self.domain,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'content_analysis': content_analysis,
            'link_analysis': link_analysis,
            'technical_analysis': technical_analysis,
            'keyword_analysis': keyword_analysis
        }
        
        # 処理時間を追加
        results['processing_time'] = round(time.time() - start_time, 2)
        
        return results
    
    def _fetch_content(self):
        """
        URLからHTMLコンテンツを取得します。
        
        Returns:
            str: HTMLコンテンツ
        """
        try:
            response = requests.get(self.url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL {self.url}: {e}")
            return ""
    
    def _extract_domain(self, url):
        """
        URLからドメイン名を抽出します。
        
        Args:
            url (str): 抽出対象のURL
            
        Returns:
            str: ドメイン名
        """
        if url is None:
            return ""
            
        try:
            extracted = tldextract.extract(url)
            return f"{extracted.domain}.{extracted.suffix}"
        except Exception as e:
            print(f"Error extracting domain from {url}: {e}")
            return ""
            
    def get_headings(self):
        """HTMLから見出しタグ (h1-h6) とそのテキストを抽出します。"""
        headings = {'h1': [], 'h2': [], 'h3': [], 'h4': [], 'h5': [], 'h6': []}
        if not self.soup:
            print("Warning: Soup object is not available for heading extraction.")
            return headings
        try:
            for i in range(1, 7):
                tag_name = f'h{i}'
                found_tags = self.soup.find_all(tag_name)
                for tag in found_tags:
                    # タグが存在し、テキストコンテンツがある場合のみ追加
                    text = tag.get_text(strip=True)
                    if text:
                         headings[tag_name].append(text)
        except Exception as e:
            print(f"Error extracting headings: {e}")
        return headings
