"""
SEOマスターパッケージの技術的SEO分析モジュール
"""
import requests
import time
from bs4 import BeautifulSoup
import re

class TechnicalAnalyzer:
    """
    Webページの技術的SEO要素を分析するクラス。
    ステータスコード、レスポンス時間、モバイルフレンドリー、ページ速度などを分析します。
    """
    
    def __init__(self, url):
        """
        技術的アナライザーを初期化します。
        
        Args:
            url (str): 分析対象のURL
        """
        self.url = url
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        self.timeout = 30
        self.response = None
        self.response_time = None
        self.html_content = None
        self.soup = None
        
        # 初期データ取得
        self._fetch_data()
    
    def analyze(self):
        """
        技術的SEO分析を実行します。
        
        Returns:
            dict: 分析結果を含む辞書
        """
        results = {
            'status_code': self._get_status_code(),
            'response_time': self.response_time,
            'page_size': self._get_page_size(),
            'meta_tags': self._analyze_meta_tags(),
            'mobile_friendly': self._check_mobile_friendly(),
            'page_speed_factors': self._analyze_page_speed_factors(),
            'structured_data': self._detect_structured_data(),
            'security': self._check_security(),
            'accessibility': self._check_accessibility()
        }
        
        return results
    
    def _fetch_data(self):
        """
        URLからデータを取得します。
        """
        try:
            start_time = time.time()
            headers = {'User-Agent': self.user_agent}
            self.response = requests.get(self.url, headers=headers, timeout=self.timeout)
            self.response_time = round((time.time() - start_time) * 1000)  # ミリ秒単位
            
            if self.response.status_code == 200:
                self.html_content = self.response.text
                self.soup = BeautifulSoup(self.html_content, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL {self.url}: {e}")
            self.response = None
            self.response_time = None
    
    def _get_status_code(self):
        """
        HTTPステータスコードを取得します。
        
        Returns:
            int: HTTPステータスコード、エラーの場合は0
        """
        return self.response.status_code if self.response else 0
    
    def _get_page_size(self):
        """
        ページサイズを取得します。
        
        Returns:
            int: ページサイズ（バイト）
        """
        if self.response and self.html_content:
            return len(self.html_content)
        return 0
    
    def _analyze_meta_tags(self):
        """
        メタタグを分析します。
        
        Returns:
            dict: メタタグ分析結果
        """
        meta_tags = {
            'title': '',
            'description': '',
            'keywords': '',
            'robots': '',
            'viewport': '',
            'canonical': '',
            'og': {},
            'twitter': {}
        }
        
        if not self.soup:
            return meta_tags
        
        # タイトル
        title_tag = self.soup.find('title')
        if title_tag:
            meta_tags['title'] = title_tag.text.strip()
        
        # メタディスクリプション
        meta_desc = self.soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            meta_tags['description'] = meta_desc.get('content', '').strip()
        
        # メタキーワード
        meta_keywords = self.soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            meta_tags['keywords'] = meta_keywords.get('content', '').strip()
        
        # ロボッツ
        meta_robots = self.soup.find('meta', attrs={'name': 'robots'})
        if meta_robots:
            meta_tags['robots'] = meta_robots.get('content', '').strip()
        
        # ビューポート
        meta_viewport = self.soup.find('meta', attrs={'name': 'viewport'})
        if meta_viewport:
            meta_tags['viewport'] = meta_viewport.get('content', '').strip()
        
        # カノニカル
        canonical = self.soup.find('link', attrs={'rel': 'canonical'})
        if canonical:
            meta_tags['canonical'] = canonical.get('href', '').strip()
        
        # OGタグ
        for og_tag in self.soup.find_all('meta', attrs={'property': re.compile('^og:')}):
            property_name = og_tag.get('property', '').replace('og:', '')
            if property_name:
                meta_tags['og'][property_name] = og_tag.get('content', '').strip()
        
        # Twitterカード
        for twitter_tag in self.soup.find_all('meta', attrs={'name': re.compile('^twitter:')}):
            property_name = twitter_tag.get('name', '').replace('twitter:', '')
            if property_name:
                meta_tags['twitter'][property_name] = twitter_tag.get('content', '').strip()
        
        return meta_tags
    
    def _check_mobile_friendly(self):
        """
        モバイルフレンドリーをチェックします。
        
        Returns:
            dict: モバイルフレンドリー分析結果
        """
        results = {
            'viewport_present': False,
            'responsive_design': False,
            'touch_elements_size': False,
            'font_size': False,
            'content_width': False
        }
        
        if not self.soup:
            return results
        
        # ビューポートの存在チェック
        viewport = self.soup.find('meta', attrs={'name': 'viewport'})
        if viewport:
            viewport_content = viewport.get('content', '').lower()
            results['viewport_present'] = True
            
            # レスポンシブデザインのチェック
            if 'width=device-width' in viewport_content and 'initial-scale=1' in viewport_content:
                results['responsive_design'] = True
        
        # タッチ要素のサイズチェック（簡易版）
        small_elements = 0
        for a in self.soup.find_all('a'):
            # スタイル属性から幅と高さを抽出（実際にはもっと複雑な分析が必要）
            style = a.get('style', '')
            if 'width' in style and any(f"{i}px" in style for i in range(1, 40)):
                small_elements += 1
        
        results['touch_elements_size'] = small_elements == 0
        
        # フォントサイズのチェック（簡易版）
        small_fonts = 0
        for font_tag in self.soup.find_all(['font', 'span', 'p', 'div']):
            style = font_tag.get('style', '')
            if 'font-size' in style and any(f"{i}px" in style for i in range(1, 12)):
                small_fonts += 1
        
        results['font_size'] = small_fonts == 0
        
        # コンテンツ幅のチェック（簡易版）
        fixed_width = 0
        for div in self.soup.find_all('div'):
            style = div.get('style', '')
            if 'width' in style and 'px' in style and not '%' in style:
                fixed_width += 1
        
        results['content_width'] = fixed_width == 0
        
        return results
    
    def _analyze_page_speed_factors(self):
        """
        ページ速度要因を分析します。
        
        Returns:
            dict: ページ速度要因分析結果
        """
        results = {
            'html_size': 0,
            'image_count': 0,
            'image_size': 0,
            'script_count': 0,
            'script_size': 0,
            'css_count': 0,
            'css_size': 0,
            'total_requests': 0
        }
        
        if not self.soup or not self.html_content:
            return results
        
        # HTML サイズ
        results['html_size'] = len(self.html_content)
        
        # 画像数
        images = self.soup.find_all('img')
        results['image_count'] = len(images)
        
        # スクリプト数
        scripts = self.soup.find_all('script')
        results['script_count'] = len(scripts)
        
        # CSS数
        css_links = self.soup.find_all('link', attrs={'rel': 'stylesheet'})
        results['css_count'] = len(css_links)
        
        # 合計リクエスト数（推定）
        results['total_requests'] = 1 + results['image_count'] + results['script_count'] + results['css_count']
        
        return results
    
    def _detect_structured_data(self):
        """
        構造化データを検出します。
        
        Returns:
            dict: 構造化データ検出結果
        """
        results = {
            'json_ld': False,
            'microdata': False,
            'rdfa': False,
            'types': []
        }
        
        if not self.soup:
            return results
        
        # JSON-LD
        json_ld_scripts = self.soup.find_all('script', attrs={'type': 'application/ld+json'})
        if json_ld_scripts:
            results['json_ld'] = True
            
            # 簡易的な型抽出（実際にはJSONをパースして詳細分析が必要）
            for script in json_ld_scripts:
                content = script.string
                if content:
                    if '"@type"' in content:
                        type_match = re.search(r'"@type"\s*:\s*"([^"]+)"', content)
                        if type_match and type_match.group(1) not in results['types']:
                            results['types'].append(type_match.group(1))
        
        # Microdata
        microdata_elements = self.soup.find_all(attrs={'itemtype': True})
        if microdata_elements:
            results['microdata'] = True
            
            for element in microdata_elements:
                itemtype = element.get('itemtype', '')
                if itemtype and itemtype not in results['types']:
                    # URLから型名を抽出
                    type_name = itemtype.split('/')[-1]
                    if type_name:
                        results['types'].append(type_name)
        
        # RDFa
        rdfa_elements = self.soup.find_all(attrs={'typeof': True})
        if rdfa_elements:
            results['rdfa'] = True
            
            for element in rdfa_elements:
                typeof = element.get('typeof', '')
                if typeof and typeof not in results['types']:
                    results['types'].append(typeof)
        
        return results
    
    def _check_security(self):
        """
        セキュリティ要素をチェックします。
        
        Returns:
            dict: セキュリティチェック結果
        """
        results = {
            'https': False,
            'hsts': False,
            'content_security_policy': False,
            'x_content_type_options': False,
            'x_frame_options': False,
            'x_xss_protection': False
        }
        
        if not self.response:
            return results
        
        # HTTPS
        results['https'] = self.url.startswith('https://')
        
        # セキュリティヘッダー
        headers = self.response.headers
        
        # HSTS
        results['hsts'] = 'Strict-Transport-Security' in headers
        
        # Content-Security-Policy
        results['content_security_policy'] = 'Content-Security-Policy' in headers
        
        # X-Content-Type-Options
        results['x_content_type_options'] = 'X-Content-Type-Options' in headers
        
        # X-Frame-Options
        results['x_frame_options'] = 'X-Frame-Options' in headers
        
        # X-XSS-Protection
        results['x_xss_protection'] = 'X-XSS-Protection' in headers
        
        return results
    
    def _check_accessibility(self):
        """
        アクセシビリティ要素をチェックします。
        
        Returns:
            dict: アクセシビリティチェック結果
        """
        results = {
            'alt_attributes': 0,
            'aria_attributes': 0,
            'lang_attribute': False,
            'form_labels': 0
        }
        
        if not self.soup:
            return results
        
        # alt属性
        images = self.soup.find_all('img')
        images_with_alt = [img for img in images if img.get('alt') is not None]
        results['alt_attributes'] = len(images_with_alt) / len(images) if images else 1
        
        # ARIA属性
        aria_elements = self.soup.find_all(attrs=lambda attr: hasattr(attr, 'keys') and any(key.startswith('aria-') for key in attr.keys()))
        results['aria_attributes'] = len(aria_elements)
        
        # lang属性
        html_tag = self.soup.find('html')
        results['lang_attribute'] = html_tag and html_tag.get('lang') is not None
        
        # フォームラベル
        forms = self.soup.find_all('form')
        form_inputs = []
        for form in forms:
            form_inputs.extend(form.find_all(['input', 'textarea', 'select']))
        
        labeled_inputs = 0
        for input_element in form_inputs:
            input_id = input_element.get('id')
            if input_id:
                label = self.soup.find('label', attrs={'for': input_id})
                if label:
                    labeled_inputs += 1
            elif input_element.parent.name == 'label':
                labeled_inputs += 1
        
        results['form_labels'] = labeled_inputs / len(form_inputs) if form_inputs else 1
        
        return results
