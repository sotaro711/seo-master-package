"""
SEOマスターパッケージ - ユーティリティモジュール

このモジュールは、URL処理、HTMLパース、ファイル操作などの共通ユーティリティ関数を提供します。
"""

import os
import re
import logging
import json
import csv
import datetime
import urllib.parse
from urllib.parse import urlparse, urljoin
import tldextract
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

# ロギングの設定
logger = logging.getLogger(__name__)

class URLUtils:
    """URL処理に関するユーティリティクラス"""
    
    @staticmethod
    def normalize_url(url):
        """
        URLを正規化する
        
        Args:
            url (str): 正規化するURL
            
        Returns:
            str: 正規化されたURL
        """
        if not url:
            return ""
        
        # プロトコルがない場合はhttpsを追加
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # 末尾のスラッシュを削除
        if url.endswith('/'):
            url = url[:-1]
        
        # URLエンコーディングを修正
        parsed = urlparse(url)
        path = urllib.parse.unquote(parsed.path)
        path = urllib.parse.quote(path, safe='/()[]{}')
        
        # 正規化されたURLを再構築
        normalized = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc,
            path,
            parsed.params,
            parsed.query,
            parsed.fragment
        ))
        
        return normalized
    
    @staticmethod
    def get_domain(url):
        """
        URLからドメインを抽出する
        
        Args:
            url (str): ドメインを抽出するURL
            
        Returns:
            str: 抽出されたドメイン
        """
        if not url:
            return ""
        
        # tldextractを使用してドメイン情報を抽出
        extract = tldextract.extract(url)
        
        # サブドメインを含まないドメイン（例: example.com）
        domain = f"{extract.domain}.{extract.suffix}"
        
        return domain
    
    @staticmethod
    def get_full_domain(url):
        """
        URLからサブドメインを含む完全なドメインを抽出する
        
        Args:
            url (str): ドメインを抽出するURL
            
        Returns:
            str: 抽出された完全なドメイン
        """
        if not url:
            return ""
        
        # tldextractを使用してドメイン情報を抽出
        extract = tldextract.extract(url)
        
        # サブドメインを含む完全なドメイン（例: www.example.com）
        if extract.subdomain:
            full_domain = f"{extract.subdomain}.{extract.domain}.{extract.suffix}"
        else:
            full_domain = f"{extract.domain}.{extract.suffix}"
        
        return full_domain
    
    @staticmethod
    def is_internal_link(url, base_url):
        """
        URLが内部リンクかどうかを判定する
        
        Args:
            url (str): 判定するURL
            base_url (str): 基準となるURL
            
        Returns:
            bool: 内部リンクの場合はTrue、それ以外はFalse
        """
        if not url or not base_url:
            return False
        
        # 相対URLの場合は内部リンク
        if not url.startswith(('http://', 'https://')):
            return True
        
        # ドメインを比較
        base_domain = URLUtils.get_domain(base_url)
        url_domain = URLUtils.get_domain(url)
        
        return base_domain == url_domain
    
    @staticmethod
    def is_valid_url(url):
        """
        URLが有効かどうかを判定する
        
        Args:
            url (str): 判定するURL
            
        Returns:
            bool: 有効なURLの場合はTrue、それ以外はFalse
        """
        if not url:
            return False
        
        # URLのパターン
        pattern = re.compile(
            r'^(?:http|https)://'  # http:// または https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # ドメイン
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IPアドレス
            r'(?::\d+)?'  # ポート（オプション）
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return bool(pattern.match(url))
    
    @staticmethod
    def get_absolute_url(url, base_url):
        """
        相対URLを絶対URLに変換する
        
        Args:
            url (str): 変換するURL
            base_url (str): 基準となるURL
            
        Returns:
            str: 絶対URL
        """
        if not url or not base_url:
            return ""
        
        # URLが既に絶対URLの場合はそのまま返す
        if url.startswith(('http://', 'https://')):
            return url
        
        # URLがJavaScriptやメールリンクの場合はそのまま返す
        if url.startswith(('javascript:', 'mailto:', 'tel:')):
            return url
        
        # 相対URLを絶対URLに変換
        absolute_url = urljoin(base_url, url)
        
        return absolute_url
    
    @staticmethod
    def check_url_status(url, timeout=10):
        """
        URLのステータスをチェックする
        
        Args:
            url (str): チェックするURL
            timeout (int, optional): タイムアウト秒数
            
        Returns:
            dict: ステータス情報（status_code, is_redirect, redirect_url, response_time）
        """
        if not url:
            return {
                'status_code': None,
                'is_redirect': False,
                'redirect_url': None,
                'response_time': None,
                'error': 'URLが指定されていません'
            }
        
        try:
            # URLにリクエストを送信
            start_time = datetime.datetime.now()
            response = requests.head(url, allow_redirects=False, timeout=timeout)
            end_time = datetime.datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            # リダイレクトの確認
            is_redirect = 300 <= response.status_code < 400
            redirect_url = response.headers.get('Location') if is_redirect else None
            
            # 結果を返す
            return {
                'status_code': response.status_code,
                'is_redirect': is_redirect,
                'redirect_url': redirect_url,
                'response_time': response_time,
                'error': None
            }
        except RequestException as e:
            logger.error(f"URLステータスチェックエラー: {url} - {str(e)}")
            return {
                'status_code': None,
                'is_redirect': False,
                'redirect_url': None,
                'response_time': None,
                'error': str(e)
            }


class HTMLUtils:
    """HTML処理に関するユーティリティクラス"""
    
    @staticmethod
    def fetch_html(url, headers=None, timeout=30):
        """
        URLからHTMLを取得する
        
        Args:
            url (str): HTMLを取得するURL
            headers (dict, optional): リクエストヘッダー
            timeout (int, optional): タイムアウト秒数
            
        Returns:
            tuple: (HTML文字列, レスポンスオブジェクト)
        """
        if not url:
            return None, None
        
        # デフォルトのヘッダー
        if headers is None:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3'
            }
        
        try:
            # URLにリクエストを送信
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()  # エラーレスポンスの場合は例外を発生
            
            # エンコーディングを検出
            if response.encoding == 'ISO-8859-1':
                # エンコーディングが不明な場合はコンテンツから推測
                response.encoding = response.apparent_encoding
            
            return response.text, response
        except RequestException as e:
            logger.error(f"HTML取得エラー: {url} - {str(e)}")
            return None, None
    
    @staticmethod
    def parse_html(html):
        """
        HTML文字列をBeautifulSoupオブジェクトに変換する
        
        Args:
            html (str): 変換するHTML文字列
            
        Returns:
            BeautifulSoup: 変換されたBeautifulSoupオブジェクト
        """
        if not html:
            return None
        
        try:
            # HTMLをBeautifulSoupオブジェクトに変換
            soup = BeautifulSoup(html, 'html.parser')
            return soup
        except Exception as e:
            logger.error(f"HTML解析エラー: {str(e)}")
            return None
    
    @staticmethod
    def extract_text_from_element(element):
        """
        HTML要素からテキストを抽出する
        
        Args:
            element: テキストを抽出するHTML要素
            
        Returns:
            str: 抽出されたテキスト
        """
        if not element:
            return ""
        
        # 要素からテキストを抽出
        text = element.get_text(strip=True)
        
        # 連続する空白を1つに置換
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    @staticmethod
    def extract_meta_tags(soup):
        """
        HTMLからメタタグを抽出する
        
        Args:
            soup (BeautifulSoup): 抽出元のBeautifulSoupオブジェクト
            
        Returns:
            dict: 抽出されたメタタグ情報
        """
        if not soup:
            return {}
        
        meta_tags = {}
        
        # titleタグ
        title = soup.find('title')
        if title:
            meta_tags['title'] = title.get_text(strip=True)
        
        # metaタグ
        for meta in soup.find_all('meta'):
            # name属性を持つmetaタグ
            if meta.get('name'):
                meta_tags[meta.get('name').lower()] = meta.get('content', '')
            
            # property属性を持つmetaタグ（OGPなど）
            elif meta.get('property'):
                meta_tags[meta.get('property').lower()] = meta.get('content', '')
            
            # http-equiv属性を持つmetaタグ
            elif meta.get('http-equiv'):
                meta_tags[meta.get('http-equiv').lower()] = meta.get('content', '')
        
        # canonical URL
        canonical = soup.find('link', rel='canonical')
        if canonical:
            meta_tags['canonical'] = canonical.get('href', '')
        
        # hreflang
        hreflangs = []
        for hreflang in soup.find_all('link', rel='alternate', hreflang=True):
            hreflangs.append({
                'hreflang': hreflang.get('hreflang', ''),
                'href': hreflang.get('href', '')
            })
        
        if hreflangs:
            meta_tags['hreflang'] = hreflangs
        
        return meta_tags
    
    @staticmethod
    def extract_headings(soup):
        """
        HTMLから見出し要素を抽出する
        
        Args:
            soup (BeautifulSoup): 抽出元のBeautifulSoupオブジェクト
            
        Returns:
            dict: 抽出された見出し要素
        """
        if not soup:
            return {}
        
        headings = {
            'h1': [],
            'h2': [],
            'h3': [],
            'h4': [],
            'h5': [],
            'h6': []
        }
        
        # 各見出し要素を抽出
        for level in range(1, 7):
            tag = f'h{level}'
            for heading in soup.find_all(tag):
                headings[tag].append(HTMLUtils.extract_text_from_element(heading))
        
        return headings
    
    @staticmethod
    def extract_links(soup, base_url):
        """
        HTMLからリンクを抽出する
        
        Args:
            soup (BeautifulSoup): 抽出元のBeautifulSoupオブジェクト
            base_url (str): 基準となるURL
            
        Returns:
            dict: 抽出されたリンク情報
        """
        if not soup or not base_url:
            return {}
        
        links = {
            'internal': [],
            'external': [],
            'images': [],
            'scripts': [],
            'stylesheets': [],
            'social': []
        }
        
        # aタグのリンクを抽出
        for a in soup.find_all('a', href=True):
            href = a.get('href', '').strip()
            
            # JavaScriptやメールリンクは除外
            if href.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                continue
            
            # 相対URLを絶対URLに変換
            absolute_url = URLUtils.get_absolute_url(href, base_url)
            
            # リンクテキストを取得
            link_text = HTMLUtils.extract_text_from_element(a)
            
            # 内部リンクと外部リンクを分類
            if URLUtils.is_internal_link(absolute_url, base_url):
                links['internal'].append({
                    'url': absolute_url,
                    'text': link_text,
                    'rel': a.get('rel', ''),
                    'target': a.get('target', '')
                })
            else:
                # ソーシャルメディアリンクの判定
                domain = URLUtils.get_domain(absolute_url).lower()
                social_domains = ['facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com', 'youtube.com', 'pinterest.com']
                
                if any(social in domain for social in social_domains):
                    links['social'].append({
                        'url': absolute_url,
                        'text': link_text,
                        'platform': next((social.split('.')[0] for social in social_domains if social in domain), 'other')
                    })
                else:
                    links['external'].append({
                        'url': absolute_url,
                        'text': link_text,
                        'rel': a.get('rel', ''),
                        'target': a.get('target', '')
                    })
        
        # 画像を抽出
        for img in soup.find_all('img', src=True):
            src = img.get('src', '').strip()
            
            # 相対URLを絶対URLに変換
            absolute_url = URLUtils.get_absolute_url(src, base_url)
            
            links['images'].append({
                'url': absolute_url,
                'alt': img.get('alt', ''),
                'width': img.get('width', ''),
                'height': img.get('height', '')
            })
        
        # スクリプトを抽出
        for script in soup.find_all('script', src=True):
            src = script.get('src', '').strip()
            
            # 相対URLを絶対URLに変換
            absolute_url = URLUtils.get_absolute_url(src, base_url)
            
            links['scripts'].append({
                'url': absolute_url,
                'type': script.get('type', '')
            })
        
        # スタイルシートを抽出
        for link in soup.find_all('link', rel='stylesheet', href=True):
            href = link.get('href', '').strip()
            
            # 相対URLを絶対URLに変換
            absolute_url = URLUtils.get_absolute_url(href, base_url)
            
            links['stylesheets'].append({
                'url': absolute_url,
                'media': link.get('media', '')
            })
        
        return links
    
    @staticmethod
    def extract_images(soup, base_url):
        """
        HTMLから画像を抽出する
        
        Args:
            soup (BeautifulSoup): 抽出元のBeautifulSoupオブジェクト
            base_url (str): 基準となるURL
            
        Returns:
            list: 抽出された画像情報
        """
        if not soup or not base_url:
            return []
        
        images = []
        
        # imgタグを抽出
        for img in soup.find_all('img', src=True):
            src = img.get('src', '').strip()
            
            # 相対URLを絶対URLに変換
            absolute_url = URLUtils.get_absolute_url(src, base_url)
            
            # 画像情報を追加
            images.append({
                'url': absolute_url,
                'alt': img.get('alt', ''),
                'width': img.get('width', ''),
                'height': img.get('height', ''),
                'loading': img.get('loading', ''),
                'srcset': img.get('srcset', '')
            })
        
        # picture要素内のsourceタグを抽出
        for picture in soup.find_all('picture'):
            for source in picture.find_all('source', srcset=True):
                srcset = source.get('srcset', '').strip()
                
                # srcsetから最初のURLを抽出
                src_match = re.search(r'([^\s,]+)', srcset)
                if src_match:
                    src = src_match.group(1)
                    
                    # 相対URLを絶対URLに変換
                    absolute_url = URLUtils.get_absolute_url(src, base_url)
                    
                    # 画像情報を追加
                    images.append({
                        'url': absolute_url,
                        'media': source.get('media', ''),
                        'type': source.get('type', ''),
                        'srcset': srcset
                    })
        
        # 背景画像を持つ要素を抽出（スタイル属性から）
        for element in soup.find_all(style=True):
            style = element.get('style', '')
            
            # background-imageプロパティを検索
            bg_match = re.search(r'background-image\s*:\s*url\([\'"]?([^\'"()]+)[\'"]?\)', style)
            if bg_match:
                src = bg_match.group(1).strip()
                
                # 相対URLを絶対URLに変換
                absolute_url = URLUtils.get_absolute_url(src, base_url)
                
                # 画像情報を追加
                images.append({
                    'url': absolute_url,
                    'type': 'background',
                    'element': element.name
                })
        
        return images
    
    @staticmethod
    def extract_structured_data(soup):
        """
        HTMLから構造化データを抽出する
        
        Args:
            soup (BeautifulSoup): 抽出元のBeautifulSoupオブジェクト
            
        Returns:
            list: 抽出された構造化データ
        """
        if not soup:
            return []
        
        structured_data = []
        
        # application/ld+json形式の構造化データを抽出
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                structured_data.append({
                    'type': 'ld+json',
                    'data': data
                })
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"構造化データ解析エラー: {str(e)}")
        
        # microdata形式の構造化データを抽出（簡易版）
        for element in soup.find_all(itemscope=True):
            item_type = element.get('itemtype', '')
            if item_type:
                structured_data.append({
                    'type': 'microdata',
                    'itemtype': item_type
                })
        
        return structured_data


