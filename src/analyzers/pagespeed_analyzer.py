"""
SEOマスターパッケージ - ページ速度分析モジュール

このモジュールは、Webサイトのページ読み込み速度を分析する機能を提供します。
ページサイズ、リソース数、画像最適化、キャッシュ設定、JavaScriptとCSSの最適化などを分析します。
"""

import logging
import json
import os
import re
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import urllib.parse
import hashlib

from src.core.analyzer import SEOAnalyzer

# ロギングの設定
logger = logging.getLogger(__name__)

class PageSpeedAnalyzer:
    """Webサイトのページ速度を分析するクラス"""
    
    def __init__(self, url):
        """
        PageSpeedAnalyzerクラスの初期化
        
        Args:
            url (str): 分析対象のURL
        """
        self.url = url
        self.seo_analyzer = SEOAnalyzer(url)
        self.domain = self.seo_analyzer.domain
        self.html = None
        self.soup = None
        self.resources = {
            'js': [],
            'css': [],
            'images': [],
            'fonts': [],
            'other': []
        }
        
        # データディレクトリの確認
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _fetch_page(self):
        """
        ページのHTMLを取得
        
        Returns:
            bool: 取得成功の場合はTrue、失敗の場合はFalse
        """
        if self.html:
            return True
            
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(self.url, headers=headers, timeout=30)
            response.raise_for_status()
            self.html = response.text
            self.soup = BeautifulSoup(self.html, 'html.parser')
            return True
        except Exception as e:
            logger.error(f"ページの取得に失敗しました: {str(e)}")
            return False
    
    def _get_absolute_url(self, url):
        """
        相対URLを絶対URLに変換
        
        Args:
            url (str): 変換する相対URL
            
        Returns:
            str: 絶対URL
        """
        if url.startswith('http://') or url.startswith('https://'):
            return url
        elif url.startswith('//'):
            return 'https:' + url
        elif url.startswith('/'):
            parsed_url = urllib.parse.urlparse(self.url)
            base = f"{parsed_url.scheme}://{parsed_url.netloc}"
            return base + url
        else:
            # 相対パスの場合
            parsed_url = urllib.parse.urlparse(self.url)
            path = parsed_url.path
            if not path.endswith('/'):
                path = path[:path.rfind('/')+1] if '/' in path else '/'
            base = f"{parsed_url.scheme}://{parsed_url.netloc}{path}"
            return base + url
    
    def _get_resource_size(self, url):
        """
        リソースのサイズを取得
        
        Args:
            url (str): リソースのURL
            
        Returns:
            int: リソースのサイズ（バイト）
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Range': 'bytes=0-0'  # まずヘッダーだけを取得してContent-Lengthを確認
            }
            response = requests.head(url, headers=headers, timeout=10)
            
            # Content-Lengthヘッダーがある場合
            if 'Content-Length' in response.headers:
                return int(response.headers['Content-Length'])
            
            # ヘッダーにサイズ情報がない場合は実際にダウンロード
            response = requests.get(url, headers={'User-Agent': headers['User-Agent']}, timeout=10, stream=True)
            response.raise_for_status()
            
            # ストリーミングでサイズを計算
            size = 0
            for chunk in response.iter_content(chunk_size=8192):
                size += len(chunk)
            
            return size
        except Exception as e:
            logger.warning(f"リソースサイズの取得に失敗しました: {url} - {str(e)}")
            return 0
    
    def _check_cache_headers(self, url):
        """
        キャッシュヘッダーを確認
        
        Args:
            url (str): 確認するURL
            
        Returns:
            dict: キャッシュヘッダー情報
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.head(url, headers=headers, timeout=10)
            
            cache_control = response.headers.get('Cache-Control', '')
            expires = response.headers.get('Expires', '')
            etag = response.headers.get('ETag', '')
            last_modified = response.headers.get('Last-Modified', '')
            
            has_cache_headers = bool(cache_control or expires or etag or last_modified)
            max_age = None
            
            if 'max-age=' in cache_control:
                max_age_match = re.search(r'max-age=(\d+)', cache_control)
                if max_age_match:
                    max_age = int(max_age_match.group(1))
            
            return {
                'has_cache_headers': has_cache_headers,
                'cache_control': cache_control,
                'expires': expires,
                'etag': etag,
                'last_modified': last_modified,
                'max_age': max_age
            }
        except Exception as e:
            logger.warning(f"キャッシュヘッダーの確認に失敗しました: {url} - {str(e)}")
            return {
                'has_cache_headers': False,
                'error': str(e)
            }
    
    def collect_resources(self):
        """
        ページ内のリソースを収集
        
        Returns:
            dict: 収集したリソース情報
        """
        if not self._fetch_page():
            return {'status': 'error', 'message': 'ページの取得に失敗しました'}
        
        # JavaScriptファイル
        for script in self.soup.find_all('script', src=True):
            src = script.get('src')
            if src:
                absolute_url = self._get_absolute_url(src)
                self.resources['js'].append({
                    'url': absolute_url,
                    'inline': False,
                    'async': script.get('async') is not None,
                    'defer': script.get('defer') is not None
                })
        
        # インラインJavaScript
        for script in self.soup.find_all('script', src=None):
            if script.string and len(script.string.strip()) > 0:
                # インラインスクリプトのハッシュを生成（識別用）
                script_hash = hashlib.md5(script.string.encode()).hexdigest()[:8]
                self.resources['js'].append({
                    'url': f"inline-script-{script_hash}",
                    'inline': True,
                    'size': len(script.string),
                    'minified': self._is_minified(script.string)
                })
        
        # CSSファイル
        for link in self.soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                absolute_url = self._get_absolute_url(href)
                self.resources['css'].append({
                    'url': absolute_url,
                    'inline': False
                })
        
        # インラインCSS
        for style in self.soup.find_all('style'):
            if style.string and len(style.string.strip()) > 0:
                # インラインスタイルのハッシュを生成（識別用）
                style_hash = hashlib.md5(style.string.encode()).hexdigest()[:8]
                self.resources['css'].append({
                    'url': f"inline-style-{style_hash}",
                    'inline': True,
                    'size': len(style.string),
                    'minified': self._is_minified(style.string)
                })
        
        # 画像
        for img in self.soup.find_all('img', src=True):
            src = img.get('src')
            if src and not src.startswith('data:'):
                absolute_url = self._get_absolute_url(src)
                width = img.get('width', '')
                height = img.get('height', '')
                
                self.resources['images'].append({
                    'url': absolute_url,
                    'width': width,
                    'height': height,
                    'has_dimensions': bool(width and height),
                    'lazy_loading': img.get('loading') == 'lazy'
                })
        
        # フォント
        for link in self.soup.find_all('link', rel='preload'):
            if link.get('as') == 'font':
                href = link.get('href')
                if href:
                    absolute_url = self._get_absolute_url(href)
                    self.resources['fonts'].append({
                        'url': absolute_url,
                        'preloaded': True
                    })
        
        # Google Fontsなどの外部フォント
        for link in self.soup.find_all('link'):
            href = link.get('href', '')
            if 'fonts.googleapis.com' in href or 'fonts.gstatic.com' in href:
                self.resources['fonts'].append({
                    'url': href,
                    'preloaded': link.get('rel') == 'preload'
                })
        
        # リソースのサイズと追加情報を取得
        for resource_type, resources in self.resources.items():
            for i, resource in enumerate(resources):
                if not resource.get('inline', False) and not resource.get('size', 0):
                    # 外部リソースのサイズを取得
                    size = self._get_resource_size(resource['url'])
                    self.resources[resource_type][i]['size'] = size
                    
                    # キャッシュヘッダーを確認
                    cache_info = self._check_cache_headers(resource['url'])
                    self.resources[resource_type][i]['cache'] = cache_info
        
        # 結果の作成
        result = {
            'status': 'ok',
            'resources': self.resources,
            'summary': {
                'js_count': len(self.resources['js']),
                'css_count': len(self.resources['css']),
                'images_count': len(self.resources['images']),
                'fonts_count': len(self.resources['fonts']),
                'total_resources': sum(len(resources) for resources in self.resources.values()),
                'js_size': sum(resource.get('size', 0) for resource in self.resources['js']),
                'css_size': sum(resource.get('size', 0) for resource in self.resources['css']),
                'images_size': sum(resource.get('size', 0) for resource in self.resources['images']),
                'fonts_size': sum(resource.get('size', 0) for resource in self.resources['fonts']),
                'total_size': sum(sum(resource.get('size', 0) for resource in resources) for resources in self.resources.values())
            }
        }
        
        return result
    
    def _is_minified(self, content):
        """
        コンテンツが最小化されているかを確認
        
        Args:
            content (str): 確認するコンテンツ
            
        Returns:
            bool: 最小化されている場合はTrue
        """
        if not content:
            return False
        
        # 改行の数をカウント
        newline_count = content.count('\n')
        
        # コンテンツの長さに対する改行の割合
        newline_ratio = newline_count / max(1, len(content))
        
        # 空白文字の割合
        whitespace_count = sum(1 for c in content if c.isspace())
        whitespace_ratio = whitespace_count / max(1, len(content))
        
        # 改行が少なく、空白文字の割合が低い場合は最小化されていると判断
        return newline_ratio < 0.01 and whitespace_ratio < 0.1
    
    def check_render_blocking_resources(self):
        """
        レンダリングをブロックするリソースを確認
        
        Returns:
            dict: レンダリングブロックリソース分析結果
        """
        if not self.resources['js'] and not self.resources['css']:
            # リソースが収集されていない場合は収集を実行
            self.collect_resources()
        
        # レンダリングをブロックするJavaScript
        blocking_js = []
        for resource in self.resources['js']:
            if not resource.get('inline', False) and not resource.get('async') and not resource.get('defer'):
                blocking_js.append(resource)
        
        # レンダリングをブロックするCSS
        blocking_css = []
        for resource in self.resources['css']:
            if not resource.get('inline', False):
                # メディアクエリがあるか確認
                media = resource.get('media', '')
                if not media or media == 'all' or media == 'screen':
                    blocking_css.append(resource)
        
        # 結果の作成
        return {
            'blocking_js_count': len(blocking_js),
            'blocking_css_count': len(blocking_css),
            'blocking_js': blocking_js[:5],  # 最初の5つのみ表示
            'blocking_css': blocking_css[:5],  # 最初の5つのみ表示
            'issues': [
                f'{len(blocking_js)}個のJavaScriptファイルがレンダリングをブロックしています' if blocking_js else None,
                f'{len(blocking_css)}個のCSSファイルがレンダリングをブロックしています' if blocking_css else None
            ],
            'recommendations': [
                'JavaScriptファイルにasyncまたはdefer属性を追加してください',
                'クリティカルCSSをインライン化し、残りのCSSを非同期で読み込んでください',
                'レンダリングに不要なJavaScriptは遅延読み込みしてください'
            ] if blocking_js or blocking_css else []
        }
    
    def check_image_optimization(self):
        """
        画像の最適化状況を確認
        
        Returns:
            dict: 画像最適化分析結果
        """
        if not self.resources['images']:
            # リソースが収集されていない場合は収集を実行
            self.collect_resources()
        
        # 最適化が必要な画像
        large_images = []
        missing_dimensions = []
        non_lazy_images = []
        
        for image in self.resources['images']:
            # サイズが大きい画像
            if image.get('size', 0) > 100 * 1024:  # 100KB以上
                large_images.append(image)
            
            # width/height属性がない画像
            if not image.get('has_dimensions', False):
                missing_dimensions.append(image)
            
            # 遅延読み込みが設定されていない画像
            if not image.get('lazy_loading', False):
                non_lazy_images.append(image)
        
        # 結果の作成
        return {
            'total_images': len(self.resources['images']),
            'large_images_count': len(large_images),
            'missing_dimensions_count': len(missing_dimensions),
            'non_lazy_images_count': len(non_lazy_images),
            'large_images': large_images[:5],  # 最初の5つのみ表示
            'missing_dimensions': missing_dimensions[:5],  # 最初の5つのみ表示
            'non_lazy_images': non_lazy_images[:5],  # 最初の5つのみ表示
            'issues': [
                f'{len(large_images)}個の画像が最適化されていない可能性があります' if large_images else None,
                f'{len(missing_dimensions)}個の画像にwidth/height属性が設定されていません' if missing_dimensions else None,
                f'{len(non_lazy_images)}個の画像に遅延読み込みが設定されていません' if non_lazy_images else None
            ],
            'recommendations': [
                '大きな画像は圧縮し、適切なフォーマット（WebP、AVIF）を使用してください',
                'すべての画像にwidth/height属性を設定して、レイアウトシフトを防止してください',
                'ファーストビュー外の画像には loading="lazy" 属性を追加してください',
                '画像のサイズを表示サイズに合わせて最適化してください'
            ] if large_images or missing_dimensions or non_lazy_images else []
        }
    
    def check_minification(self):
        """
        JavaScriptとCSSの最小化状況を確認
        
        Returns:
            dict: 最小化分析結果
        """
        if not self.resources['js'] and not self.resources['css']:
            # リソースが収集されていない場合は収集を実行
            self.collect_resources()
        
        # 最小化されていないJavaScript
        non_minified_js = []
        for resource in self.resources['js']:
            if resource.get('inline', False) and not resource.get('minified', False):
                non_minified_js.append(resource)
        
        # 最小化されていないCSS
        non_minified_css = []
        for resource in self.resources['css']:
            if resource.get('inline', False) and not resource.get('minified', False):
                non_minified_css.append(resource)
        
        # 結果の作成
        return {
            'non_minified_js_count': len(non_minified_js),
            'non_minified_css_count': len(non_minified_css),
            'non_minified_js': non_minified_js[:5],  # 最初の5つのみ表示
            'non_minified_css': non_minified_css[:5],  # 最初の5つのみ表示
            'issues': [
                f'{len(non_minified_js)}個のインラインJavaScriptが最小化されていません' if non_minified_js else None,
                f'{len(non_minified_css)}個のインラインCSSが最小化されていません' if non_minified_css else None
            ],
            'recommendations': [
                'JavaScriptとCSSを最小化して、ファイルサイズを削減してください',
                '本番環境では最小化ツール（Terser、CSSNano、UglifyJSなど）を使用してください'
            ] if non_minified_js or non_minified_css else []
        }
    
    def check_caching(self):
        """
        リソースのキャッシュ設定を確認
        
        Returns:
            dict: キャッシュ分析結果
        """
        if not self.resources['js'] and not self.resources['css'] and not self.resources['images']:
            # リソースが収集されていない場合は収集を実行
            self.collect_resources()
        
        # キャッシュヘッダーがないリソース
        non_cached_resources = []
        short_cache_resources = []
        
        for resource_type, resources in self.resources.items():
            if resource_type == 'other':
                continue
                
            for resource in resources:
                if not resource.get('inline', False):
                    cache_info = resource.get('cache', {})
                    
                    if not cache_info.get('has_cache_headers', False):
                        non_cached_resources.append({
                            'url': resource['url'],
                            'type': resource_type
                        })
                    elif cache_info.get('max_age') is not None and cache_info.get('max_age') < 86400:  # 1日未満
                        short_cache_resources.append({
                            'url': resource['url'],
                            'type': resource_type,
                            'max_age': cache_info.get('max_age')
                        })
        
        # 結果の作成
        return {
            'non_cached_count': len(non_cached_resources),
            'short_cache_count': len(short_cache_resources),
            'non_cached_resources': non_cached_resources[:5],  # 最初の5つのみ表示
            'short_cache_resources': short_cache_resources[:5],  # 最初の5つのみ表示
            'issues': [
                f'{len(non_cached_resources)}個のリソースにキャッシュヘッダーが設定されていません' if non_cached_resources else None,
                f'{len(short_cache_resources)}個のリソースのキャッシュ期間が短すぎます' if short_cache_resources else None
            ],
            'recommendations': [
                '静的リソース（JS、CSS、画像、フォント）には適切なキャッシュヘッダーを設定してください',
                '静的リソースには少なくとも1週間（604800秒）のキャッシュ期間を設定することを検討してください',
                'コンテンツが変更されたときに確実に更新されるよう、ファイル名にバージョンやハッシュを含めてください'
            ] if non_cached_resources or short_cache_resources else []
        }
    
    def analyze(self):
        """
        ページ速度分析を実行
        
        Returns:
            dict: ページ速度分析結果
        """
        logger.info(f"ページ速度分析を開始: {self.url}")
        
        # 分析開始時刻
        start_time = time.time()
        
        # リソースの収集
        resources_result = self.collect_resources()
        
        if resources_result.get('status') == 'error':
            return {
                'url': self.url,
                'domain': self.domain,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'analysis_duration': round(time.time() - start_time, 2),
                'status': 'error',
                'message': resources_result.get('message', 'リソースの収集に失敗しました')
            }
        
        # 各チェックを実行
        render_blocking_result = self.check_render_blocking_resources()
        image_optimization_result = self.check_image_optimization()
        minification_result = self.check_minification()
        caching_result = self.check_caching()
        
        # 総合スコアの計算
        score_components = []
        
        # ページサイズのスコア（20点満点）
        total_size_kb = resources_result['summary']['total_size'] / 1024
        if total_size_kb <= 500:  # 500KB以下
            score_components.append(20)
        elif total_size_kb <= 1000:  # 1MB以下
            score_components.append(15)
        elif total_size_kb <= 2000:  # 2MB以下
            score_components.append(10)
        elif total_size_kb <= 3000:  # 3MB以下
            score_components.append(5)
        else:
            score_components.append(0)
        
        # リソース数のスコア（15点満点）
        total_resources = resources_result['summary']['total_resources']
        if total_resources <= 20:
            score_components.append(15)
        elif total_resources <= 40:
            score_components.append(10)
        elif total_resources <= 60:
            score_components.append(5)
        else:
            score_components.append(0)
        
        # レンダリングブロックリソースのスコア（20点満点）
        blocking_resources = render_blocking_result['blocking_js_count'] + render_blocking_result['blocking_css_count']
        if blocking_resources == 0:
            score_components.append(20)
        elif blocking_resources <= 2:
            score_components.append(15)
        elif blocking_resources <= 5:
            score_components.append(10)
        elif blocking_resources <= 10:
            score_components.append(5)
        else:
            score_components.append(0)
        
        # 画像最適化のスコア（20点満点）
        image_issues = image_optimization_result['large_images_count'] + image_optimization_result['missing_dimensions_count']
        if image_issues == 0:
            score_components.append(20)
        else:
            # 画像の総数に対する問題のある画像の割合
            issue_ratio = min(1.0, image_issues / max(1, image_optimization_result['total_images']))
            score_components.append(max(0, 20 - int(issue_ratio * 20)))
        
        # キャッシュのスコア（15点満点）
        cache_issues = caching_result['non_cached_count'] + caching_result['short_cache_count']
        if cache_issues == 0:
            score_components.append(15)
        else:
            # リソースの総数に対するキャッシュ問題のあるリソースの割合
            cache_ratio = min(1.0, cache_issues / max(1, resources_result['summary']['total_resources']))
            score_components.append(max(0, 15 - int(cache_ratio * 15)))
        
        # 最小化のスコア（10点満点）
        minification_issues = minification_result['non_minified_js_count'] + minification_result['non_minified_css_count']
        if minification_issues == 0:
            score_components.append(10)
        else:
            score_components.append(max(0, 10 - minification_issues))
        
        # 総合スコアの計算
        total_score = sum(score_components)
        
        # ページ速度評価
        if total_score >= 90:
            speed_rating = '非常に高速'
        elif total_score >= 70:
            speed_rating = '高速'
        elif total_score >= 50:
            speed_rating = '普通'
        elif total_score >= 30:
            speed_rating = '遅い'
        else:
            speed_rating = '非常に遅い'
        
        # 推定読み込み時間（非常に大まかな推定）
        estimated_load_time = 0.5  # 基本的な接続時間とHTMLパース時間
        
        # リソースサイズに基づく推定
        estimated_load_time += total_size_kb / 1000  # 1MBあたり1秒と仮定
        
        # ブロッキングリソースに基づく追加時間
        estimated_load_time += blocking_resources * 0.1  # ブロッキングリソース1つあたり0.1秒
        
        # 分析結果の作成
        result = {
            'url': self.url,
            'domain': self.domain,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'analysis_duration': round(time.time() - start_time, 2),
            'page_speed_score': total_score,
            'speed_rating': speed_rating,
            'estimated_load_time': round(estimated_load_time, 2),
            'page_size': {
                'total_size_bytes': resources_result['summary']['total_size'],
                'total_size_kb': round(total_size_kb, 2),
                'js_size_kb': round(resources_result['summary']['js_size'] / 1024, 2),
                'css_size_kb': round(resources_result['summary']['css_size'] / 1024, 2),
                'images_size_kb': round(resources_result['summary']['images_size'] / 1024, 2),
                'fonts_size_kb': round(resources_result['summary']['fonts_size'] / 1024, 2)
            },
            'resources_count': {
                'total': resources_result['summary']['total_resources'],
                'js': resources_result['summary']['js_count'],
                'css': resources_result['summary']['css_count'],
                'images': resources_result['summary']['images_count'],
                'fonts': resources_result['summary']['fonts_count']
            },
            'render_blocking': render_blocking_result,
            'image_optimization': image_optimization_result,
            'minification': minification_result,
            'caching': caching_result,
            'summary': {
                'total_issues': sum(1 for issue in render_blocking_result.get('issues', []) + 
                                   image_optimization_result.get('issues', []) + 
                                   minification_result.get('issues', []) + 
                                   caching_result.get('issues', []) if issue)
            }
        }
        
        logger.info(f"ページ速度分析が完了しました: {self.url}")
        
        return result
