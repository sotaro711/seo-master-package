"""
SEOマスターパッケージ - Google Search Console連携モジュール

このモジュールは、Google Search Consoleとの連携機能を提供します。
検索パフォーマンス、インデックスカバレッジ、モバイルユーザビリティなどのデータを取得し分析します。
"""

import logging
import json
import os
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from urllib.parse import urlparse

# モックモードでの動作のため、実際のGoogle APIクライアントはコメントアウト
# from googleapiclient.discovery import build
# from google.oauth2.credentials import Credentials

from src.core.analyzer import SEOAnalyzer

# ロギングの設定
logger = logging.getLogger(__name__)

class SearchConsoleAnalyzer:
    """Google Search Consoleと連携してデータを分析するクラス"""
    
    def __init__(self, url, credentials_file=None, mock_mode=True):
        """
        SearchConsoleAnalyzerクラスの初期化
        
        Args:
            url (str): 分析対象のURL
            credentials_file (str, optional): Google API認証情報ファイルのパス
            mock_mode (bool, optional): モックモードを使用するかどうか（APIキーがない場合など）
        """
        self.url = url
        self.seo_analyzer = SEOAnalyzer(url)
        self.domain = self.seo_analyzer.domain
        self.credentials_file = credentials_file
        self.mock_mode = mock_mode
        self.service = None
        
        # データディレクトリの確認
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # モックモードでない場合はGoogle APIクライアントを初期化
        if not self.mock_mode and self.credentials_file:
            self._init_service()
    
    def _init_service(self):
        """Google Search Console APIサービスを初期化"""
        try:
            # 実際の実装では以下のコードを使用
            # credentials = Credentials.from_authorized_user_file(self.credentials_file)
            # self.service = build('searchconsole', 'v1', credentials=credentials)
            pass
        except Exception as e:
            logger.error(f"Google Search Console APIの初期化に失敗しました: {str(e)}")
            self.mock_mode = True
    
    def get_search_performance(self, days=28, dimensions=None):
        """
        検索パフォーマンスデータを取得
        
        Args:
            days (int, optional): 取得する日数（過去何日分か）
            dimensions (list, optional): 分析ディメンション（'query', 'page', 'device', 'country', 'date'）
            
        Returns:
            dict: 検索パフォーマンスデータ
        """
        if not dimensions:
            dimensions = ['query']
        
        if self.mock_mode:
            # モックデータを返す
            logger.info("モックモードでSearch Consoleデータを生成します")
            
            # 日付範囲の設定
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            # クエリのモックデータ
            mock_queries = [
                self.domain,
                f"{self.domain} ログイン",
                f"{self.domain} 評判",
                f"{self.domain} 料金",
                f"{self.domain} 使い方",
                "SEO対策",
                "ウェブサイト最適化",
                "検索エンジン対策",
                "コンテンツマーケティング",
                "キーワード分析",
                "被リンク分析",
                "モバイルフレンドリー",
                "ページ速度最適化",
                "構造化データ",
                "メタタグ最適化"
            ]
            
            # ページのモックデータ
            mock_pages = [
                self.url,
                f"{self.url}about/",
                f"{self.url}services/",
                f"{self.url}contact/",
                f"{self.url}blog/",
                f"{self.url}blog/seo-tips/",
                f"{self.url}blog/content-marketing/",
                f"{self.url}blog/keyword-research/",
                f"{self.url}products/",
                f"{self.url}faq/"
            ]
            
            # デバイスのモックデータ
            mock_devices = ['MOBILE', 'DESKTOP', 'TABLET']
            
            # 国のモックデータ
            mock_countries = ['jp', 'us', 'cn', 'kr', 'gb', 'fr', 'de', 'ca', 'au', 'sg']
            
            # 日付ごとのデータを生成
            date_range = pd.date_range(start=start_date, end=end_date)
            date_data = []
            
            for date in date_range:
                date_str = date.strftime('%Y-%m-%d')
                clicks = np.random.randint(10, 100)
                impressions = clicks * np.random.randint(5, 20)
                ctr = round(clicks / max(1, impressions) * 100, 2)
                position = round(np.random.uniform(1.0, 20.0), 1)
                
                date_data.append({
                    'date': date_str,
                    'clicks': clicks,
                    'impressions': impressions,
                    'ctr': ctr,
                    'position': position
                })
            
            # ディメンションごとのデータを生成
            dimension_data = []
            
            if 'query' in dimensions:
                for query in mock_queries:
                    clicks = np.random.randint(5, 50)
                    impressions = clicks * np.random.randint(5, 15)
                    ctr = round(clicks / max(1, impressions) * 100, 2)
                    position = round(np.random.uniform(1.0, 30.0), 1)
                    
                    dimension_data.append({
                        'dimension_type': 'query',
                        'dimension_value': query,
                        'clicks': clicks,
                        'impressions': impressions,
                        'ctr': ctr,
                        'position': position
                    })
            
            if 'page' in dimensions:
                for page in mock_pages:
                    clicks = np.random.randint(5, 50)
                    impressions = clicks * np.random.randint(5, 15)
                    ctr = round(clicks / max(1, impressions) * 100, 2)
                    position = round(np.random.uniform(1.0, 20.0), 1)
                    
                    dimension_data.append({
                        'dimension_type': 'page',
                        'dimension_value': page,
                        'clicks': clicks,
                        'impressions': impressions,
                        'ctr': ctr,
                        'position': position
                    })
            
            if 'device' in dimensions:
                total_clicks = sum(item['clicks'] for item in date_data)
                total_impressions = sum(item['impressions'] for item in date_data)
                
                # デバイス別の割合を設定
                device_ratios = {'MOBILE': 0.6, 'DESKTOP': 0.35, 'TABLET': 0.05}
                
                for device in mock_devices:
                    ratio = device_ratios.get(device, 0.1)
                    clicks = int(total_clicks * ratio)
                    impressions = int(total_impressions * ratio)
                    ctr = round(clicks / max(1, impressions) * 100, 2)
                    position = round(np.random.uniform(1.0, 20.0), 1)
                    
                    dimension_data.append({
                        'dimension_type': 'device',
                        'dimension_value': device,
                        'clicks': clicks,
                        'impressions': impressions,
                        'ctr': ctr,
                        'position': position
                    })
            
            if 'country' in dimensions:
                total_clicks = sum(item['clicks'] for item in date_data)
                total_impressions = sum(item['impressions'] for item in date_data)
                
                # 日本が最も多いと仮定
                country_clicks = total_clicks
                country_impressions = total_impressions
                
                for country in mock_countries:
                    if country == 'jp':
                        ratio = 0.7
                    else:
                        ratio = 0.3 / (len(mock_countries) - 1)
                    
                    clicks = int(country_clicks * ratio)
                    impressions = int(country_impressions * ratio)
                    ctr = round(clicks / max(1, impressions) * 100, 2)
                    position = round(np.random.uniform(1.0, 20.0), 1)
                    
                    dimension_data.append({
                        'dimension_type': 'country',
                        'dimension_value': country,
                        'clicks': clicks,
                        'impressions': impressions,
                        'ctr': ctr,
                        'position': position
                    })
            
            # 総計を計算
            total_clicks = sum(item['clicks'] for item in date_data)
            total_impressions = sum(item['impressions'] for item in date_data)
            avg_ctr = round(total_clicks / max(1, total_impressions) * 100, 2)
            avg_position = round(sum(item['position'] for item in date_data) / len(date_data), 1)
            
            # トレンドを計算
            if len(date_data) > 1:
                first_half = date_data[:len(date_data)//2]
                second_half = date_data[len(date_data)//2:]
                
                first_half_clicks = sum(item['clicks'] for item in first_half)
                second_half_clicks = sum(item['clicks'] for item in second_half)
                clicks_trend = round((second_half_clicks - first_half_clicks) / max(1, first_half_clicks) * 100, 1)
                
                first_half_impressions = sum(item['impressions'] for item in first_half)
                second_half_impressions = sum(item['impressions'] for item in second_half)
                impressions_trend = round((second_half_impressions - first_half_impressions) / max(1, first_half_impressions) * 100, 1)
                
                first_half_position = sum(item['position'] for item in first_half) / len(first_half)
                second_half_position = sum(item['position'] for item in second_half) / len(second_half)
                position_trend = round(first_half_position - second_half_position, 1)  # 位置は小さい方が良いので、減少していれば正の値
            else:
                clicks_trend = 0
                impressions_trend = 0
                position_trend = 0
            
            # 結果の作成
            result = {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'dimensions': dimensions,
                'totals': {
                    'clicks': total_clicks,
                    'impressions': total_impressions,
                    'ctr': avg_ctr,
                    'position': avg_position
                },
                'trends': {
                    'clicks': clicks_trend,
                    'impressions': impressions_trend,
                    'position': position_trend
                },
                'date_data': date_data,
                'dimension_data': dimension_data
            }
            
            return result
        else:
            # 実際のAPIを使用してデータを取得（実装が必要）
            # ここでは例としてモックデータを返す
            logger.warning("Google Search Console APIが実装されていません。モックデータを返します。")
            return self.get_search_performance(days, dimensions)
    
    def get_index_coverage(self):
        """
        インデックスカバレッジデータを取得
        
        Returns:
            dict: インデックスカバレッジデータ
        """
        if self.mock_mode:
            # モックデータを返す
            logger.info("モックモードでインデックスカバレッジデータを生成します")
            
            # インデックス状態のモックデータ
            total_urls = np.random.randint(100, 1000)
            
            # 各状態のURLの割合
            valid_ratio = np.random.uniform(0.7, 0.95)
            excluded_ratio = np.random.uniform(0.01, 0.1)
            error_ratio = np.random.uniform(0.01, 0.1)
            warning_ratio = 1 - valid_ratio - excluded_ratio - error_ratio
            
            valid_count = int(total_urls * valid_ratio)
            excluded_count = int(total_urls * excluded_ratio)
            error_count = int(total_urls * error_ratio)
            warning_count = total_urls - valid_count - excluded_count - error_count
            
            # エラーの種類
            error_types = [
                {'type': 'server_error', 'count': int(error_count * 0.3)},
                {'type': 'redirect_error', 'count': int(error_count * 0.2)},
                {'type': 'not_found', 'count': int(error_count * 0.4)},
                {'type': 'other', 'count': error_count - int(error_count * 0.3) - int(error_count * 0.2) - int(error_count * 0.4)}
            ]
            
            # 除外の理由
            excluded_types = [
                {'type': 'robots_txt', 'count': int(excluded_count * 0.5)},
                {'type': 'noindex', 'count': int(excluded_count * 0.3)},
                {'type': 'canonical', 'count': int(excluded_count * 0.1)},
                {'type': 'other', 'count': excluded_count - int(excluded_count * 0.5) - int(excluded_count * 0.3) - int(excluded_count * 0.1)}
            ]
            
            # 警告の種類
            warning_types = [
                {'type': 'duplicate_content', 'count': int(warning_count * 0.4)},
                {'type': 'soft_404', 'count': int(warning_count * 0.3)},
                {'type': 'mobile_usability', 'count': int(warning_count * 0.2)},
                {'type': 'other', 'count': warning_count - int(warning_count * 0.4) - int(warning_count * 0.3) - int(warning_count * 0.2)}
            ]
            
            # 結果の作成
            result = {
                'total_urls': total_urls,
                'valid': {
                    'count': valid_count,
                    'percentage': round(valid_count / total_urls * 100, 1)
                },
                'excluded': {
                    'count': excluded_count,
                    'percentage': round(excluded_count / total_urls * 100, 1),
                    'types': excluded_types
                },
                'error': {
                    'count': error_count,
                    'percentage': round(error_count / total_urls * 100, 1),
                    'types': error_types
                },
                'warning': {
                    'count': warning_count,
                    'percentage': round(warning_count / total_urls * 100, 1),
                    'types': warning_types
                }
            }
            
            return result
        else:
            # 実際のAPIを使用してデータを取得（実装が必要）
            # ここでは例としてモックデータを返す
            logger.warning("Google Search Console APIが実装されていません。モックデータを返します。")
            return self.get_index_coverage()
    
    def get_mobile_usability(self):
        """
        モバイルユーザビリティデータを取得
        
        Returns:
            dict: モバイルユーザビリティデータ
        """
        if self.mock_mode:
            # モックデータを返す
            logger.info("モックモードでモバイルユーザビリティデータを生成します")
            
            # モバイルユーザビリティの問題のモックデータ
            total_pages = np.random.randint(50, 200)
            
            # 問題のある割合
            issue_ratio = np.random.uniform(0.05, 0.3)
            issue_count = int(total_pages * issue_ratio)
            valid_count = total_pages - issue_count
            
            # 問題の種類
            issue_types = [
                {'type': 'viewport_not_set', 'count': int(issue_count * 0.2)},
                {'type': 'content_wider_than_screen', 'count': int(issue_count * 0.3)},
                {'type': 'text_too_small', 'count': int(issue_count * 0.25)},
                {'type': 'clickable_elements_too_close', 'count': int(issue_count * 0.15)},
                {'type': 'other', 'count': issue_count - int(issue_count * 0.2) - int(issue_count * 0.3) - int(issue_count * 0.25) - int(issue_count * 0.15)}
            ]
            
            # 結果の作成
            result = {
                'total_pages': total_pages,
                'valid': {
                    'count': valid_count,
                    'percentage': round(valid_count / total_pages * 100, 1)
                },
                'issues': {
                    'count': issue_count,
                    'percentage': round(issue_count / total_pages * 100, 1),
                    'types': issue_types
                }
            }
            
            return result
        else:
            # 実際のAPIを使用してデータを取得（実装が必要）
            # ここでは例としてモックデータを返す
            logger.warning("Google Search Console APIが実装されていません。モックデータを返します。")
            return self.get_mobile_usability()
    
    def analyze(self):
        """
        Google Search Console分析を実行
        
        Returns:
            dict: Google Search Console分析結果
        """
        logger.info(f"Google Search Console分析を開始: {self.url}")
        
        # 分析開始時刻
        start_time = time.time()
        
        # 検索パフォーマンスデータの取得
        performance_data = self.get_search_performance(days=28, dimensions=['query', 'page', 'device', 'country'])
        
        # インデックスカバレッジデータの取得
        coverage_data = self.get_index_coverage()
        
        # モバイルユーザビリティデータの取得
        mobile_data = self.get_mobile_usability()
        
        # 上位キーワードの抽出
        top_queries = sorted(
            [item for item in performance_data['dimension_data'] if item['dimension_type'] == 'query'],
            key=lambda x: x['clicks'],
            reverse=True
        )[:10]
        
        # 上位ページの抽出
        top_pages = sorted(
            [item for item in performance_data['dimension_data'] if item['dimension_type'] == 'page'],
            key=lambda x: x['clicks'],
            reverse=True
        )[:10]
        
        # デバイス別データの抽出
        device_data = [item for item in performance_data['dimension_data'] if item['dimension_type'] == 'device']
        
        # 国別データの抽出
        country_data = [item for item in performance_data['dimension_data'] if item['dimension_type'] == 'country']
        
        # 検索パフォーマンスの評価
        if performance_data['totals']['clicks'] > 1000:
            performance_rating = '非常に良好'
        elif performance_data['totals']['clicks'] > 500:
            performance_rating = '良好'
        elif performance_data['totals']['clicks'] > 100:
            performance_rating = '普通'
        else:
            performance_rating = '改善の余地あり'
        
        # インデックスカバレッジの評価
        if coverage_data['valid']['percentage'] > 90:
            coverage_rating = '非常に良好'
        elif coverage_data['valid']['percentage'] > 80:
            coverage_rating = '良好'
        elif coverage_data['valid']['percentage'] > 70:
            coverage_rating = '普通'
        else:
            coverage_rating = '改善の余地あり'
        
        # モバイルユーザビリティの評価
        if mobile_data['valid']['percentage'] > 95:
            mobile_rating = '非常に良好'
        elif mobile_data['valid']['percentage'] > 90:
            mobile_rating = '良好'
        elif mobile_data['valid']['percentage'] > 80:
            mobile_rating = '普通'
        else:
            mobile_rating = '改善の余地あり'
        
        # 改善提案の作成
        recommendations = []
        
        # 検索パフォーマンスに基づく提案
        if performance_data['totals']['position'] > 10:
            recommendations.append('検索順位が低いため、コンテンツの質と関連性を向上させてください')
        if performance_data['totals']['ctr'] < 3:
            recommendations.append('クリック率が低いため、メタタイトルとメタディスクリプションを最適化してください')
        if performance_data['trends']['clicks'] < 0:
            recommendations.append('クリック数が減少傾向にあります。コンテンツの更新や新規コンテンツの追加を検討してください')
        
        # インデックスカバレッジに基づく提案
        if coverage_data['error']['count'] > 0:
            recommendations.append(f'インデックスエラーが{coverage_data["error"]["count"]}件あります。これらを修正してください')
        if coverage_data['warning']['count'] > 0:
            recommendations.append(f'インデックス警告が{coverage_data["warning"]["count"]}件あります。これらを確認してください')
        
        # モバイルユーザビリティに基づく提案
        if mobile_data['issues']['count'] > 0:
            recommendations.append(f'モバイルユーザビリティの問題が{mobile_data["issues"]["count"]}件あります。モバイル対応を改善してください')
        
        # 分析結果の作成
        result = {
            'url': self.url,
            'domain': self.domain,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'analysis_duration': round(time.time() - start_time, 2),
            'search_performance': {
                'summary': performance_data['totals'],
                'trends': performance_data['trends'],
                'rating': performance_rating,
                'top_queries': top_queries,
                'top_pages': top_pages,
                'device_data': device_data,
                'country_data': country_data,
                'date_data': performance_data['date_data']
            },
            'index_coverage': {
                'summary': {
                    'total_urls': coverage_data['total_urls'],
                    'valid': coverage_data['valid'],
                    'error': coverage_data['error'],
                    'excluded': coverage_data['excluded'],
                    'warning': coverage_data['warning']
                },
                'rating': coverage_rating
            },
            'mobile_usability': {
                'summary': {
                    'total_pages': mobile_data['total_pages'],
                    'valid': mobile_data['valid'],
                    'issues': mobile_data['issues']
                },
                'rating': mobile_rating
            },
            'recommendations': recommendations
        }
        
        logger.info(f"Google Search Console分析が完了しました: {self.url}")
        
        return result