class FileUtils:
    """ファイル操作に関するユーティリティクラス"""
    
    @staticmethod
    def save_json(data, file_path, ensure_dir=True):
        """
        データをJSONファイルに保存する
        
        Args:
            data: 保存するデータ
            file_path (str): 保存先のファイルパス
            ensure_dir (bool, optional): ディレクトリが存在しない場合に作成するかどうか
            
        Returns:
            bool: 保存に成功した場合はTrue、それ以外はFalse
        """
        if ensure_dir:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"JSONファイル保存エラー: {file_path} - {str(e)}")
            return False
    
    @staticmethod
    def load_json(file_path):
        """
        JSONファイルからデータを読み込む
        
        Args:
            file_path (str): 読み込むファイルパス
            
        Returns:
            object: 読み込まれたデータ、エラーの場合はNone
        """
        if not os.path.exists(file_path):
            logger.error(f"JSONファイルが存在しません: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"JSONファイル読み込みエラー: {file_path} - {str(e)}")
            return None
    
    @staticmethod
    def save_csv(data, file_path, headers=None, ensure_dir=True):
        """
        データをCSVファイルに保存する
        
        Args:
            data (list): 保存するデータ（辞書のリスト）
            file_path (str): 保存先のファイルパス
            headers (list, optional): CSVのヘッダー（指定がない場合は最初の辞書のキーを使用）
            ensure_dir (bool, optional): ディレクトリが存在しない場合に作成するかどうか
            
        Returns:
            bool: 保存に成功した場合はTrue、それ以外はFalse
        """
        if not data:
            logger.error("CSVファイル保存エラー: データが空です")
            return False
        
        if ensure_dir:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        try:
            # ヘッダーが指定されていない場合は最初の辞書のキーを使用
            if headers is None and isinstance(data[0], dict):
                headers = list(data[0].keys())
            
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                
                # ヘッダーを書き込む
                if headers:
                    writer.writerow(headers)
                
                # データを書き込む
                for row in data:
                    if isinstance(row, dict) and headers:
                        # 辞書の場合はヘッダーの順序でデータを取得
                        writer.writerow([row.get(header, '') for header in headers])
                    else:
                        # リストの場合はそのまま書き込む
                        writer.writerow(row)
            
            return True
        except Exception as e:
            logger.error(f"CSVファイル保存エラー: {file_path} - {str(e)}")
            return False
    
    @staticmethod
    def load_csv(file_path, as_dict=True):
        """
        CSVファイルからデータを読み込む
        
        Args:
            file_path (str): 読み込むファイルパス
            as_dict (bool, optional): 辞書形式で読み込むかどうか
            
        Returns:
            list: 読み込まれたデータ、エラーの場合は空リスト
        """
        if not os.path.exists(file_path):
            logger.error(f"CSVファイルが存在しません: {file_path}")
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8', newline='') as f:
                if as_dict:
                    reader = csv.DictReader(f)
                    return list(reader)
                else:
                    reader = csv.reader(f)
                    return list(reader)
        except Exception as e:
            logger.error(f"CSVファイル読み込みエラー: {file_path} - {str(e)}")
            return []
    
    @staticmethod
    def ensure_directory(directory_path):
        """
        ディレクトリが存在することを確認し、存在しない場合は作成する
        
        Args:
            directory_path (str): 確認するディレクトリパス
            
        Returns:
            bool: ディレクトリが存在する（または作成された）場合はTrue、それ以外はFalse
        """
        try:
            os.makedirs(directory_path, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"ディレクトリ作成エラー: {directory_path} - {str(e)}")
            return False
    
    @staticmethod
    def get_file_extension(file_path):
        """
        ファイルパスから拡張子を取得する
        
        Args:
            file_path (str): 拡張子を取得するファイルパス
            
        Returns:
            str: 取得された拡張子（ドットを含まない）
        """
        return os.path.splitext(file_path)[1].lstrip('.')
    
    @staticmethod
    def generate_filename(prefix, extension, timestamp=True):
        """
        タイムスタンプを含むファイル名を生成する
        
        Args:
            prefix (str): ファイル名のプレフィックス
            extension (str): ファイルの拡張子（ドットを含まない）
            timestamp (bool, optional): タイムスタンプを含めるかどうか
            
        Returns:
            str: 生成されたファイル名
        """
        if timestamp:
            timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"{prefix}_{timestamp_str}.{extension}"
        else:
            return f"{prefix}.{extension}"
