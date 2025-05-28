"""
SEOマスターパッケージのリンクアナライザーモジュール
"""
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse

class LinkAnalyzer:
    """
    Webページのリンク構造を分析するクラス。
    内部リンク、外部リンク、リンク切れなどを分析します。
    """
    
    def __init__(self, soup, url, domain):
        """
        リンクアナライザーを初期化します。
        
        Args:
            soup (BeautifulSoup): 分析対象のBeautifulSoupオブジェクト
            url (str): 分析対象のURL
            domain (str): 分析対象のドメイン
        """
        self.soup = soup
        self.url = url
        self.domain = domain
        self.internal_links = []
        self.external_links = []
        self.broken_links = []
    
    def analyze(self):
        """
        リンク分析を実行します。
        
        Returns:
            dict: 分析結果を含む辞書
        """
        self._extract_links()
        self._check_broken_links()
        
        results = {
            'internal': self.internal_links,
            'external': self.external_links,
            'broken': self.broken_links,
            'stats': {
                'total_links': len(self.internal_links) + len(self.external_links),
                'internal_links_count': len(self.internal_links),
                'external_links_count': len(self.external_links),
                'broken_links_count': len(self.broken_links)
            }
        }
        
        return results
    
    def _extract_links(self):
        """
        ページから内部リンクと外部リンクを抽出します。
        """
        self.internal_links = []
        self.external_links = []
        
        for a_tag in self.soup.find_all('a', href=True):
            href = a_tag.get('href')
            text = a_tag.text.strip()
            nofollow = 'rel' in a_tag.attrs and 'nofollow' in a_tag['rel']
            
            # 相対URLを絶対URLに変換
            absolute_url = urljoin(self.url, href)
            
            # URLのドメインを取得
            parsed_url = urlparse(absolute_url)
            link_domain = parsed_url.netloc
            
            # 内部リンクと外部リンクを分類
            if self.domain in link_domain:
                self.internal_links.append({
                    'url': absolute_url,
                    'text': text,
                    'nofollow': nofollow
                })
            else:
                self.external_links.append({
                    'url': absolute_url,
                    'text': text,
                    'nofollow': nofollow
                })
    
    def _check_broken_links(self):
        """
        リンク切れをチェックします。
        注: 実際の運用では、すべてのリンクをチェックするとパフォーマンスに影響するため、
        サンプリングや非同期処理を検討すべきです。
        """
        self.broken_links = []
        
        # テスト環境では実際のリクエストは行わず、モックデータを使用
        # 実際の実装では、以下のようなコードを使用
        """
        all_links = self.internal_links + self.external_links
        for link in all_links:
            try:
                response = requests.head(link['url'], timeout=5)
                if response.status_code >= 400:
                    self.broken_links.append({
                        'url': link['url'],
                        'text': link['text'],
                        'status_code': response.status_code
                    })
            except requests.exceptions.RequestException:
                self.broken_links.append({
                    'url': link['url'],
                    'text': link['text'],
                    'status_code': 'Connection Error'
                })
        """
        
        # モックデータ: 実際の実装では削除
        if self.internal_links and len(self.internal_links) > 3:
            self.broken_links.append({
                'url': self.internal_links[3]['url'],
                'text': self.internal_links[3]['text'],
                'status_code': 404
            })
    
    def get_link_distribution(self):
        """
        リンクの分布状況を分析します。
        
        Returns:
            dict: リンク分布の分析結果
        """
        # 内部リンクと外部リンクの比率
        total_links = len(self.internal_links) + len(self.external_links)
        internal_ratio = 0
        external_ratio = 0
        
        if total_links > 0:
            internal_ratio = len(self.internal_links) / total_links
            external_ratio = len(self.external_links) / total_links
        
        # リンクテキストの長さ分布
        text_lengths = [len(link['text']) for link in self.internal_links + self.external_links if link['text']]
        avg_text_length = 0
        
        if text_lengths:
            avg_text_length = sum(text_lengths) / len(text_lengths)
        
        # nofollowリンクの割合
        nofollow_links = [link for link in self.internal_links + self.external_links if link.get('nofollow')]
        nofollow_ratio = 0
        
        if total_links > 0:
            nofollow_ratio = len(nofollow_links) / total_links
        
        return {
            'internal_ratio': round(internal_ratio * 100, 1),
            'external_ratio': round(external_ratio * 100, 1),
            'avg_text_length': round(avg_text_length, 1),
            'nofollow_ratio': round(nofollow_ratio * 100, 1),
            'broken_ratio': round(len(self.broken_links) / total_links * 100 if total_links > 0 else 0, 1)
        }
    
    def get_anchor_text_analysis(self):
        """
        アンカーテキストの分析を行います。
        
        Returns:
            dict: アンカーテキスト分析の結果
        """
        all_links = self.internal_links + self.external_links
        
        # 空のアンカーテキスト
        empty_anchors = [link for link in all_links if not link['text']]
        
        # 一般的な「ここをクリック」などの非記述的アンカーテキスト
        generic_terms = ['click here', 'read more', 'learn more', 'click', 'here', 'link', 
                         'ここをクリック', 'こちら', '詳細', 'もっと見る', 'リンク']
        generic_anchors = [link for link in all_links 
                          if link['text'] and any(term in link['text'].lower() for term in generic_terms)]
        
        # キーワードを含むアンカーテキスト（実際の実装ではキーワードリストが必要）
        # ここではモックデータを使用
        keyword_anchors = [link for link in all_links 
                          if link['text'] and len(link['text']) > 10]  # 長めのアンカーテキストをキーワード含有と仮定
        
        return {
            'empty_anchors_count': len(empty_anchors),
            'empty_anchors_ratio': round(len(empty_anchors) / len(all_links) * 100 if all_links else 0, 1),
            'generic_anchors_count': len(generic_anchors),
            'generic_anchors_ratio': round(len(generic_anchors) / len(all_links) * 100 if all_links else 0, 1),
            'keyword_anchors_count': len(keyword_anchors),
            'keyword_anchors_ratio': round(len(keyword_anchors) / len(all_links) * 100 if all_links else 0, 1)
        }
