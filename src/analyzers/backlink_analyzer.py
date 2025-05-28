"""
SEOマスターパッケージ - バックリンクアナライザーモジュール

このモジュールは、Webサイトのバックリンク（被リンク）分析機能を提供します。
外部サイトからの被リンク分析、Link Intersect分析、悪質な被リンクの検出などの機能を実装しています。
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

from src.core.analyzer import SEOAnalyzer

# ロギングの設定
logger = logging.getLogger(__name__)

class BacklinkAnalyzer:
    """Webサイトのバックリンク（被リンク）を分析するクラス"""
    
    def __init__(self, url, mock_mode=True):
        """
        BacklinkAnalyzerクラスの初期化
        
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
    
    def get_backlinks(self, limit=100):
        """
        バックリンク（被リンク）を取得
        
        Args:
            limit (int, optional): 取得するバックリンクの最大数
            
        Returns:
            list: バックリンクのリスト
        """
        if self.mock_mode:
            # モックデータを返す
            logger.info("モックモードでバックリンクデータを生成します")
            
            # ドメインのサンプル（モック）
            sample_domains = [
                'example.com', 'blog.example.net', 'news.example.org', 'tech.example.io',
                'review.example.co.jp', 'forum.example.com', 'community.example.net',
                'support.example.org', 'docs.example.io', 'help.example.co.jp'
            ]
            
            # パスのサンプル（モック）
            sample_paths = [
                '/blog/post-1', '/news/article-2', '/review/product-3', '/forum/thread-4',
                '/community/topic-5', '/support/ticket-6', '/docs/guide-7', '/help/faq-8',
                '/about', '/contact', '/products', '/services', '/team', '/partners'
            ]
            
            # アンカーテキストのサンプル（モック）
            sample_anchor_texts = [
                'ウェブサイト', '詳細はこちら', '公式サイト', '参考リンク', 'クリックして詳細を見る',
                self.domain, f'{self.domain}の公式サイト', f'{self.domain}について',
                'SEO対策', 'マーケティング戦略', 'コンテンツ最適化', 'ウェブ分析',
                'デジタルマーケティング', 'オンラインビジネス', 'ウェブ開発'
            ]
            
            # バックリンクの生成（モック）
            backlinks = []
            for i in range(min(limit, 500)):  # 最大500件のモックデータ
                domain = random.choice(sample_domains)
                path = random.choice(sample_paths)
                source_url = f'https://{domain}{path}'
                
                # ドメイン権威スコア（DA）の生成（モック）
                domain_authority = random.randint(1, 100)
                
                # ページ権威スコア（PA）の生成（モック）
                page_authority = random.randint(1, 100)
                
                # リンクの種類（dofollow/nofollow）の決定（モック）
                is_dofollow = random.random() > 0.2  # 80%の確率でdofollow
                
                # アンカーテキストの選択（モック）
                anchor_text = random.choice(sample_anchor_texts)
                
                # 最初の発見日の生成（モック）
                days_ago = random.randint(1, 365)
                first_seen = (datetime.now() - pd.Timedelta(days=days_ago)).strftime('%Y-%m-%d')
                
                # 最終確認日の生成（モック）
                days_ago_last = random.randint(0, min(days_ago, 30))
                last_seen = (datetime.now() - pd.Timedelta(days=days_ago_last)).strftime('%Y-%m-%d')
                
                # リンク先URLの生成（モック）
                target_path = random.choice([
                    '/', '/about', '/products', '/services', '/blog', '/contact',
                    '/blog/post-1', '/products/item-2', '/services/service-3'
                ])
                target_url = f'https://{self.domain}{target_path}'
                
                # バックリンク情報の追加
                backlinks.append({
                    'source_url': source_url,
                    'source_domain': domain,
                    'target_url': target_url,
                    'anchor_text': anchor_text,
                    'domain_authority': domain_authority,
                    'page_authority': page_authority,
                    'is_dofollow': is_dofollow,
                    'first_seen': first_seen,
                    'last_seen': last_seen
                })
            
            return backlinks
        else:
            # 実際のAPIを使用してバックリンクを取得（実装が必要）
            # ここでは例としてモックデータを返す
            logger.warning("バックリンク取得APIが実装されていません。モックデータを返します。")
            return self.get_backlinks(limit)
    
    def analyze_backlinks(self, backlinks=None):
        """
        バックリンクを分析
        
        Args:
            backlinks (list, optional): 分析するバックリンクのリスト（指定がない場合は取得）
            
        Returns:
            dict: バックリンク分析結果
        """
        if backlinks is None:
            backlinks = self.get_backlinks()
        
        if not backlinks:
            return {}
        
        # バックリンクの総数
        total_backlinks = len(backlinks)
        
        # リンク元ドメインの数
        referring_domains = set(backlink['source_domain'] for backlink in backlinks)
        total_referring_domains = len(referring_domains)
        
        # dofollowリンクの数
        dofollow_links = sum(1 for backlink in backlinks if backlink['is_dofollow'])
        
        # nofollowリンクの数
        nofollow_links = total_backlinks - dofollow_links
        
        # ドメイン権威スコア（DA）の分布
        da_values = [backlink['domain_authority'] for backlink in backlinks]
        da_distribution = {
            'min': min(da_values),
            'max': max(da_values),
            'avg': sum(da_values) / len(da_values),
            'median': sorted(da_values)[len(da_values) // 2]
        }
        
        # ページ権威スコア（PA）の分布
        pa_values = [backlink['page_authority'] for backlink in backlinks]
        pa_distribution = {
            'min': min(pa_values),
            'max': max(pa_values),
            'avg': sum(pa_values) / len(pa_values),
            'median': sorted(pa_values)[len(pa_values) // 2]
        }
        
        # アンカーテキストの分析
        anchor_texts = [backlink['anchor_text'] for backlink in backlinks]
        anchor_text_counts = {}
        for anchor in anchor_texts:
            anchor_text_counts[anchor] = anchor_text_counts.get(anchor, 0) + 1
        
        # 上位のアンカーテキスト
        top_anchor_texts = sorted(anchor_text_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # リンク先URLの分析
        target_urls = [backlink['target_url'] for backlink in backlinks]
        target_url_counts = {}
        for url in target_urls:
            target_url_counts[url] = target_url_counts.get(url, 0) + 1
        
        # 上位のリンク先URL
        top_target_urls = sorted(target_url_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # 分析結果の統合
        analysis_results = {
            'total_backlinks': total_backlinks,
            'total_referring_domains': total_referring_domains,
            'dofollow_links': dofollow_links,
            'nofollow_links': nofollow_links,
            'domain_authority_distribution': da_distribution,
            'page_authority_distribution': pa_distribution,
            'top_anchor_texts': [{'text': text, 'count': count} for text, count in top_anchor_texts],
            'top_target_urls': [{'url': url, 'count': count} for url, count in top_target_urls]
        }
        
        logger.info(f"バックリンク分析完了: {self.url}")
        return analysis_results
    
    def analyze_link_intersect(self, competitor_urls, limit=100):
        """
        Link Intersect分析を実行（競合が獲得しているが自社が獲得できていないリンクを特定）
        
        Args:
            competitor_urls (list): 競合サイトのURLリスト
            limit (int, optional): 取得するバックリンクの最大数
            
        Returns:
            dict: Link Intersect分析結果
        """
        if not competitor_urls:
            return {}
        
        # 自社のバックリンクを取得
        own_backlinks = self.get_backlinks(limit)
        own_backlink_domains = set(backlink['source_domain'] for backlink in own_backlinks)
        
        # 競合のバックリンクを取得
        competitor_backlinks = {}
        for competitor_url in competitor_urls:
            # 競合ドメインの抽出
            competitor_domain = tldextract.extract(competitor_url).registered_domain
            
            if self.mock_mode:
                # モックデータを生成
                logger.info(f"モックモードで競合バックリンクデータを生成します: {competitor_url}")
                
                # 競合のバックリンクを生成（モック）
                comp_backlinks = self.get_backlinks(limit)
                
                # 一部のバックリンクを自社と重複させる（モック）
                overlap_ratio = random.uniform(0.1, 0.4)  # 10%〜40%の重複
                overlap_count = int(len(comp_backlinks) * overlap_ratio)
                
                for i in range(overlap_count):
                    if i < len(comp_backlinks):
                        comp_backlinks[i]['source_domain'] = random.choice(list(own_backlink_domains))
                
                competitor_backlinks[competitor_domain] = comp_backlinks
            else:
                # 実際のAPIを使用して競合のバックリンクを取得（実装が必要）
                # ここでは例としてモックデータを返す
                logger.warning(f"競合バックリンク取得APIが実装されていません。モックデータを返します: {competitor_url}")
                competitor_backlinks[competitor_domain] = self.get_backlinks(limit)
        
        # Link Intersect分析
        link_opportunities = {}
        
        for competitor_domain, comp_backlinks in competitor_backlinks.items():
            # 競合のバックリンクドメイン
            comp_backlink_domains = set(backlink['source_domain'] for backlink in comp_backlinks)
            
            # 競合が獲得しているが自社が獲得できていないリンク元ドメイン
            unique_domains = comp_backlink_domains - own_backlink_domains
            
            # 各ドメインからの最も価値の高いバックリンク
            valuable_backlinks = []
            
            for domain in unique_domains:
                # ドメインからのバックリンクを抽出
                domain_backlinks = [backlink for backlink in comp_backlinks if backlink['source_domain'] == domain]
                
                # ドメイン権威スコア（DA）で並べ替え
                sorted_backlinks = sorted(domain_backlinks, key=lambda x: x['domain_authority'], reverse=True)
                
                if sorted_backlinks:
                    valuable_backlinks.append(sorted_backlinks[0])
            
            # 価値の高い順に並べ替え
            valuable_backlinks = sorted(valuable_backlinks, key=lambda x: x['domain_authority'], reverse=True)
            
            link_opportunities[competitor_domain] = valuable_backlinks
        
        # 分析結果の統合
        analysis_results = {
            'own_backlink_domains_count': len(own_backlink_domains),
            'competitor_data': {}
        }
        
        for competitor_domain, opportunities in link_opportunities.items():
            analysis_results['competitor_data'][competitor_domain] = {
                'total_unique_domains': len(opportunities),
                'opportunities': opportunities[:min(20, len(opportunities))]  # 上位20件
            }
        
        logger.info(f"Link Intersect分析完了: {self.url}")
        return analysis_results
    
    def detect_toxic_backlinks(self, backlinks=None, threshold=30):
        """
        悪質なバックリンクを検出
        
        Args:
            backlinks (list, optional): 分析するバックリンクのリスト（指定がない場合は取得）
            threshold (int, optional): 悪質と判断するドメイン権威スコア（DA）のしきい値
            
        Returns:
            dict: 悪質なバックリンクの検出結果
        """
        if backlinks is None:
            backlinks = self.get_backlinks()
        
        if not backlinks:
            return {}
        
        # 悪質なバックリンクの検出
        toxic_backlinks = []
        
        for backlink in backlinks:
            # ドメイン権威スコア（DA）が低い
            is_low_da = backlink['domain_authority'] < threshold
            
            # スパムの可能性がある（モック）
            is_spam = False
            if self.mock_mode:
                # ランダムにスパムフラグを設定（モック）
                is_spam = random.random() < 0.1  # 10%の確率でスパム
            
            # 悪質なアンカーテキスト（モック）
            has_toxic_anchor = False
            toxic_keywords = ['casino', 'gambling', 'viagra', 'cialis', 'porn', 'xxx', 'adult']
            for keyword in toxic_keywords:
                if keyword in backlink['anchor_text'].lower():
                    has_toxic_anchor = True
                    break
            
            # 悪質なバックリンクの判定
            is_toxic = is_low_da or is_spam or has_toxic_anchor
            
            if is_toxic:
                toxic_backlinks.append({
                    'backlink': backlink,
                    'reasons': {
                        'low_domain_authority': is_low_da,
                        'spam_domain': is_spam,
                        'toxic_anchor_text': has_toxic_anchor
                    }
                })
        
        # 分析結果の統合
        analysis_results = {
            'total_backlinks': len(backlinks),
            'toxic_backlinks_count': len(toxic_backlinks),
            'toxic_ratio': len(toxic_backlinks) / len(backlinks) if backlinks else 0,
            'toxic_backlinks': toxic_backlinks
        }
        
        logger.info(f"悪質なバックリンク検出完了: {self.url}")
        return analysis_results
    
    def analyze(self, competitor_urls=None):
        """
        バックリンク分析を実行
        
        Args:
            competitor_urls (list, optional): 競合サイトのURLリスト（Link Intersect分析用）
            
        Returns:
            dict: バックリンク分析結果
        """
        # バックリンクの取得
        backlinks = self.get_backlinks()
        
        if not backlinks:
            logger.error(f"分析失敗: バックリンクが取得できませんでした: {self.url}")
            return {}
        
        # 基本情報
        basic_info = {
            'url': self.url,
            'domain': self.domain
        }
        
        # バックリンク分析
        backlink_analysis = self.analyze_backlinks(backlinks)
        
        # 悪質なバックリンクの検出
        toxic_backlinks = self.detect_toxic_backlinks(backlinks)
        
        # Link Intersect分析（競合URLが指定されている場合）
        link_intersect = {}
        if competitor_urls:
            link_intersect = self.analyze_link_intersect(competitor_urls)
        
        # 分析結果の統合
        analysis_results = {
            'basic_info': basic_info,
            'backlink_analysis': backlink_analysis,
            'toxic_backlinks': toxic_backlinks
        }
        
        if link_intersect:
            analysis_results['link_intersect'] = link_intersect
        
        logger.info(f"バックリンク分析完了: {self.url}")
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
            filename = f"backlink_analysis_{timestamp}.json"
        
        file_path = os.path.join(self.data_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"分析結果を保存しました: {file_path}")
        return file_path
