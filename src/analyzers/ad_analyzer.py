"""
SEOマスターパッケージ - 広告アナライザーモジュール

このモジュールは、Webサイトの広告出稿分析機能を提供します。
Google広告、ソーシャルメディア広告の収集と分析、広告テキスト・キーワード・ランディングページURLの抽出などの機能を実装しています。
"""

import logging
import json
import os
import re
import time
from datetime import datetime
import random
import numpy as np
import pandas as pd
from urllib.parse import urlparse
import tldextract
import requests
from bs4 import BeautifulSoup

from src.core.analyzer import SEOAnalyzer

# ロギングの設定
logger = logging.getLogger(__name__)

class AdAnalyzer:
    """Webサイトの広告出稿を分析するクラス"""
    
    def __init__(self, url, mock_mode=True):
        """
        AdAnalyzerクラスの初期化
        
        Args:
            url (str): 分析対象のURL
            mock_mode (bool, optional): モックモードを使用するかどうか（APIキーがない場合など）
        """
        self.url = url
        self.mock_mode = mock_mode
        self.seo_analyzer = SEOAnalyzer(url)
        self.domain = self.seo_analyzer.domain
        
        # データディレクトリの確認
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def get_google_ads(self, keywords=None, limit=50):
        """
        Google広告を取得
        
        Args:
            keywords (list, optional): 検索するキーワードのリスト（指定がない場合は自動生成）
            limit (int, optional): 取得する広告の最大数
            
        Returns:
            list: Google広告のリスト
        """
        if self.mock_mode:
            # モックデータを返す
            logger.info("モックモードでGoogle広告データを生成します")
            
            # キーワードが指定されていない場合は自動生成
            if not keywords:
                # ドメインに基づいてキーワードを生成（モック）
                industry_keywords = {
                    'shop': ['オンラインショップ', 'ネット通販', 'オンラインストア', 'ECサイト', '送料無料'],
                    'blog': ['ブログ', 'コンテンツ', '記事', '情報', 'ニュース'],
                    'tech': ['テクノロジー', 'IT', 'ソフトウェア', 'アプリ', 'デジタル'],
                    'finance': ['金融', '投資', '保険', '資産運用', '株式'],
                    'travel': ['旅行', 'ツアー', 'ホテル', '観光', '予約'],
                    'health': ['健康', '医療', 'フィットネス', 'ダイエット', '美容'],
                    'education': ['教育', '学習', 'オンライン講座', 'スクール', '資格']
                }
                
                # ドメインからカテゴリを推測（モック）
                domain_keywords = []
                for category, kw_list in industry_keywords.items():
                    if category in self.domain.lower():
                        domain_keywords.extend(kw_list)
                
                # デフォルトのキーワード
                if not domain_keywords:
                    domain_keywords = ['サービス', '製品', '会社', 'ビジネス', '公式']
                
                # ドメイン名を含むキーワード
                domain_name = self.domain.split('.')[0]
                domain_keywords.extend([
                    domain_name,
                    f'{domain_name} 公式',
                    f'{domain_name} サービス',
                    f'{domain_name} 評判',
                    f'{domain_name} 料金'
                ])
                
                keywords = domain_keywords
            
            # 広告のサンプル（モック）
            sample_headlines = [
                '【公式】{domain} - 高品質なサービスを提供',
                '最新の{keyword}情報 - {domain}',
                '{keyword}のエキスパート | {domain}',
                '{domain}で{keyword}を今すぐチェック',
                '【期間限定】{keyword}が今だけお得 - {domain}',
                '{keyword}ならNo.1の{domain}',
                '信頼と実績の{domain} - {keyword}のプロフェッショナル',
                '{keyword}の悩みを解決 - {domain}',
                '【初回限定】{keyword}サービスを無料体験 - {domain}',
                '24時間対応の{keyword}サポート - {domain}'
            ]
            
            sample_descriptions = [
                '業界トップクラスの{keyword}サービスを提供しています。今すぐお問い合わせください。',
                '{keyword}に関する豊富な実績と経験。お客様満足度98%の{domain}にお任せください。',
                '初めての方も安心。{keyword}のプロが丁寧にサポートします。無料相談実施中。',
                '最新の{keyword}情報を毎日更新。業界の最新トレンドを{domain}でチェック。',
                '{keyword}に関するあらゆるニーズにお応えします。24時間365日対応可能。',
                '【公式】{domain} - {keyword}のリーディングカンパニー。今なら特別キャンペーン実施中。',
                '{keyword}の悩みを解決するための専門サービス。満足度保証付き。',
                '他社と比べて{keyword}の品質が違います。無料見積もり実施中。',
                '{keyword}に関する無料相談受付中。専門スタッフが丁寧に対応します。',
                '【期間限定】{keyword}サービスが今だけ30%OFF。この機会をお見逃しなく。'
            ]
            
            # 広告の生成（モック）
            ads = []
            for i in range(min(limit, len(keywords) * 5)):
                keyword = keywords[i % len(keywords)]
                
                # ヘッドラインの生成
                headline = random.choice(sample_headlines).format(
                    domain=self.domain,
                    keyword=keyword
                )
                
                # ディスクリプションの生成
                description = random.choice(sample_descriptions).format(
                    domain=self.domain,
                    keyword=keyword
                )
                
                # 表示URLの生成
                display_url = f'https://{self.domain}/{keyword.replace(" ", "-").lower()}'
                
                # 最終URLの生成
                final_url = f'{display_url}?utm_source=google&utm_medium=cpc&utm_campaign={keyword.replace(" ", "_").lower()}'
                
                # 広告の種類（検索広告/ディスプレイ広告）の決定（モック）
                ad_type = random.choice(['search', 'display'])
                
                # 広告の表示位置の決定（モック）
                position = random.choice(['top', 'bottom', 'side']) if ad_type == 'search' else 'content'
                
                # 広告の入札キーワードの生成（モック）
                bid_keywords = [
                    keyword,
                    f'{keyword} {random.choice(["サービス", "会社", "比較", "おすすめ", "ランキング"])}',
                    f'最新 {keyword}',
                    f'{keyword} {random.choice(["料金", "価格", "費用", "相場"])}',
                    f'{self.domain} {keyword}'
                ]
                
                # 広告の推定費用の生成（モック）
                estimated_cost = {
                    'cpc': round(random.uniform(50, 500), 2),  # クリック単価
                    'daily_budget': round(random.uniform(1000, 10000), 2),  # 日予算
                    'monthly_spend': round(random.uniform(30000, 300000), 2)  # 月間支出
                }
                
                # 広告の競合性の生成（モック）
                competition = random.choice(['低', '中', '高'])
                
                # 広告情報の追加
                ads.append({
                    'keyword': keyword,
                    'headline': headline,
                    'description': description,
                    'display_url': display_url,
                    'final_url': final_url,
                    'ad_type': ad_type,
                    'position': position,
                    'bid_keywords': bid_keywords,
                    'estimated_cost': estimated_cost,
                    'competition': competition,
                    'first_seen': (datetime.now() - pd.Timedelta(days=random.randint(1, 90))).strftime('%Y-%m-%d'),
                    'last_seen': datetime.now().strftime('%Y-%m-%d')
                })
            
            return ads
        else:
            # 実際のAPIを使用してGoogle広告を取得（実装が必要）
            # ここでは例としてモックデータを返す
            logger.warning("Google広告取得APIが実装されていません。モックデータを返します。")
            return self.get_google_ads(keywords, limit)
    
    def get_social_ads(self, platforms=None, limit=50):
        """
        ソーシャルメディア広告を取得
        
        Args:
            platforms (list, optional): 取得するプラットフォームのリスト（指定がない場合は全プラットフォーム）
            limit (int, optional): 取得する広告の最大数
            
        Returns:
            dict: プラットフォームごとのソーシャルメディア広告
        """
        if not platforms:
            platforms = ['facebook', 'instagram', 'twitter', 'linkedin']
        
        if self.mock_mode:
            # モックデータを返す
            logger.info("モックモードでソーシャルメディア広告データを生成します")
            
            # プラットフォームごとの広告サンプル（モック）
            platform_samples = {
                'facebook': {
                    'headlines': [
                        '{domain}の新サービスを今すぐチェック',
                        '【公式】{domain} - 高品質なサービスを提供',
                        '{domain}で理想の{product}を見つけよう',
                        '【期間限定】{domain}の特別キャンペーン実施中',
                        '{domain}が選ばれる理由とは？'
                    ],
                    'descriptions': [
                        '業界トップクラスのサービスを提供しています。今すぐお問い合わせください。',
                        '豊富な実績と経験。お客様満足度98%の{domain}にお任せください。',
                        '初めての方も安心。プロが丁寧にサポートします。無料相談実施中。',
                        '最新情報を毎日更新。業界の最新トレンドを{domain}でチェック。',
                        'あらゆるニーズにお応えします。24時間365日対応可能。'
                    ],
                    'formats': ['single_image', 'carousel', 'video', 'slideshow', 'collection'],
                    'objectives': ['brand_awareness', 'reach', 'traffic', 'engagement', 'app_installs', 'video_views', 'lead_generation', 'conversions', 'catalog_sales', 'store_traffic']
                },
                'instagram': {
                    'headlines': [
                        '{domain}の新商品をチェック',
                        '【公式】{domain} - スタイリッシュな{product}',
                        '{domain}で{product}の魅力を発見',
                        '【限定】{domain}の特別コレクション',
                        '{domain}のこだわりとは？'
                    ],
                    'descriptions': [
                        'トレンドの最先端。{domain}の新コレクションをチェック。',
                        'プロが選ぶ{product}。{domain}の公式アカウントをフォロー。',
                        '毎日をスタイリッシュに。{domain}の{product}で差をつける。',
                        '限定デザインを公開中。{domain}でしか手に入らない{product}。',
                        'こだわり抜いた{product}。{domain}の世界観をお楽しみください。'
                    ],
                    'formats': ['single_image', 'carousel', 'video', 'reels', 'stories'],
                    'objectives': ['brand_awareness', 'reach', 'traffic', 'engagement', 'app_installs', 'video_views', 'lead_generation', 'conversions']
                },
                'twitter': {
                    'headlines': [
                        '{domain}の最新情報をチェック',
                        '【公式】{domain} - 今すぐフォロー',
                        '{domain}で最新の{product}情報をゲット',
                        '【速報】{domain}の新サービス登場',
                        '{domain}からのお知らせ'
                    ],
                    'descriptions': [
                        '最新情報をいち早くお届け。{domain}の公式アカウントをフォロー。',
                        '業界の最新トレンドを発信中。{domain}で最新情報をチェック。',
                        'フォロワー限定キャンペーン実施中。今すぐ{domain}をフォロー。',
                        '{product}に関する情報満載。{domain}の公式アカウントで確認を。',
                        '24時間以内に返信。{domain}にDMでお問い合わせください。'
                    ],
                    'formats': ['single_image', 'carousel', 'video', 'text'],
                    'objectives': ['awareness', 'consideration', 'conversion']
                },
                'linkedin': {
                    'headlines': [
                        '{domain}のビジネスソリューション',
                        '【公式】{domain} - プロフェッショナルの選択',
                        '{domain}で{product}のエキスパートに',
                        '【採用情報】{domain}でキャリアアップ',
                        '{domain}のビジネス戦略とは'
                    ],
                    'descriptions': [
                        'ビジネスの成長をサポート。{domain}の法人向けサービスをご紹介。',
                        'プロフェッショナルが選ぶ{product}。{domain}の実績をご覧ください。',
                        'スキルアップを目指すなら{domain}。業界トップクラスの研修制度。',
                        '優秀な人材を求めています。{domain}で一緒に働きませんか？',
                        'ビジネスの課題を解決。{domain}の{product}で業務効率化を実現。'
                    ],
                    'formats': ['single_image', 'carousel', 'video', 'text', 'document'],
                    'objectives': ['brand_awareness', 'website_visits', 'engagement', 'video_views', 'lead_generation', 'website_conversions', 'job_applicants']
                }
            }
            
            # 製品/サービスのサンプル（モック）
            sample_products = [
                'サービス', '製品', 'ソリューション', 'アプリ', 'プラン',
                'コンサルティング', 'サポート', 'ツール', 'システム', 'プログラム'
            ]
            
            # ソーシャルメディア広告の生成（モック）
            social_ads = {}
            
            for platform in platforms:
                if platform not in platform_samples:
                    continue
                
                platform_data = platform_samples[platform]
                ads = []
                
                for i in range(min(limit, 20)):  # 最大20件のモックデータ
                    product = random.choice(sample_products)
                    
                    # ヘッドラインの生成
                    headline = random.choice(platform_data['headlines']).format(
                        domain=self.domain,
                        product=product
                    )
                    
                    # ディスクリプションの生成
                    description = random.choice(platform_data['descriptions']).format(
                        domain=self.domain,
                        product=product
                    )
                    
                    # 広告フォーマットの選択
                    ad_format = random.choice(platform_data['formats'])
                    
                    # 広告目的の選択
                    objective = random.choice(platform_data['objectives'])
                    
                    # ターゲティングの生成（モック）
                    targeting = {
                        'age': random.choice(['18-24', '25-34', '35-44', '45-54', '55-64', '65+']),
                        'gender': random.choice(['all', 'male', 'female']),
                        'locations': random.sample(['東京', '大阪', '名古屋', '福岡', '札幌', '仙台', '広島', '全国'], k=random.randint(1, 3)),
                        'interests': random.sample(['ビジネス', 'テクノロジー', '教育', '金融', '旅行', '健康', 'ライフスタイル', 'スポーツ', 'エンターテイメント'], k=random.randint(1, 4))
                    }
                    
                    # クリエイティブの生成（モック）
                    creative = {
                        'type': ad_format,
                        'headline': headline,
                        'description': description,
                        'call_to_action': random.choice(['詳細を見る', '今すぐ申し込む', '無料体験', 'お問い合わせ', '購入する', 'ダウンロード', '登録する']),
                        'image_url': f'https://example.com/images/{platform}/{ad_format}_{i}.jpg'
                    }
                    
                    # ランディングページURLの生成
                    landing_page = f'https://{self.domain}/{product.replace(" ", "-").lower()}?utm_source={platform}&utm_medium=social&utm_campaign={objective}'
                    
                    # 広告の推定費用の生成（モック）
                    estimated_cost = {
                        'cpm': round(random.uniform(300, 1500), 2),  # 1000インプレッション単価
                        'daily_budget': round(random.uniform(1000, 10000), 2),  # 日予算
                        'monthly_spend': round(random.uniform(30000, 300000), 2)  # 月間支出
                    }
                    
                    # 広告情報の追加
                    ads.append({
                        'platform': platform,
                        'headline': headline,
                        'description': description,
                        'format': ad_format,
                        'objective': objective,
                        'targeting': targeting,
                        'creative': creative,
                        'landing_page': landing_page,
                        'estimated_cost': estimated_cost,
                        'first_seen': (datetime.now() - pd.Timedelta(days=random.randint(1, 90))).strftime('%Y-%m-%d'),
                        'last_seen': datetime.now().strftime('%Y-%m-%d')
                    })
                
                social_ads[platform] = ads
            
            return social_ads
        else:
            # 実際のAPIを使用してソーシャルメディア広告を取得（実装が必要）
            # ここでは例としてモックデータを返す
            logger.warning("ソーシャルメディア広告取得APIが実装されていません。モックデータを返します。")
            return self.get_social_ads(platforms, limit)
    
    def analyze_google_ads(self, ads=None):
        """
        Google広告を分析
        
        Args:
            ads (list, optional): 分析する広告のリスト（指定がない場合は取得）
            
        Returns:
            dict: Google広告分析結果
        """
        if ads is None:
            ads = self.get_google_ads()
        
        if not ads:
            return {}
        
        # 広告の総数
        total_ads = len(ads)
        
        # 広告の種類別の数
        ad_types = {}
        for ad in ads:
            ad_type = ad['ad_type']
            ad_types[ad_type] = ad_types.get(ad_type, 0) + 1
        
        # 広告の表示位置別の数
        positions = {}
        for ad in ads:
            position = ad['position']
            positions[position] = positions.get(position, 0) + 1
        
        # キーワード分析
        keywords = {}
        for ad in ads:
            keyword = ad['keyword']
            keywords[keyword] = keywords.get(keyword, 0) + 1
        
        # 上位のキーワード
        top_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # 入札キーワード分析
        bid_keywords = {}
        for ad in ads:
            for keyword in ad['bid_keywords']:
                bid_keywords[keyword] = bid_keywords.get(keyword, 0) + 1
        
        # 上位の入札キーワード
        top_bid_keywords = sorted(bid_keywords.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # 広告テキスト分析
        headline_words = {}
        description_words = {}
        
        for ad in ads:
            # ヘッドラインの単語分析
            for word in re.findall(r'\w+', ad['headline'].lower()):
                if len(word) > 2:  # 短い単語を除外
                    headline_words[word] = headline_words.get(word, 0) + 1
            
            # ディスクリプションの単語分析
            for word in re.findall(r'\w+', ad['description'].lower()):
                if len(word) > 2:  # 短い単語を除外
                    description_words[word] = description_words.get(word, 0) + 1
        
        # 上位のヘッドライン単語
        top_headline_words = sorted(headline_words.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # 上位のディスクリプション単語
        top_description_words = sorted(description_words.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # ランディングページ分析
        landing_pages = {}
        for ad in ads:
            landing_page = ad['final_url']
            landing_pages[landing_page] = landing_pages.get(landing_page, 0) + 1
        
        # 上位のランディングページ
        top_landing_pages = sorted(landing_pages.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # 推定費用の分析
        cpc_values = [ad['estimated_cost']['cpc'] for ad in ads]
        daily_budget_values = [ad['estimated_cost']['daily_budget'] for ad in ads]
        monthly_spend_values = [ad['estimated_cost']['monthly_spend'] for ad in ads]
        
        estimated_cost_analysis = {
            'cpc': {
                'min': min(cpc_values),
                'max': max(cpc_values),
                'avg': sum(cpc_values) / len(cpc_values)
            },
            'daily_budget': {
                'min': min(daily_budget_values),
                'max': max(daily_budget_values),
                'avg': sum(daily_budget_values) / len(daily_budget_values)
            },
            'monthly_spend': {
                'min': min(monthly_spend_values),
                'max': max(monthly_spend_values),
                'avg': sum(monthly_spend_values) / len(monthly_spend_values),
                'total': sum(monthly_spend_values)
            }
        }
        
        # 競合性の分析
        competition = {}
        for ad in ads:
            comp = ad['competition']
            competition[comp] = competition.get(comp, 0) + 1
        
        # 分析結果の統合
        analysis_results = {
            'total_ads': total_ads,
            'ad_types': ad_types,
            'positions': positions,
            'top_keywords': [{'keyword': keyword, 'count': count} for keyword, count in top_keywords],
            'top_bid_keywords': [{'keyword': keyword, 'count': count} for keyword, count in top_bid_keywords],
            'top_headline_words': [{'word': word, 'count': count} for word, count in top_headline_words],
            'top_description_words': [{'word': word, 'count': count} for word, count in top_description_words],
            'top_landing_pages': [{'url': url, 'count': count} for url, count in top_landing_pages],
            'estimated_cost': estimated_cost_analysis,
            'competition': competition
        }
        
        logger.info(f"Google広告分析完了: {self.url}")
        return analysis_results
    
    def analyze_social_ads(self, social_ads=None):
        """
        ソーシャルメディア広告を分析
        
        Args:
            social_ads (dict, optional): 分析する広告のディクショナリ（指定がない場合は取得）
            
        Returns:
            dict: ソーシャルメディア広告分析結果
        """
        if social_ads is None:
            social_ads = self.get_social_ads()
        
        if not social_ads:
            return {}
        
        # プラットフォーム別の広告数
        platform_counts = {platform: len(ads) for platform, ads in social_ads.items()}
        total_ads = sum(platform_counts.values())
        
        # プラットフォーム別の分析結果
        platform_analysis = {}
        
        for platform, ads in social_ads.items():
            if not ads:
                continue
            
            # 広告フォーマット別の数
            formats = {}
            for ad in ads:
                ad_format = ad['format']
                formats[ad_format] = formats.get(ad_format, 0) + 1
            
            # 広告目的別の数
            objectives = {}
            for ad in ads:
                objective = ad['objective']
                objectives[objective] = objectives.get(objective, 0) + 1
            
            # ターゲティング分析
            age_targeting = {}
            gender_targeting = {}
            location_targeting = {}
            interest_targeting = {}
            
            for ad in ads:
                targeting = ad['targeting']
                
                # 年齢ターゲティング
                age = targeting['age']
                age_targeting[age] = age_targeting.get(age, 0) + 1
                
                # 性別ターゲティング
                gender = targeting['gender']
                gender_targeting[gender] = gender_targeting.get(gender, 0) + 1
                
                # 地域ターゲティング
                for location in targeting['locations']:
                    location_targeting[location] = location_targeting.get(location, 0) + 1
                
                # 興味関心ターゲティング
                for interest in targeting['interests']:
                    interest_targeting[interest] = interest_targeting.get(interest, 0) + 1
            
            # クリエイティブ分析
            call_to_actions = {}
            for ad in ads:
                cta = ad['creative']['call_to_action']
                call_to_actions[cta] = call_to_actions.get(cta, 0) + 1
            
            # ランディングページ分析
            landing_pages = {}
            for ad in ads:
                landing_page = ad['landing_page']
                landing_pages[landing_page] = landing_pages.get(landing_page, 0) + 1
            
            # 推定費用の分析
            cpm_values = [ad['estimated_cost']['cpm'] for ad in ads]
            daily_budget_values = [ad['estimated_cost']['daily_budget'] for ad in ads]
            monthly_spend_values = [ad['estimated_cost']['monthly_spend'] for ad in ads]
            
            estimated_cost_analysis = {
                'cpm': {
                    'min': min(cpm_values),
                    'max': max(cpm_values),
                    'avg': sum(cpm_values) / len(cpm_values)
                },
                'daily_budget': {
                    'min': min(daily_budget_values),
                    'max': max(daily_budget_values),
                    'avg': sum(daily_budget_values) / len(daily_budget_values)
                },
                'monthly_spend': {
                    'min': min(monthly_spend_values),
                    'max': max(monthly_spend_values),
                    'avg': sum(monthly_spend_values) / len(monthly_spend_values),
                    'total': sum(monthly_spend_values)
                }
            }
            
            # プラットフォーム別の分析結果を統合
            platform_analysis[platform] = {
                'total_ads': len(ads),
                'formats': formats,
                'objectives': objectives,
                'targeting': {
                    'age': age_targeting,
                    'gender': gender_targeting,
                    'location': location_targeting,
                    'interest': interest_targeting
                },
                'call_to_actions': call_to_actions,
                'top_landing_pages': [{'url': url, 'count': count} for url, count in sorted(landing_pages.items(), key=lambda x: x[1], reverse=True)[:5]],
                'estimated_cost': estimated_cost_analysis
            }
        
        # 全プラットフォームの推定総費用
        total_monthly_spend = sum(
            platform_data['estimated_cost']['monthly_spend']['total']
            for platform_data in platform_analysis.values()
        )
        
        # 分析結果の統合
        analysis_results = {
            'total_ads': total_ads,
            'platform_counts': platform_counts,
            'platform_analysis': platform_analysis,
            'total_monthly_spend': total_monthly_spend
        }
        
        logger.info(f"ソーシャルメディア広告分析完了: {self.url}")
        return analysis_results
    
    def analyze(self):
        """
        広告出稿分析を実行
        
        Returns:
            dict: 広告出稿分析結果
        """
        # 基本情報
        basic_info = {
            'url': self.url,
            'domain': self.domain
        }
        
        # Google広告の取得と分析
        google_ads = self.get_google_ads()
        google_ads_analysis = self.analyze_google_ads(google_ads)
        
        # ソーシャルメディア広告の取得と分析
        social_ads = self.get_social_ads()
        social_ads_analysis = self.analyze_social_ads(social_ads)
        
        # 総合分析
        total_monthly_spend = 0
        if google_ads_analysis and 'estimated_cost' in google_ads_analysis:
            total_monthly_spend += google_ads_analysis['estimated_cost']['monthly_spend']['total']
        
        if social_ads_analysis and 'total_monthly_spend' in social_ads_analysis:
            total_monthly_spend += social_ads_analysis['total_monthly_spend']
        
        # 分析結果の統合
        analysis_results = {
            'basic_info': basic_info,
            'google_ads': {
                'ads': google_ads,
                'analysis': google_ads_analysis
            },
            'social_ads': {
                'ads': social_ads,
                'analysis': social_ads_analysis
            },
            'total_monthly_spend': total_monthly_spend
        }
        
        logger.info(f"広告出稿分析完了: {self.url}")
        return analysis_results
    
    def save_analysis_results(self, results, filename=None):
        """
        分析結果をJSONファイルに保存
        
        Args:
            results (dict): 保存する分析結果
            filename (str, optional): 保存するファイル名
            
        Returns:
            str: 保存したファイルのパス
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ad_analysis_{timestamp}.json"
        
        file_path = os.path.join(self.data_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"分析結果を保存しました: {file_path}")
        return file_path
