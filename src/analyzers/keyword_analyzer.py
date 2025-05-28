"""
SEOマスターパッケージ - キーワードアナライザーモジュール

このモジュールは、Webページのキーワード分析機能を提供します。
キーワード抽出、キーワード密度、検索ボリューム、キーワード難易度、キーワードトラッキングなどの機能を実装しています。
"""

import re
import logging
import math
from collections import Counter
import nltk
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

from src.core.analyzer import SEOAnalyzer

# 必要なNLTKデータのダウンロード（初回実行時のみ）
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')
# ロギングの設定
logger = logging.getLogger(__name__)

class KeywordAnalyzer:
    """Webページのキーワードを分析するクラス"""
    
    def __init__(self, soup, seo_analyzer, language='japanese', mock_mode=True):
        """
        KeywordAnalyzerクラスの初期化
        
        Args:
            soup (BeautifulSoup): 解析対象ページのBeautifulSoupオブジェクト
            seo_analyzer (SEOAnalyzer): 呼び出し元のSEOAnalyzerインスタンス
            language (str, optional): コンテンツの言語（デフォルト: 'japanese'）
            mock_mode (bool, optional): モックモードを使用するかどうか（APIキーがない場合など）
        """
        self.soup = soup
        self.seo_analyzer = seo_analyzer  # 受け取ったインスタンスを保存 ★重要★
        self.url = self.seo_analyzer.url # URLは seo_analyzer から取得
        self.language = language # language は引数から（または seo_analyzer から取得も可）
        self.mock_mode = mock_mode # mock_mode は引数から

        # text_content も seo_analyzer が持っている可能性が高い
        # もし seo_analyzer に self.text_content があればそれを使う方が効率的
        # なければ soup から取得
        if hasattr(self.seo_analyzer, 'text_content'):
             self.text_content = self.seo_analyzer.text_content
        else:
             self.text_content = self.soup.get_text() if self.soup else ''

        # meta_tags も同様
        if hasattr(self.seo_analyzer, 'meta_tags'):
             self.meta_tags = self.seo_analyzer.meta_tags
        else:
             # 必要ならここで self.seo_analyzer.get_meta_tags() を呼ぶか、
             # または KeywordAnalyzer 自身が抽出するロジックを持つ
             # ここでは一旦空にするか、seo_analyzer から取得を試みる
             self.meta_tags = getattr(self.seo_analyzer, 'get_meta_tags', lambda: {})()

        # ストップワードの設定 (言語の扱いを seo_analyzer に合わせるか要検討)
        try:
            self.stopwords = set(nltk.corpus.stopwords.words(self._map_language(self.language)))
        except Exception as e:
            self.stopwords = set()
            logger.warning(f"指定された言語 '{self.language}' のストップワード設定でエラー: {e}")
        
        # データディレクトリの確認 (これはこのままでOK)
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _map_language(self, language):
        """
        言語名をNLTKの言語コードにマッピング
        
        Args:
            language (str): 言語名
            
        Returns:
            str: NLTKの言語コード
        """
        language_map = {
            'japanese': 'japanese',
            'english': 'english',
            'french': 'french',
            'german': 'german',
            'spanish': 'spanish',
            'italian': 'italian',
            'portuguese': 'portuguese',
            'dutch': 'dutch',
            'russian': 'russian'
        }
        
        return language_map.get(language.lower(), 'english')
    
    def extract_keywords(self, top_n=20):
        """
        テキストからキーワードを抽出
        
        Args:
            top_n (int, optional): 抽出する上位キーワードの数
            
        Returns:
            list: 抽出されたキーワードのリスト
        """
        if not self.text_content:
            return []
        
        # テキストをトークン化
        words = nltk.word_tokenize(self.text_content.lower())
        
        # ストップワードと短い単語（1-2文字）を除外
        filtered_words = [word for word in words if word.isalnum() and len(word) > 2 and word not in self.stopwords]
        
        # 単語の出現回数をカウント
        word_counts = Counter(filtered_words)
        
        # 上位キーワードを抽出
        top_keywords = word_counts.most_common(top_n)
        
        return [{'keyword': keyword, 'count': count} for keyword, count in top_keywords]
    
    def extract_keyphrases(self, top_n=10, max_phrase_length=4):
        """
        テキストからキーフレーズを抽出
        
        Args:
            top_n (int, optional): 抽出する上位キーフレーズの数
            max_phrase_length (int, optional): キーフレーズの最大単語数
            
        Returns:
            list: 抽出されたキーフレーズのリスト
        """
        if not self.text_content:
            return []
        
        # テキストをトークン化
        words = nltk.word_tokenize(self.text_content.lower())
        
        # ストップワードと短い単語（1-2文字）を除外
        filtered_words = [word for word in words if word.isalnum() and len(word) > 2 and word not in self.stopwords]
        
        # n-gramの生成
        phrases = []
        for n in range(2, max_phrase_length + 1):
            for i in range(len(filtered_words) - n + 1):
                phrase = ' '.join(filtered_words[i:i+n])
                phrases.append(phrase)
        
        # フレーズの出現回数をカウント
        phrase_counts = Counter(phrases)
        
        # 上位キーフレーズを抽出
        top_keyphrases = phrase_counts.most_common(top_n)
        
        return [{'keyphrase': keyphrase, 'count': count} for keyphrase, count in top_keyphrases]
    
    def analyze_keyword_placement(self, keywords):
        """
        キーワードの配置を分析
        
        Args:
            keywords (list): 分析対象のキーワードリスト
            
        Returns:
            dict: キーワード配置の分析結果
        """
        if not self.soup or not keywords:
            return {}
        
        placement_analysis = {}
        
        for keyword_info in keywords:
            keyword = keyword_info['keyword']
            placement = {
                'in_title': False,
                'in_meta_description': False,
                'in_headings': [],
                'in_url': False,
                'in_first_paragraph': False,
                'in_last_paragraph': False,
                'in_image_alt': False,
                'in_link_text': False
            }
            
            # タイトルでの出現
            title = self.meta_tags.get('title', '')
            if title and keyword in title.lower():
                placement['in_title'] = True
            
            # メタディスクリプションでの出現
            description = self.meta_tags.get('description', '')
            if description and keyword in description.lower():
                placement['in_meta_description'] = True
            
            # 見出しでの出現
            headings = self.seo_analyzer.get_headings()
            for h_level, h_list in headings.items():
                for h_text in h_list:
                    if keyword in h_text.lower():
                        placement['in_headings'].append(h_level)
            
            # URLでの出現
            if keyword in self.url.lower():
                placement['in_url'] = True
            
            # 最初の段落での出現
            paragraphs = self.soup.find_all('p')
            if paragraphs and keyword in paragraphs[0].text.lower():
                placement['in_first_paragraph'] = True
            
            # 最後の段落での出現
            if paragraphs and keyword in paragraphs[-1].text.lower():
                placement['in_last_paragraph'] = True
            
            # 画像のalt属性での出現
            for img in self.soup.find_all('img', alt=True):
                if keyword in img['alt'].lower():
                    placement['in_image_alt'] = True
                    break
            
            # リンクテキストでの出現
            for link in self.soup.find_all('a'):
                if keyword in link.text.lower():
                    placement['in_link_text'] = True
                    break
            
            placement_analysis[keyword] = placement
        
        return placement_analysis
    
    def get_search_volume(self, keywords, country='JP'):
        """
        キーワードの検索ボリュームを取得
        
        Args:
            keywords (list): 検索ボリュームを取得するキーワードのリスト
            country (str, optional): 国コード（デフォルト: 'JP'）
            
        Returns:
            dict: キーワードごとの検索ボリューム
        """
        if self.mock_mode:
            # モックデータを返す
            logger.info("モックモードで検索ボリュームを生成します")
            search_volumes = {}
            for keyword_info in keywords:
                keyword = keyword_info['keyword']
                # ランダムな検索ボリュームを生成（モック）
                search_volumes[keyword] = {
                    'volume': np.random.randint(10, 10000),
                    'trend': np.random.choice(['上昇', '安定', '下降']),
                    'competition': round(np.random.random(), 2)
                }
            return search_volumes
        else:
            # 実際のAPIを使用して検索ボリュームを取得（実装が必要）
            # ここでは例としてモックデータを返す
            logger.warning("検索ボリュームAPIが実装されていません。モックデータを返します。")
            return self.get_search_volume(keywords, country)
    
    def calculate_keyword_difficulty(self, keywords):
        """
        キーワードの難易度スコアを計算
        
        Args:
            keywords (list): 難易度を計算するキーワードのリスト
            
        Returns:
            dict: キーワードごとの難易度スコア
        """
        if self.mock_mode:
            # モックデータを返す
            logger.info("モックモードでキーワード難易度を生成します")
            difficulty_scores = {}
            for keyword_info in keywords:
                keyword = keyword_info['keyword']
                # ランダムな難易度スコアを生成（モック）
                difficulty = np.random.randint(1, 100)
                
                # 難易度の評価
                if difficulty < 30:
                    difficulty_level = '簡単'
                elif difficulty < 60:
                    difficulty_level = '普通'
                else:
                    difficulty_level = '難しい'
                
                difficulty_scores[keyword] = {
                    'score': difficulty,
                    'level': difficulty_level,
                    'competition': round(np.random.random(), 2),
                    'serp_features': np.random.choice(['なし', '特集スニペット', 'ローカルパック', 'ショッピング広告'], size=np.random.randint(0, 3), replace=False).tolist()
                }
            return difficulty_scores
        else:
            # 実際のAPIを使用してキーワード難易度を計算（実装が必要）
            # ここでは例としてモックデータを返す
            logger.warning("キーワード難易度APIが実装されていません。モックデータを返します。")
            return self.calculate_keyword_difficulty(keywords)
    
    def track_keyword_rankings(self, keywords, country='JP'):
        """
        キーワードの検索順位を追跡
        
        Args:
            keywords (list): 追跡するキーワードのリスト
            country (str, optional): 国コード（デフォルト: 'JP'）
            
        Returns:
            dict: キーワードごとの検索順位
        """
        if self.mock_mode:
            # モックデータを返す
            logger.info("モックモードでキーワード順位を生成します")
            rankings = {}
            domain = self.seo_analyzer.domain
            
            for keyword_info in keywords:
                keyword = keyword_info['keyword']
                # ランダムな順位を生成（モック）
                current_rank = np.random.randint(1, 100)
                previous_rank = current_rank + np.random.randint(-10, 10)
                if previous_rank <= 0:
                    previous_rank = current_rank + np.random.randint(1, 10)
                
                # 順位変動
                rank_change = previous_rank - current_rank
                
                rankings[keyword] = {
                    'current_rank': current_rank,
                    'previous_rank': previous_rank,
                    'rank_change': rank_change,
                    'url': f'https://{domain}/page-{np.random.randint(1, 10)}',
                    'last_updated': datetime.now().strftime("%Y-%m-%d")
                }
            return rankings
        else:
            # 実際のAPIを使用してキーワード順位を取得（実装が必要）
            # ここでは例としてモックデータを返す
            logger.warning("キーワード順位追跡APIが実装されていません。モックデータを返します。")
            return self.track_keyword_rankings(keywords, country)
    
    def suggest_related_keywords(self, keywords, country='JP'):
        """
        関連キーワードを提案
        
        Args:
            keywords (list): 関連キーワードを提案するキーワードのリスト
            country (str, optional): 国コード（デフォルト: 'JP'）
            
        Returns:
            dict: キーワードごとの関連キーワード
        """
        if self.mock_mode:
            # モックデータを返す
            logger.info("モックモードで関連キーワードを生成します")
            related_keywords = {}
            
            # 関連キーワードのサンプル（モック）
            sample_related = {
                'ビジネス': ['起業', '経営', '投資', '株式', 'マーケティング', '戦略', 'スタートアップ'],
                'プログラミング': ['Python', 'JavaScript', 'Java', 'C++', 'HTML', 'CSS', 'フレームワーク'],
                'SEO': ['検索エンジン', 'キーワード', 'バックリンク', 'コンテンツ', 'ランキング', 'メタタグ'],
                '健康': ['ダイエット', '運動', '栄養', 'フィットネス', '睡眠', 'ストレス', '食事'],
                '旅行': ['ホテル', '観光', 'ツアー', '航空券', '海外', '国内', 'リゾート']
            }
            
            for keyword_info in keywords:
                keyword = keyword_info['keyword']
                
                # キーワードに関連する単語を選択（モック）
                if keyword in sample_related:
                    related = sample_related[keyword]
                else:
                    # ランダムな関連キーワードを生成
                    all_related = [word for sublist in sample_related.values() for word in sublist]
                    related = np.random.choice(all_related, size=np.random.randint(3, 8), replace=False).tolist()
                
                related_keywords[keyword] = [
                    {
                        'keyword': related_keyword,
                        'search_volume': np.random.randint(10, 5000),
                        'difficulty': np.random.randint(1, 100)
                    } for related_keyword in related
                ]
            
            return related_keywords
        else:
            # 実際のAPIを使用して関連キーワードを取得（実装が必要）
            # ここでは例としてモックデータを返す
            logger.warning("関連キーワード提案APIが実装されていません。モックデータを返します。")
            return self.suggest_related_keywords(keywords, country)
    
    def analyze_basic(self):
        """
        基本的なキーワード分析を実行
        
        Returns:
            dict: 基本的なキーワード分析結果
        """
        if not self.soup:
            logger.error(f"分析失敗: HTMLが取得できていません: {self.url}")
            return {}
        
        # 基本情報
        basic_info = {
            'url': self.url,
            'domain': self.seo_analyzer.domain,
            'language': self.language
        }
        
        # キーワード抽出
        keywords = self.extract_keywords(top_n=20)
        
        # キーフレーズ抽出
        keyphrases = self.extract_keyphrases(top_n=10)
        
        # キーワード配置分析
        keyword_placement = self.analyze_keyword_placement(keywords[:10])
        
        # 分析結果の統合
        analysis_results = {
            'basic_info': basic_info,
            'keywords': keywords,
            'keyphrases': keyphrases,
            'keyword_placement': keyword_placement
        }
        
        logger.info(f"基本キーワード分析完了: {self.url}")
        return analysis_results
    
    def analyze_advanced(self):
        """
        高度なキーワード分析を実行
        
        Returns:
            dict: 高度なキーワード分析結果
        """
        # 基本分析を実行
        basic_analysis = self.analyze_basic()
        
        if not basic_analysis:
            return {}
        
        # 上位キーワードを取得
        top_keywords = basic_analysis['keywords'][:10]
        
        # 検索ボリュームの取得
        search_volumes = self.get_search_volume(top_keywords)
        
        # キーワード難易度の計算
        keyword_difficulty = self.calculate_keyword_difficulty(top_keywords)
        
        # キーワード順位の追跡
        keyword_rankings = self.track_keyword_rankings(top_keywords)
        
        # 関連キーワードの提案
        related_keywords = self.suggest_related_keywords(top_keywords[:5])
        
        # 高度な分析結果を基本分析結果に追加
        advanced_analysis = basic_analysis.copy()
        advanced_analysis.update({
            'search_volumes': search_volumes,
            'keyword_difficulty': keyword_difficulty,
            'keyword_rankings': keyword_rankings,
            'related_keywords': related_keywords
        })
        
        logger.info(f"高度なキーワード分析完了: {self.url}")
        return advanced_analysis
    
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
            filename = f"keyword_analysis_{timestamp}.json"
        
        file_path = os.path.join(self.data_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"分析結果を保存しました: {file_path}")
        return file_path
