"""
SEOマスターパッケージのコンテンツアナライザーモジュール
"""
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class ContentAnalyzer:
    """
    Webページのコンテンツを分析するクラス。
    タイトル、メタディスクリプション、見出し構造、画像、テキスト内容などを分析します。
    """
    
    def __init__(self, soup):
        """
        コンテンツアナライザーを初期化します。
        
        Args:
            soup (BeautifulSoup): 分析対象のBeautifulSoupオブジェクト
        """
        self.soup = soup
    
    def analyze(self):
        """
        コンテンツ分析を実行します。
        
        Returns:
            dict: 分析結果を含む辞書
        """
        # 各情報を取得
        title = self.get_title()
        meta_description = self.get_meta_description()
        word_count = self.get_word_count()
        headings_dict = self.get_headings() # 元のheadings辞書
        images = self.get_images()
        paragraphs = self.get_paragraphs()
        content_quality = self.analyze_content_quality()

        # 各カウントを計算
        paragraph_count = len(paragraphs)
        image_count = len(images)
        heading_count = sum(len(h_list) for h_list in headings_dict.values())

        # headings の構造をテンプレートに合わせて変換
        structured_headings = []
        for level_str, text_list in headings_dict.items():
            try:
                level = int(level_str[1:]) # 'h1' -> 1
                for text in text_list:
                    structured_headings.append({'level': level, 'text': text})
            except (ValueError, IndexError):
                logger.warning(f"Invalid heading tag format encountered: {level_str}")
                continue # 不正な形式の場合はスキップ

        # results 辞書を構築（新しいキーと構造化された headings を含める）
        results = {
            'title': title,
            'meta_description': meta_description,
            'word_count': word_count,
            'paragraph_count': paragraph_count, # 追加
            'image_count': image_count,         # 追加
            'heading_count': heading_count,     # 追加
            'headings': structured_headings,    # 構造を変更したリストを使用
            'images': images,                   # (画像リスト自体はそのまま保持しても良い)
            'paragraphs': paragraphs,           # (段落リスト自体はそのまま保持しても良い)
            'content_quality': content_quality
        }

        return results
    
    def get_title(self):
        """
        ページタイトルを取得します。
        
        Returns:
            str: ページタイトル、見つからない場合は空文字列
        """
        title_tag = self.soup.find('title')
        return title_tag.text.strip() if title_tag else ""
    
    def get_meta_description(self):
        """
        メタディスクリプションを取得します。
        
        Returns:
            str: メタディスクリプション、見つからない場合は空文字列
        """
        meta_desc = self.soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '').strip() if meta_desc else ""
    
    def get_word_count(self):
        """
        ページ内のテキスト単語数を取得します。
        日本語の場合は文字数をカウントします。
        
        Returns:
            int: 単語数または文字数
        """
        text = self.soup.get_text()
        # 空白や改行を削除して文字数をカウント
        cleaned_text = ''.join(text.split())
        return len(cleaned_text)
    
    def get_headings(self):
        """
        ページ内の見出し構造を取得します。
        
        Returns:
            dict: 見出しレベルごとのテキストリスト
        """
        headings = {
            'h1': [],
            'h2': [],
            'h3': [],
            'h4': [],
            'h5': [],
            'h6': []
        }
        
        for level in headings.keys():
            for heading in self.soup.find_all(level):
                headings[level].append(heading.text.strip())
        
        return headings
    
    def get_images(self):
        """
        ページ内の画像情報を取得します。
        
        Returns:
            list: 画像情報（src, alt, width, height）のリスト
        """
        images = []
        for img in self.soup.find_all('img'):
            image_info = {
                'src': img.get('src', ''),
                'alt': img.get('alt', ''),
                'width': img.get('width', ''),
                'height': img.get('height', '')
            }
            images.append(image_info)
        
        return images
    
    def get_paragraphs(self):
        """
        ページ内の段落テキストを取得します。
        
        Returns:
            list: 段落テキストのリスト
        """
        paragraphs = []
        for p in self.soup.find_all('p'):
            text = p.text.strip()
            if text:  # 空の段落は除外
                paragraphs.append(text)
        
        return paragraphs
    
    def analyze_content_quality(self):
        """
        コンテンツの品質を分析します。
        
        Returns:
            dict: コンテンツ品質の分析結果
        """
        title = self.get_title()
        description = self.get_meta_description()
        headings = self.get_headings()
        paragraphs = self.get_paragraphs()
        
        # タイトルの長さをチェック
        title_length = len(title)
        title_score = 0
        if 10 <= title_length <= 60:
            title_score = 100
        elif 60 < title_length <= 70:
            title_score = 80
        elif title_length > 70:
            title_score = 60
        elif 5 <= title_length < 10:
            title_score = 40
        else:
            title_score = 20
        
        # メタディスクリプションの長さをチェック
        desc_length = len(description)
        desc_score = 0
        if 120 <= desc_length <= 155:
            desc_score = 100
        elif 100 <= desc_length < 120 or 155 < desc_length <= 170:
            desc_score = 80
        elif 80 <= desc_length < 100 or 170 < desc_length <= 200:
            desc_score = 60
        elif 50 <= desc_length < 80:
            desc_score = 40
        else:
            desc_score = 20
        
        # 見出し構造をチェック
        heading_score = 0
        if headings['h1'] and len(headings['h1']) == 1:
            heading_score += 50
        if headings['h2']:
            heading_score += 30
        if headings['h3']:
            heading_score += 20
        
        # 段落数をチェック
        paragraph_count = len(paragraphs)
        paragraph_score = 0
        if paragraph_count >= 5:
            paragraph_score = 100
        elif 3 <= paragraph_count < 5:
            paragraph_score = 80
        elif 2 == paragraph_count:
            paragraph_score = 60
        elif 1 == paragraph_count:
            paragraph_score = 40
        else:
            paragraph_score = 0
        
        # 総合スコアを計算
        overall_score = (title_score * 0.3) + (desc_score * 0.2) + (heading_score * 0.3) + (paragraph_score * 0.2)
        
        return {
            'title_score': title_score,
            'description_score': desc_score,
            'heading_score': heading_score,
            'paragraph_score': paragraph_score,
            'overall_score': round(overall_score, 1)
        }
