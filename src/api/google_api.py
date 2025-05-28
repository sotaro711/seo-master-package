"""
SEOマスターパッケージのGoogle API連携モジュール
"""
import os
import json
from datetime import datetime, timedelta
import requests
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleSearchConsoleAPI:
    """
    Google Search Console APIを利用してサイトの検索パフォーマンスデータを取得するクラス
    """
    
    def __init__(self, site_url):
        """
        Google Search Console APIクライアントを初期化します。
        
        Args:
            site_url (str): 分析対象のサイトURL
        """
        self.site_url = site_url
        self.service = None
        self.mock_mode = True
        
        # 認証情報の設定を試みる
        try:
            self._setup_service()
            self.mock_mode = False
        except Exception as e:
            print(f"Google Search Console API認証に失敗しました: {e}")
            print("モックモードで動作します。")
    
    def _setup_service(self):
        """
        Google Search Console APIサービスをセットアップします。
        
        Raises:
            FileNotFoundError: 認証ファイルが見つからない場合
            Exception: API接続に失敗した場合
        """
        # 認証ファイルのパスを設定
        credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        
        if not credentials_path or not os.path.exists(credentials_path):
            raise FileNotFoundError("Google API認証ファイルが見つかりません。")
        
        # 認証情報を読み込む
        credentials = Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/webmasters.readonly']
        )
        
        # APIサービスを構築
        self.service = build('searchconsole', 'v1', credentials=credentials)
    
    def get_search_analytics(self, days=30, dimensions=None):
        """
        Search Consoleから検索アナリティクスデータを取得します。
        
        Args:
            days (int): 取得する日数（デフォルト: 30日）
            dimensions (list): データのディメンション（デフォルト: ['query']）
            
        Returns:
            dict: 検索アナリティクスデータ
        """
        if dimensions is None:
            dimensions = ['query']
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        if self.mock_mode:
            return self._get_mock_search_analytics(dimensions)
        
        try:
            request = {
                'startDate': start_date.strftime('%Y-%m-%d'),
                'endDate': end_date.strftime('%Y-%m-%d'),
                'dimensions': dimensions,
                'rowLimit': 1000
            }
            
            response = self.service.searchanalytics().query(siteUrl=self.site_url, body=request).execute()
            return response
        except HttpError as e:
            print(f"Google Search Console APIリクエストエラー: {e}")
            return self._get_mock_search_analytics(dimensions)
    
    def _get_mock_search_analytics(self, dimensions):
        """
        モックの検索アナリティクスデータを生成します。
        
        Args:
            dimensions (list): データのディメンション
            
        Returns:
            dict: モックの検索アナリティクスデータ
        """
        mock_data = {
            'rows': []
        }
        
        # ディメンションに応じてモックデータを生成
        if 'query' in dimensions:
            mock_data['rows'] = [
                {'keys': ['seo分析'], 'clicks': 120, 'impressions': 1500, 'ctr': 0.08, 'position': 3.2},
                {'keys': ['seoツール'], 'clicks': 95, 'impressions': 1200, 'ctr': 0.079, 'position': 4.1},
                {'keys': ['無料seo診断'], 'clicks': 85, 'impressions': 950, 'ctr': 0.089, 'position': 2.8},
                {'keys': ['seo対策 方法'], 'clicks': 75, 'impressions': 850, 'ctr': 0.088, 'position': 5.3},
                {'keys': ['サイト分析 ツール'], 'clicks': 65, 'impressions': 750, 'ctr': 0.087, 'position': 6.2}
            ]
        elif 'page' in dimensions:
            mock_data['rows'] = [
                {'keys': ['/'], 'clicks': 250, 'impressions': 3000, 'ctr': 0.083, 'position': 2.5},
                {'keys': ['/services'], 'clicks': 180, 'impressions': 2200, 'ctr': 0.082, 'position': 3.1},
                {'keys': ['/blog/seo-tips'], 'clicks': 150, 'impressions': 1800, 'ctr': 0.083, 'position': 2.8},
                {'keys': ['/contact'], 'clicks': 120, 'impressions': 1500, 'ctr': 0.08, 'position': 3.5},
                {'keys': ['/about'], 'clicks': 100, 'impressions': 1200, 'ctr': 0.083, 'position': 4.2}
            ]
        
        return mock_data
    
    def analyze_search_performance(self, days=30):
        """
        検索パフォーマンスを分析します。
        
        Args:
            days (int): 分析する日数
            
        Returns:
            dict: 分析結果
        """
        # クエリデータを取得
        query_data = self.get_search_analytics(days, ['query'])
        
        # ページデータを取得
        page_data = self.get_search_analytics(days, ['page'])
        
        # 分析結果を生成
        results = {
            'period': f"過去{days}日間",
            'top_queries': [],
            'top_pages': [],
            'summary': {
                'total_clicks': 0,
                'total_impressions': 0,
                'average_ctr': 0,
                'average_position': 0
            }
        }
        
        # クエリデータを処理
        if 'rows' in query_data:
            total_clicks = sum(row.get('clicks', 0) for row in query_data['rows'])
            total_impressions = sum(row.get('impressions', 0) for row in query_data['rows'])
            
            # CTRと平均順位を計算
            if total_impressions > 0:
                average_ctr = total_clicks / total_impressions
            else:
                average_ctr = 0
                
            if query_data['rows']:
                average_position = sum(row.get('position', 0) for row in query_data['rows']) / len(query_data['rows'])
            else:
                average_position = 0
            
            # サマリーを更新
            results['summary'] = {
                'total_clicks': total_clicks,
                'total_impressions': total_impressions,
                'average_ctr': round(average_ctr * 100, 2),
                'average_position': round(average_position, 1)
            }
            
            # トップクエリを追加
            results['top_queries'] = [
                {
                    'query': row['keys'][0],
                    'clicks': row.get('clicks', 0),
                    'impressions': row.get('impressions', 0),
                    'ctr': round(row.get('ctr', 0) * 100, 2),
                    'position': round(row.get('position', 0), 1)
                }
                for row in query_data['rows'][:10]  # 上位10件を取得
            ]
        
        # ページデータを処理
        if 'rows' in page_data:
            # トップページを追加
            results['top_pages'] = [
                {
                    'page': row['keys'][0],
                    'clicks': row.get('clicks', 0),
                    'impressions': row.get('impressions', 0),
                    'ctr': round(row.get('ctr', 0) * 100, 2),
                    'position': round(row.get('position', 0), 1)
                }
                for row in page_data['rows'][:10]  # 上位10件を取得
            ]
        
        return results
    
    def generate_report(self, days=30, output_dir=None):
        """
        検索パフォーマンスレポートを生成します。
        
        Args:
            days (int): 分析する日数
            output_dir (str): 出力ディレクトリ
            
        Returns:
            str: レポートファイルのパス
        """
        # 分析を実行
        analysis_results = self.analyze_search_performance(days)
        
        # 出力ディレクトリの設定
        if output_dir is None:
            output_dir = os.path.join(os.getcwd(), 'data', 'reports')
        
        # ディレクトリが存在しない場合は作成
        os.makedirs(output_dir, exist_ok=True)
        
        # ファイル名を生成
        domain = self.site_url.replace('https://', '').replace('http://', '').replace('/', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"search_console_report_{domain}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        # レポートをJSONファイルとして保存
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=2)
        
        return filepath


