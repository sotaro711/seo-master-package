#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SEOマスターパッケージ - メインエントリーポイント

このスクリプトは、SEOマスターパッケージの主要な機能にアクセスするためのコマンドラインインターフェースを提供します。
基本SEO分析、高度SEO分析、広告分析、総合分析などの機能を実行できます。
また、Webインターフェースを起動することもできます。
"""

import argparse
import sys
import os
import logging
from datetime import datetime

# 内部モジュールのインポート
from src.core.analyzer import SEOAnalyzer
from src.analyzers.content_analyzer import ContentAnalyzer
from src.analyzers.link_analyzer import LinkAnalyzer
from src.analyzers.technical_analyzer import TechnicalAnalyzer
from src.analyzers.keyword_analyzer import KeywordAnalyzer
from src.analyzers.backlink_analyzer import BacklinkAnalyzer
#from src.analyzers.competitor_analyzer import CompetitorAnalyzer
from src.analyzers.ads_analyzer import AdsAnalyzer
from src.web.app import run_app

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("seo_master.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_argparse():
    """コマンドライン引数の設定"""
    parser = argparse.ArgumentParser(description='SEOマスターパッケージ - 包括的なSEO分析ツール')
    
    # サブコマンドの設定
    subparsers = parser.add_subparsers(dest='command', help='実行するコマンド')
    
    # 基本SEO分析コマンド
    seo_parser = subparsers.add_parser('seo', help='基本的なSEO分析を実行')
    seo_parser.add_argument('--url', required=True, help='分析対象のURL')
    seo_parser.add_argument('--output', help='出力ファイル名（デフォルト: seo_report_{日時}.html）')
    seo_parser.add_argument('--format', choices=['html', 'pdf'], default='html', help='出力形式（html または pdf）')
    
    # 高度SEO分析コマンド
    seo_advanced_parser = subparsers.add_parser('seo-advanced', help='高度なSEO分析を実行（被リンク分析を含む）')
    seo_advanced_parser.add_argument('--url', required=True, help='分析対象のURL')
    seo_advanced_parser.add_argument('--output', help='出力ファイル名（デフォルト: seo_advanced_report_{日時}.html）')
    seo_advanced_parser.add_argument('--format', choices=['html', 'pdf'], default='html', help='出力形式（html または pdf）')
    
    # 広告分析コマンド
    ads_parser = subparsers.add_parser('ads', help='広告分析を実行')
    ads_parser.add_argument('--url', required=True, help='分析対象のURL')
    ads_parser.add_argument('--output', help='出力ファイル名（デフォルト: ads_report_{日時}.html）')
    ads_parser.add_argument('--format', choices=['html', 'pdf'], default='html', help='出力形式（html または pdf）')
    ads_parser.add_argument('--depth', type=int, default=2, help='クロール深度（デフォルト: 2）')
    ads_parser.add_argument('--timeout', type=int, default=30, help='タイムアウト秒数（デフォルト: 30）')
    
    # 総合分析コマンド
    all_parser = subparsers.add_parser('all', help='すべての分析を実行')
    all_parser.add_argument('--url', required=True, help='分析対象のURL')
    all_parser.add_argument('--output', help='出力ファイル名（デフォルト: full_report_{日時}.html）')
    all_parser.add_argument('--format', choices=['html', 'pdf'], default='html', help='出力形式（html または pdf）')
    
    # Webインターフェース起動コマンド
    parser.add_argument('--web', action='store_true', help='Webインターフェースを起動')
    parser.add_argument('--port', type=int, default=5000, help='Webサーバーのポート番号（デフォルト: 5000）')
    
    return parser

def run_seo_analysis(args):
    """基本的なSEO分析を実行"""
    logger.info(f"基本SEO分析を開始: {args.url}")
    
    # 出力ファイル名の設定
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"seo_report_{timestamp}.{args.format}"
    
    # 分析の実行
    analyzer = SEOAnalyzer(args.url)
    content_analyzer = ContentAnalyzer(args.url)
    link_analyzer = LinkAnalyzer(args.url)
    technical_analyzer = TechnicalAnalyzer(args.url)
    keyword_analyzer = KeywordAnalyzer(args.url)
    
    # 分析結果の取得
    results = {
        'content': content_analyzer.analyze(),
        'links': link_analyzer.analyze(),
        'technical': technical_analyzer.analyze(),
        'keywords': keyword_analyzer.analyze_basic()
    }
    
    # レポートの生成
    if args.format == 'html':
        from src.reporters.html_reporter import HTMLReporter
        reporter = HTMLReporter()
        report_path = reporter.generate_report(results, args.output)
    else:
        from src.reporters.pdf_reporter import PDFReporter
        reporter = PDFReporter()
        report_path = reporter.generate_report(results, args.output)
    
    logger.info(f"基本SEO分析が完了しました。レポート: {report_path}")
    print(f"分析が完了しました。レポート: {report_path}")
    
    return report_path

def run_seo_advanced_analysis(args):
    """高度なSEO分析を実行"""
    logger.info(f"高度なSEO分析を開始: {args.url}")
    
    # 出力ファイル名の設定
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"seo_advanced_report_{timestamp}.{args.format}"
    
    # 分析の実行
    analyzer = SEOAnalyzer(args.url)
    content_analyzer = ContentAnalyzer(args.url)
    link_analyzer = LinkAnalyzer(args.url)
    technical_analyzer = TechnicalAnalyzer(args.url)
    keyword_analyzer = KeywordAnalyzer(args.url)
    backlink_analyzer = BacklinkAnalyzer(args.url)
    competitor_analyzer = CompetitorAnalyzer(args.url)
    
    # 分析結果の取得
    results = {
        'content': content_analyzer.analyze(),
        'links': link_analyzer.analyze(),
        'technical': technical_analyzer.analyze(),
        'keywords': keyword_analyzer.analyze_advanced(),
        'backlinks': backlink_analyzer.analyze(),
        'competitors': competitor_analyzer.analyze()
    }
    
    # レポートの生成
    if args.format == 'html':
        from src.reporters.html_reporter import HTMLReporter
        reporter = HTMLReporter()
        report_path = reporter.generate_report(results, args.output)
    else:
        from src.reporters.pdf_reporter import PDFReporter
        reporter = PDFReporter()
        report_path = reporter.generate_report(results, args.output)
    
    logger.info(f"高度なSEO分析が完了しました。レポート: {report_path}")
    print(f"分析が完了しました。レポート: {report_path}")
    
    return report_path

def run_ads_analysis(args):
    """広告分析を実行"""
    logger.info(f"広告分析を開始: {args.url}")
    
    # 出力ファイル名の設定
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"ads_report_{timestamp}.{args.format}"
    
    # 分析の実行
    ads_analyzer = AdsAnalyzer(args.url, depth=args.depth, timeout=args.timeout)
    
    # 分析結果の取得
    results = ads_analyzer.analyze()
    
    # レポートの生成
    if args.format == 'html':
        from src.reporters.html_reporter import HTMLReporter
        reporter = HTMLReporter()
        report_path = reporter.generate_report(results, args.output)
    else:
        from src.reporters.pdf_reporter import PDFReporter
        reporter = PDFReporter()
        report_path = reporter.generate_report(results, args.output)
    
    logger.info(f"広告分析が完了しました。レポート: {report_path}")
    print(f"分析が完了しました。レポート: {report_path}")
    
    return report_path

def run_all_analysis(args):
    """すべての分析を実行"""
    logger.info(f"総合分析を開始: {args.url}")
    
    # 出力ファイル名の設定
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"full_report_{timestamp}.{args.format}"
    
    # 分析の実行
    analyzer = SEOAnalyzer(args.url)
    content_analyzer = ContentAnalyzer(args.url)
    link_analyzer = LinkAnalyzer(args.url)
    technical_analyzer = TechnicalAnalyzer(args.url)
    keyword_analyzer = KeywordAnalyzer(args.url)
    backlink_analyzer = BacklinkAnalyzer(args.url)
    competitor_analyzer = CompetitorAnalyzer(args.url)
    ads_analyzer = AdsAnalyzer(args.url)
    
    # 分析結果の取得
    results = {
        'content': content_analyzer.analyze(),
        'links': link_analyzer.analyze(),
        'technical': technical_analyzer.analyze(),
        'keywords': keyword_analyzer.analyze_advanced(),
        'backlinks': backlink_analyzer.analyze(),
        'competitors': competitor_analyzer.analyze(),
        'ads': ads_analyzer.analyze()
    }
    
    # レポートの生成
    if args.format == 'html':
        from src.reporters.html_reporter import HTMLReporter
        reporter = HTMLReporter()
        report_path = reporter.generate_report(results, args.output)
    else:
        from src.reporters.pdf_reporter import PDFReporter
        reporter = PDFReporter()
        report_path = reporter.generate_report(results, args.output)
    
    logger.info(f"総合分析が完了しました。レポート: {report_path}")
    print(f"分析が完了しました。レポート: {report_path}")
    
    return report_path

def run_web_interface(args):
    """Webインターフェースを起動"""
    logger.info(f"Webインターフェースを起動: ポート {args.port}")
    run_app(port=args.port, debug=True)

def main():
    """メイン関数"""
    parser = setup_argparse()
    args = parser.parse_args()
    
    # コマンドに基づいて処理を実行
    if args.web:
        run_web_interface(args)
    elif args.command == 'seo':
        run_seo_analysis(args)
    elif args.command == 'seo-advanced':
        run_seo_advanced_analysis(args)
    elif args.command == 'ads':
        run_ads_analysis(args)
    elif args.command == 'all':
        run_all_analysis(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
