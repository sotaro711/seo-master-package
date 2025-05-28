"""
SEOマスターパッケージ - モバイルフレンドリー分析モジュール

このモジュールは、Webサイトのモバイルフレンドリー性を分析する機能を提供します。
レスポンシブデザイン、ビューポート設定、タッチ要素のサイズと間隔、
フォントサイズ、コンテンツの幅などの要素を分析します。
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

from src.core.analyzer import SEOAnalyzer

# ロギングの設定
logger = logging.getLogger(__name__)

class MobileAnalyzer:
    """Webサイトのモバイルフレンドリー性を分析するクラス"""
    
    def __init__(self, url):
        """
        MobileAnalyzerクラスの初期化
        
        Args:
            url (str): 分析対象のURL
        """
        self.url = url
        self.seo_analyzer = SEOAnalyzer(url)
        self.domain = self.seo_analyzer.domain
        self.html = None
        self.soup = None
        
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
            # モバイルユーザーエージェントを使用
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
            }
            response = requests.get(self.url, headers=headers, timeout=30)
            response.raise_for_status()
            self.html = response.text
            self.soup = BeautifulSoup(self.html, 'html.parser')
            return True
        except Exception as e:
            logger.error(f"ページの取得に失敗しました: {str(e)}")
            return False
    
    def check_viewport(self):
        """
        ビューポートメタタグの確認
        
        Returns:
            dict: ビューポート分析結果
        """
        if not self._fetch_page():
            return {'status': 'error', 'message': 'ページの取得に失敗しました'}
        
        viewport_meta = self.soup.find('meta', attrs={'name': 'viewport'})
        
        if not viewport_meta:
            return {
                'status': 'error',
                'has_viewport': False,
                'message': 'ビューポートメタタグが設定されていません',
                'recommendation': 'ビューポートメタタグを追加してください: <meta name="viewport" content="width=device-width, initial-scale=1.0">'
            }
        
        viewport_content = viewport_meta.get('content', '')
        
        # 必要な設定が含まれているか確認
        has_width = 'width=device-width' in viewport_content or 'width=' in viewport_content
        has_initial_scale = 'initial-scale=' in viewport_content
        
        issues = []
        if not has_width:
            issues.append('width=device-widthが設定されていません')
        if not has_initial_scale:
            issues.append('initial-scaleが設定されていません')
        
        return {
            'status': 'ok' if has_width and has_initial_scale else 'warning',
            'has_viewport': True,
            'viewport_content': viewport_content,
            'has_width': has_width,
            'has_initial_scale': has_initial_scale,
            'issues': issues,
            'recommendation': '最適なビューポート設定: <meta name="viewport" content="width=device-width, initial-scale=1.0">' if issues else None
        }
    
    def check_responsive_design(self):
        """
        レスポンシブデザインの確認
        
        Returns:
            dict: レスポンシブデザイン分析結果
        """
        if not self._fetch_page():
            return {'status': 'error', 'message': 'ページの取得に失敗しました'}
        
        # メディアクエリの確認
        stylesheets = self.soup.find_all('link', rel='stylesheet')
        style_tags = self.soup.find_all('style')
        
        media_queries_count = 0
        
        # インラインスタイルタグ内のメディアクエリを確認
        for style in style_tags:
            if style.string and '@media' in style.string:
                media_queries_count += len(re.findall(r'@media', style.string))
        
        # 固定幅の要素を確認
        fixed_width_elements = []
        for element in self.soup.find_all(['div', 'table', 'section', 'article']):
            style = element.get('style', '')
            if style and ('width:' in style or 'width=' in style) and 'px' in style:
                # 幅が固定されている可能性がある要素
                if not any(term in style for term in ['max-width', 'min-width']):
                    width_match = re.search(r'width:\s*(\d+)px', style)
                    if width_match and int(width_match.group(1)) > 320:
                        fixed_width_elements.append({
                            'tag': element.name,
                            'style': style,
                            'width': width_match.group(1) + 'px'
                        })
        
        # 画像のレスポンシブ性を確認
        images = self.soup.find_all('img')
        non_responsive_images = []
        
        for img in images:
            style = img.get('style', '')
            width = img.get('width', '')
            
            # 固定幅の画像を検出
            if (style and 'width:' in style and 'px' in style and 'max-width' not in style) or \
               (width and width.isdigit() and int(width) > 320):
                non_responsive_images.append({
                    'src': img.get('src', ''),
                    'width': width or re.search(r'width:\s*(\d+)px', style).group(1) + 'px' if re.search(r'width:\s*(\d+)px', style) else 'unknown'
                })
        
        # フレキシブルグリッドの使用を確認
        has_grid = any('grid' in str(style) for style in style_tags) or \
                  any('flex' in str(style) for style in style_tags)
        
        # 結果の作成
        issues = []
        if media_queries_count == 0:
            issues.append('メディアクエリが検出されませんでした')
        if fixed_width_elements:
            issues.append(f'{len(fixed_width_elements)}個の固定幅要素が検出されました')
        if non_responsive_images:
            issues.append(f'{len(non_responsive_images)}個の非レスポンシブ画像が検出されました')
        if not has_grid:
            issues.append('フレキシブルグリッドまたはフレックスボックスが検出されませんでした')
        
        return {
            'status': 'ok' if not issues else 'warning',
            'media_queries_count': media_queries_count,
            'fixed_width_elements': fixed_width_elements[:5],  # 最初の5つのみ表示
            'fixed_width_elements_count': len(fixed_width_elements),
            'non_responsive_images': non_responsive_images[:5],  # 最初の5つのみ表示
            'non_responsive_images_count': len(non_responsive_images),
            'has_flexible_grid': has_grid,
            'issues': issues,
            'recommendations': [
                'メディアクエリを使用して異なる画面サイズに対応してください',
                '固定幅の代わりに相対単位（%、em、rem）を使用してください',
                '画像にmax-width: 100%を適用してレスポンシブにしてください',
                'フレキシブルグリッドまたはフレックスボックスを使用してレイアウトを構築してください'
            ] if issues else []
        }
    
    def check_touch_elements(self):
        """
        タッチ要素のサイズと間隔の確認
        
        Returns:
            dict: タッチ要素分析結果
        """
        if not self._fetch_page():
            return {'status': 'error', 'message': 'ページの取得に失敗しました'}
        
        # クリック可能な要素を取得
        clickable_elements = self.soup.find_all(['a', 'button', 'input', 'select', 'textarea'])
        
        small_elements = []
        for element in clickable_elements:
            style = element.get('style', '')
            
            # サイズが小さい要素を検出
            width_match = re.search(r'width:\s*(\d+)px', style)
            height_match = re.search(r'height:\s*(\d+)px', style)
            
            if width_match and int(width_match.group(1)) < 44:
                small_elements.append({
                    'tag': element.name,
                    'text': element.get_text()[:30] if element.get_text() else '',
                    'width': width_match.group(1) + 'px',
                    'height': height_match.group(1) + 'px' if height_match else 'unknown'
                })
            elif height_match and int(height_match.group(1)) < 44:
                small_elements.append({
                    'tag': element.name,
                    'text': element.get_text()[:30] if element.get_text() else '',
                    'width': width_match.group(1) + 'px' if width_match else 'unknown',
                    'height': height_match.group(1) + 'px'
                })
        
        # 結果の作成
        return {
            'status': 'ok' if not small_elements else 'warning',
            'clickable_elements_count': len(clickable_elements),
            'small_elements': small_elements[:5],  # 最初の5つのみ表示
            'small_elements_count': len(small_elements),
            'issues': [f'{len(small_elements)}個のタッチ要素が推奨サイズ（44x44px）より小さいです'] if small_elements else [],
            'recommendations': [
                'タッチ要素（ボタン、リンクなど）は少なくとも44x44ピクセルのサイズにしてください',
                'タッチ要素の間には十分な間隔（少なくとも8px）を確保してください'
            ] if small_elements else []
        }
    
    def check_font_size(self):
        """
        フォントサイズの確認
        
        Returns:
            dict: フォントサイズ分析結果
        """
        if not self._fetch_page():
            return {'status': 'error', 'message': 'ページの取得に失敗しました'}
        
        # フォントサイズが小さい要素を検出
        small_font_elements = []
        
        # インラインスタイルでフォントサイズが設定されている要素を確認
        for element in self.soup.find_all(['p', 'span', 'div', 'a', 'li', 'td']):
            style = element.get('style', '')
            if style and 'font-size:' in style:
                font_size_match = re.search(r'font-size:\s*(\d+)(px|pt|rem|em)', style)
                if font_size_match:
                    size = float(font_size_match.group(1))
                    unit = font_size_match.group(2)
                    
                    # 単位に応じて小さいフォントを判定
                    is_small = False
                    if unit == 'px' and size < 16:
                        is_small = True
                    elif unit == 'pt' and size < 12:
                        is_small = True
                    elif unit == 'rem' and size < 1:
                        is_small = True
                    elif unit == 'em' and size < 1:
                        is_small = True
                    
                    if is_small:
                        small_font_elements.append({
                            'tag': element.name,
                            'text': element.get_text()[:30] if element.get_text() else '',
                            'font_size': f"{size}{unit}"
                        })
        
        # 結果の作成
        return {
            'status': 'ok' if not small_font_elements else 'warning',
            'small_font_elements': small_font_elements[:5],  # 最初の5つのみ表示
            'small_font_elements_count': len(small_font_elements),
            'issues': [f'{len(small_font_elements)}個の要素が小さいフォントサイズを使用しています'] if small_font_elements else [],
            'recommendations': [
                'モバイルデバイスでの読みやすさを確保するために、本文テキストは少なくとも16px（または1rem）のフォントサイズを使用してください',
                'フォントサイズを指定する場合は、相対単位（rem、em）を使用することを検討してください'
            ] if small_font_elements else []
        }
    
    def check_content_width(self):
        """
        コンテンツの幅の確認
        
        Returns:
            dict: コンテンツ幅分析結果
        """
        if not self._fetch_page():
            return {'status': 'error', 'message': 'ページの取得に失敗しました'}
        
        # 水平スクロールが必要になる可能性のある要素を検出
        overflow_elements = []
        
        for element in self.soup.find_all(['div', 'table', 'section', 'article']):
            style = element.get('style', '')
            width_match = re.search(r'width:\s*(\d+)px', style)
            
            if width_match and int(width_match.group(1)) > 320:
                overflow_elements.append({
                    'tag': element.name,
                    'width': width_match.group(1) + 'px'
                })
        
        # テーブルの確認
        tables = self.soup.find_all('table')
        non_responsive_tables = []
        
        for table in tables:
            # テーブルがレスポンシブ対応されているか確認
            parent_div = table.find_parent('div')
            if parent_div:
                parent_style = parent_div.get('style', '')
                if 'overflow' not in parent_style and 'max-width' not in parent_style:
                    non_responsive_tables.append({
                        'id': table.get('id', ''),
                        'class': table.get('class', '')
                    })
            else:
                non_responsive_tables.append({
                    'id': table.get('id', ''),
                    'class': table.get('class', '')
                })
        
        # 結果の作成
        issues = []
        if overflow_elements:
            issues.append(f'{len(overflow_elements)}個の要素が画面幅を超える可能性があります')
        if non_responsive_tables:
            issues.append(f'{len(non_responsive_tables)}個のテーブルがレスポンシブ対応されていない可能性があります')
        
        return {
            'status': 'ok' if not issues else 'warning',
            'overflow_elements': overflow_elements[:5],  # 最初の5つのみ表示
            'overflow_elements_count': len(overflow_elements),
            'non_responsive_tables': non_responsive_tables[:5],  # 最初の5つのみ表示
            'non_responsive_tables_count': len(non_responsive_tables),
            'issues': issues,
            'recommendations': [
                'コンテンツが画面幅を超えないようにしてください',
                'テーブルをレスポンシブにするには、親要素に overflow-x: auto を設定してください',
                '固定幅の代わりに相対単位（%）を使用してください'
            ] if issues else []
        }
    
    def analyze(self):
        """
        モバイルフレンドリー分析を実行
        
        Returns:
            dict: モバイルフレンドリー分析結果
        """
        logger.info(f"モバイルフレンドリー分析を開始: {self.url}")
        
        # 分析開始時刻
        start_time = time.time()
        
        # 各チェックを実行
        viewport_result = self.check_viewport()
        responsive_result = self.check_responsive_design()
        touch_result = self.check_touch_elements()
        font_result = self.check_font_size()
        content_width_result = self.check_content_width()
        
        # 総合スコアの計算
        score_components = []
        
        # ビューポート設定のスコア（20点満点）
        if viewport_result.get('status') == 'ok':
            score_components.append(20)
        elif viewport_result.get('status') == 'warning':
            score_components.append(10)
        else:
            score_components.append(0)
        
        # レスポンシブデザインのスコア（30点満点）
        if responsive_result.get('status') == 'ok':
            score_components.append(30)
        elif responsive_result.get('status') == 'warning':
            # 問題の数に応じてスコアを減点
            issues_count = len(responsive_result.get('issues', []))
            score_components.append(max(0, 30 - issues_count * 7))
        else:
            score_components.append(0)
        
        # タッチ要素のスコア（20点満点）
        if touch_result.get('status') == 'ok':
            score_components.append(20)
        elif touch_result.get('status') == 'warning':
            # 小さい要素の割合に応じてスコアを計算
            small_ratio = touch_result.get('small_elements_count', 0) / max(1, touch_result.get('clickable_elements_count', 1))
            score_components.append(max(0, 20 - int(small_ratio * 100)))
        else:
            score_components.append(0)
        
        # フォントサイズのスコア（15点満点）
        if font_result.get('status') == 'ok':
            score_components.append(15)
        elif font_result.get('status') == 'warning':
            # 小さいフォント要素の数に応じてスコアを減点
            small_count = font_result.get('small_font_elements_count', 0)
            score_components.append(max(0, 15 - small_count))
        else:
            score_components.append(0)
        
        # コンテンツ幅のスコア（15点満点）
        if content_width_result.get('status') == 'ok':
            score_components.append(15)
        elif content_width_result.get('status') == 'warning':
            # 問題の数に応じてスコアを減点
            issues_count = len(content_width_result.get('issues', []))
            score_components.append(max(0, 15 - issues_count * 5))
        else:
            score_components.append(0)
        
        # 総合スコアの計算
        total_score = sum(score_components)
        
        # モバイルフレンドリー評価
        if total_score >= 90:
            mobile_friendly_status = '非常に良好'
        elif total_score >= 70:
            mobile_friendly_status = '良好'
        elif total_score >= 50:
            mobile_friendly_status = '改善の余地あり'
        else:
            mobile_friendly_status = '要改善'
        
        # 分析結果の作成
        result = {
            'url': self.url,
            'domain': self.domain,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'analysis_duration': round(time.time() - start_time, 2),
            'mobile_friendly_score': total_score,
            'mobile_friendly_status': mobile_friendly_status,
            'viewport': viewport_result,
            'responsive_design': responsive_result,
            'touch_elements': touch_result,
            'font_size': font_result,
            'content_width': content_width_result,
            'summary': {
                'passed_checks': sum(1 for r in [viewport_result, responsive_result, touch_result, font_result, content_width_result] if r.get('status') == 'ok'),
                'warning_checks': sum(1 for r in [viewport_result, responsive_result, touch_result, font_result, content_width_result] if r.get('status') == 'warning'),
                'failed_checks': sum(1 for r in [viewport_result, responsive_result, touch_result, font_result, content_width_result] if r.get('status') == 'error'),
                'total_issues': sum(len(r.get('issues', [])) for r in [viewport_result, responsive_result, touch_result, font_result, content_width_result])
            }
        }
        
        logger.info(f"モバイルフレンドリー分析が完了しました: {self.url}")
        
        return result