class GoogleAnalyticsAPI:
    """
    Google Analytics Data APIを利用してサイトのアクセス解析データを取得するクラス
    """
    
    def __init__(self, property_id):
        """
        Google Analytics APIクライアントを初期化します。
        
        Args:
            property_id (str): Google Analyticsのプロパティ ID
        """
        self.property_id = property_id
        self.service = None
        self.mock_mode = True
        
        # 認証情報の設定を試みる
        try:
            self._setup_service()
            self.mock_mode = False
        except Exception as e:
            print(f"Google Analytics API認証に失敗しました: {e}")
            print("モックモードで動作します。")
    
    def _setup_service(self):
        """
        Google Analytics APIサービスをセットアップします。
        
        Raises:
            FileNotFoundError: 認証ファイルが見つからない場合
            Exception: API接続に失敗した場合
        """
        # 認証ファイルのパスを設定
        credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        
        if not credentials_path or not os.path.exists(credentials_path):
            raise FileNotFoundError("Google API認証ファイルが見つかりません。")
        
        # 認証情報を読み込む
        credentials = Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/analytics.readonly']
        )
        
        # APIサービスを構築
        self.service = build('analyticsdata', 'v1beta', credentials=credentials)
    
    def get_traffic_data(self, days=30):
        """
        Google Analyticsからトラフィックデータを取得します。
        
        Args:
            days (int): 取得する日数（デフォルト: 30日）
            
        Returns:
            dict: トラフィックデータ
        """
        if self.mock_mode:
            return self._get_mock_traffic_data(days)
        
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            request = {
                'property': f"properties/{self.property_id}",
                'dateRanges': [
                    {
                        'startDate': start_date.strftime('%Y-%m-%d'),
                        'endDate': end_date.strftime('%Y-%m-%d')
                    }
                ],
                'dimensions': [
                    {'name': 'date'}
                ],
                'metrics': [
                    {'name': 'sessions'},
                    {'name': 'activeUsers'},
                    {'name': 'newUsers'},
                    {'name': 'engagementRate'},
                    {'name': 'averageSessionDuration'}
                ]
            }
            
            response = self.service.properties().runReport(
                property=f"properties/{self.property_id}",
                body=request
            ).execute()
            
            return response
        except Exception as e:
            print(f"Google Analytics APIリクエストエラー: {e}")
            return self._get_mock_traffic_data(days)
    
    def _get_mock_traffic_data(self, days):
        """
        モックのトラフィックデータを生成します。
        
        Args:
            days (int): 日数
            
        Returns:
            dict: モックのトラフィックデータ
        """
        end_date = datetime.now().date()
        rows = []
        
        # 日付ごとのデータを生成
        for i in range(days):
            date = end_date - timedelta(days=i)
            date_str = date.strftime('%Y%m%d')
            
            # 基本値に若干のランダム性を持たせる
            import random
            base_sessions = 100 + (days - i) * 2  # 日付が近いほど多い傾向
            variation = random.uniform(0.8, 1.2)
            
            sessions = int(base_sessions * variation)
            active_users = int(sessions * 0.9)
            new_users = int(sessions * 0.3)
            engagement_rate = round(random.uniform(0.4, 0.7), 2)
            avg_session_duration = int(random.uniform(120, 300))
            
            rows.append({
                'dimensionValues': [{'value': date_str}],
                'metricValues': [
                    {'value': str(sessions)},
                    {'value': str(active_users)},
                    {'value': str(new_users)},
                    {'value': str(engagement_rate)},
                    {'value': str(avg_session_duration)}
                ]
            })
        
        # レスポンス形式に整形
        mock_data = {
            'dimensionHeaders': [{'name': 'date'}],
            'metricHeaders': [
                {'name': 'sessions', 'type': 'INTEGER'},
                {'name': 'activeUsers', 'type': 'INTEGER'},
                {'name': 'newUsers', 'type': 'INTEGER'},
                {'name': 'engagementRate', 'type': 'FLOAT'},
                {'name': 'averageSessionDuration', 'type': 'INTEGER'}
            ],
            'rows': rows
        }
        
        return mock_data
    
    def analyze_traffic(self, days=30):
        """
        トラフィックデータを分析します。
        
        Args:
            days (int): 分析する日数
            
        Returns:
            dict: 分析結果
        """
        # トラフィックデータを取得
        traffic_data = self.get_traffic_data(days)
        
        # 分析結果を生成
        results = {
            'period': f"過去{days}日間",
            'summary': {
                'total_sessions': 0,
                'total_users': 0,
                'new_users': 0,
                'average_engagement_rate': 0,
                'average_session_duration': 0
            },
            'daily_data': []
        }
        
        # データを処理
        if 'rows' in traffic_data:
            total_sessions = 0
            total_users = 0
            total_new_users = 0
            total_engagement_rate = 0
            total_session_duration = 0
            
            for row in traffic_data['rows']:
                date_value = row['dimensionValues'][0]['value']
                sessions = int(row['metricValues'][0]['value'])
                active_users = int(row['metricValues'][1]['value'])
                new_users = int(row['metricValues'][2]['value'])
                engagement_rate = float(row['metricValues'][3]['value'])
                session_duration = int(row['metricValues'][4]['value'])
                
                # 合計を計算
                total_sessions += sessions
                total_users += active_users
                total_new_users += new_users
                total_engagement_rate += engagement_rate
                total_session_duration += session_duration
                
                # 日付フォーマットを変換
                formatted_date = f"{date_value[:4]}-{date_value[4:6]}-{date_value[6:]}"
                
                # 日次データを追加
                results['daily_data'].append({
                    'date': formatted_date,
                    'sessions': sessions,
                    'active_users': active_users,
                    'new_users': new_users,
                    'engagement_rate': round(engagement_rate * 100, 1),
                    'avg_session_duration': session_duration
                })
            
            # 平均値を計算
            row_count = len(traffic_data['rows'])
            if row_count > 0:
                avg_engagement_rate = total_engagement_rate / row_count
                avg_session_duration = total_session_duration / row_count
            else:
                avg_engagement_rate = 0
                avg_session_duration = 0
            
            # サマリーを更新
            results['summary'] = {
                'total_sessions': total_sessions,
                'total_users': total_users,
                'new_users': total_new_users,
                'average_engagement_rate': round(avg_engagement_rate * 100, 1),
                'average_session_duration': int(avg_session_duration)
            }
        
        return results
    
    def generate_report(self, days=30, output_dir=None):
        """
        トラフィック分析レポートを生成します。
        
        Args:
            days (int): 分析する日数
            output_dir (str): 出力ディレクトリ
            
        Returns:
            str: レポートファイルのパス
        """
        # 分析を実行
        analysis_results = self.analyze_traffic(days)
        
        # 出力ディレクトリの設定
        if output_dir is None:
            output_dir = os.path.join(os.getcwd(), 'data', 'reports')
        
        # ディレクトリが存在しない場合は作成
        os.makedirs(output_dir, exist_ok=True)
        
        # ファイル名を生成
        property_id = self.property_id.replace('/', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"analytics_report_{property_id}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        # レポートをJSONファイルとして保存
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=2)
        
        return filepath
