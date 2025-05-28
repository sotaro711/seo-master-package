"""
SEOマスターパッケージ - Webインターフェースモジュール

このモジュールは、SEO分析ツールのWebインターフェースを提供します。
Flask Webフレームワークを使用して、ユーザーがブラウザから分析ツールを利用できるようにします。
"""

import os
import json
import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for

# 内部モジュールのインポート
from ..core.analyzer import SEOAnalyzer
from ..analyzers.ads_analyzer import AdsAnalyzer
from ..analyzers.mobile_analyzer import MobileAnalyzer
from ..analyzers.pagespeed_analyzer import PageSpeedAnalyzer
from ..api.search_console_api import SearchConsoleAnalyzer
from ..api.analytics_api import AnalyticsAnalyzer

# Flaskアプリケーションの初期化
app = Flask(__name__)

# 結果保存ディレクトリ
RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'reports')
os.makedirs(RESULTS_DIR, exist_ok=True)

@app.route('/')
def index():
    """
    トップページを表示する
    
    Returns:
        str: レンダリングされたHTMLテンプレート
    """
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    URLを分析する
    
    Returns:
        str: 分析結果ページにリダイレクト
    """
    url = request.form.get('url', '')
    analysis_type = request.form.get('analysis_type', 'seo')
    
    if not url:
        return render_template('index.html', error='URLを入力してください')
    
    # 分析タイプに応じて処理を分岐
    if analysis_type == 'seo':
        # SEO分析を実行
        analyzer = SEOAnalyzer(url)
        result = analyzer.analyze()
        
        # 結果を保存
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"seo_report_{timestamp}.json"
        filepath = os.path.join(RESULTS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return redirect(url_for('show_result', filename=filename))
    
    elif analysis_type == 'ad':
        # 広告分析を実行
        analyzer = AdsAnalyzer(url)
        result = analyzer.analyze()
        
        # 結果を保存
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"ad_report_{timestamp}.json"
        filepath = os.path.join(RESULTS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return redirect(url_for('show_result', filename=filename))
    
    elif analysis_type == 'mobile':
        # モバイルフレンドリー分析を実行
        analyzer = MobileAnalyzer(url)
        result = analyzer.analyze()
        
        # 結果を保存
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"mobile_report_{timestamp}.json"
        filepath = os.path.join(RESULTS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return redirect(url_for('show_result', filename=filename))
    
    elif analysis_type == 'pagespeed':
        # ページ速度分析を実行
        analyzer = PageSpeedAnalyzer(url)
        result = analyzer.analyze()
        
        # 結果を保存
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"pagespeed_report_{timestamp}.json"
        filepath = os.path.join(RESULTS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return redirect(url_for('show_result', filename=filename))
    
    elif analysis_type == 'searchconsole':
        # Google Search Console分析を実行
        analyzer = SearchConsoleAnalyzer(url, mock_mode=True)
        result = analyzer.analyze()
        
        # 結果を保存
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"searchconsole_report_{timestamp}.json"
        filepath = os.path.join(RESULTS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return redirect(url_for('show_result', filename=filename))
    
    elif analysis_type == 'analytics':
        # Google Analytics分析を実行
        analyzer = AnalyticsAnalyzer(url, mock_mode=True)
        result = analyzer.analyze()
        
        # 結果を保存
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"analytics_report_{timestamp}.json"
        filepath = os.path.join(RESULTS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return redirect(url_for('show_result', filename=filename))
    
    elif analysis_type == 'comprehensive':
        # 総合分析を実行（すべての分析を実行して結果を統合）
        results = {}
        
        # SEO基本分析
        seo_analyzer = SEOAnalyzer(url)
        results['seo'] = seo_analyzer.analyze()
        
        # モバイルフレンドリー分析
        mobile_analyzer = MobileAnalyzer(url)
        results['mobile'] = mobile_analyzer.analyze()
        
        # ページ速度分析
        pagespeed_analyzer = PageSpeedAnalyzer(url)
        results['pagespeed'] = pagespeed_analyzer.analyze()
        
        # 広告分析
        ads_analyzer = AdsAnalyzer(url)
        results['ads'] = ads_analyzer.analyze()
        
        # Google Search Console分析
        searchconsole_analyzer = SearchConsoleAnalyzer(url, mock_mode=True)
        results['searchconsole'] = searchconsole_analyzer.analyze()
        
        # Google Analytics分析
        analytics_analyzer = AnalyticsAnalyzer(url, mock_mode=True)
        results['analytics'] = analytics_analyzer.analyze()
        
        # 総合スコアの計算
        total_score = 0
        score_count = 0
        
        # SEOスコア
        if 'score' in results['seo']:
            total_score += results['seo']['score']
            score_count += 1
        
        # モバイルフレンドリースコア
        if 'mobile_friendly_score' in results['mobile']:
            total_score += results['mobile']['mobile_friendly_score']
            score_count += 1
        
        # ページ速度スコア
        if 'page_speed_score' in results['pagespeed']:
            total_score += results['pagespeed']['page_speed_score']
            score_count += 1
        
        # 総合スコアの平均を計算
        comprehensive_score = round(total_score / max(1, score_count))
        
        # 総合評価
        if comprehensive_score >= 90:
            comprehensive_rating = '非常に良好'
        elif comprehensive_score >= 70:
            comprehensive_rating = '良好'
        elif comprehensive_score >= 50:
            comprehensive_rating = '普通'
        else:
            comprehensive_rating = '改善の余地あり'
        
        # 総合的な改善提案の作成
        recommendations = []
        
        # 各分析からの提案を統合
        if 'recommendations' in results['seo']:
            recommendations.extend(results['seo']['recommendations'])
        
        if 'mobile' in results and 'summary' in results['mobile'] and 'recommendations' in results['mobile']:
            for rec in results['mobile'].get('recommendations', []):
                if rec not in recommendations:
                    recommendations.append(rec)
        
        if 'pagespeed' in results:
            for section in ['render_blocking', 'image_optimization', 'minification', 'caching']:
                if section in results['pagespeed'] and 'recommendations' in results['pagespeed'][section]:
                    for rec in results['pagespeed'][section]['recommendations']:
                        if rec not in recommendations:
                            recommendations.append(rec)
        
        if 'searchconsole' in results and 'recommendations' in results['searchconsole']:
            for rec in results['searchconsole']['recommendations']:
                if rec not in recommendations:
                    recommendations.append(rec)
        
        if 'analytics' in results and 'recommendations' in results['analytics']:
            for rec in results['analytics']['recommendations']:
                if rec not in recommendations:
                    recommendations.append(rec)
        
        # 重複を削除し、最大10個の提案に制限
        recommendations = list(set(recommendations))[:10]
        
        # 総合結果の作成
        result = {
            'url': url,
            'domain': results['seo']['domain'],
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'comprehensive_score': comprehensive_score,
            'comprehensive_rating': comprehensive_rating,
            'recommendations': recommendations,
            'detailed_results': results
        }
        
        # 結果を保存
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"comprehensive_report_{timestamp}.json"
        filepath = os.path.join(RESULTS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return redirect(url_for('show_result', filename=filename))
    
    else:
        return render_template('index.html', error='不明な分析タイプです')

@app.route('/result/<filename>')
def show_result(filename):
    """
    分析結果を表示する
    
    Args:
        filename (str): 結果ファイル名
    
    Returns:
        str: レンダリングされたHTMLテンプレート
    """
    filepath = os.path.join(RESULTS_DIR, filename)
    
    if not os.path.exists(filepath):
        return render_template('index.html', error='結果ファイルが見つかりません')
    
    with open(filepath, 'r', encoding='utf-8') as f:
        result = json.load(f)
    
    # ファイル名から分析タイプを判断
    if filename.startswith('seo_'):
        analysis_type = 'seo'
    elif filename.startswith('ad_'):
        analysis_type = 'ad'
    elif filename.startswith('mobile_'):
        analysis_type = 'mobile'
    elif filename.startswith('pagespeed_'):
        analysis_type = 'pagespeed'
    elif filename.startswith('searchconsole_'):
        analysis_type = 'searchconsole'
    elif filename.startswith('analytics_'):
        analysis_type = 'analytics'
    elif filename.startswith('comprehensive_'):
        analysis_type = 'comprehensive'
    else:
        analysis_type = 'unknown'
    
    return render_template('result.html', result=result, analysis_type=analysis_type, filename=filename)

@app.route('/download/<filename>')
def download_result(filename):
    """
    分析結果をダウンロードする
    
    Args:
        filename (str): 結果ファイル名
    
    Returns:
        Response: ファイルダウンロードレスポンス
    """
    return send_from_directory(RESULTS_DIR, filename, as_attachment=True)

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """
    API経由で分析を実行する
    
    Returns:
        Response: JSON形式の分析結果
    """
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({'error': 'URLが指定されていません'}), 400
    
    url = data.get('url')
    analysis_type = data.get('analysis_type', 'seo')
    
    try:
        if analysis_type == 'seo':
            # SEO分析を実行
            analyzer = SEOAnalyzer(url)
            result = analyzer.analyze()
        elif analysis_type == 'ad':
            # 広告分析を実行
            analyzer = AdsAnalyzer(url)
            result = analyzer.analyze()
        elif analysis_type == 'mobile':
            # モバイルフレンドリー分析を実行
            analyzer = MobileAnalyzer(url)
            result = analyzer.analyze()
        elif analysis_type == 'pagespeed':
            # ページ速度分析を実行
            analyzer = PageSpeedAnalyzer(url)
            result = analyzer.analyze()
        elif analysis_type == 'searchconsole':
            # Google Search Console分析を実行
            analyzer = SearchConsoleAnalyzer(url, mock_mode=True)
            result = analyzer.analyze()
        elif analysis_type == 'analytics':
            # Google Analytics分析を実行
            analyzer = AnalyticsAnalyzer(url, mock_mode=True)
            result = analyzer.analyze()
        elif analysis_type == 'comprehensive':
            # 総合分析を実行（すべての分析を実行して結果を統合）
            # 実装は /analyze ルートと同様
            results = {}
            
            # SEO基本分析
            seo_analyzer = SEOAnalyzer(url)
            results['seo'] = seo_analyzer.analyze()
            
            # モバイルフレンドリー分析
            mobile_analyzer = MobileAnalyzer(url)
            results['mobile'] = mobile_analyzer.analyze()
            
            # ページ速度分析
            pagespeed_analyzer = PageSpeedAnalyzer(url)
            results['pagespeed'] = pagespeed_analyzer.analyze()
            
            # 広告分析
            ads_analyzer = AdsAnalyzer(url)
            results['ads'] = ads_analyzer.analyze()
            
            # Google Search Console分析
            searchconsole_analyzer = SearchConsoleAnalyzer(url, mock_mode=True)
            results['searchconsole'] = searchconsole_analyzer.analyze()
            
            # Google Analytics分析
            analytics_analyzer = AnalyticsAnalyzer(url, mock_mode=True)
            results['analytics'] = analytics_analyzer.analyze()
            
            # 総合スコアの計算
            total_score = 0
            score_count = 0
            
            # SEOスコア
            if 'score' in results['seo']:
                total_score += results['seo']['score']
                score_count += 1
            
            # モバイルフレンドリースコア
            if 'mobile_friendly_score' in results['mobile']:
                total_score += results['mobile']['mobile_friendly_score']
                score_count += 1
            
            # ページ速度スコア
            if 'page_speed_score' in results['pagespeed']:
                total_score += results['pagespeed']['page_speed_score']
                score_count += 1
            
            # 総合スコアの平均を計算
            comprehensive_score = round(total_score / max(1, score_count))
            
            # 総合評価
            if comprehensive_score >= 90:
                comprehensive_rating = '非常に良好'
            elif comprehensive_score >= 70:
                comprehensive_rating = '良好'
            elif comprehensive_score >= 50:
                comprehensive_rating = '普通'
            else:
                comprehensive_rating = '改善の余地あり'
            
            # 総合的な改善提案の作成
            recommendations = []
            
            # 各分析からの提案を統合
            if 'recommendations' in results['seo']:
                recommendations.extend(results['seo']['recommendations'])
            
            if 'mobile' in results and 'summary' in results['mobile'] and 'recommendations' in results['mobile']:
                for rec in results['mobile'].get('recommendations', []):
                    if rec not in recommendations:
                        recommendations.append(rec)
            
            if 'pagespeed' in results:
                for section in ['render_blocking', 'image_optimization', 'minification', 'caching']:
                    if section in results['pagespeed'] and 'recommendations' in results['pagespeed'][section]:
                        for rec in results['pagespeed'][section]['recommendations']:
                            if rec not in recommendations:
                                recommendations.append(rec)
            
            if 'searchconsole' in results and 'recommendations' in results['searchconsole']:
                for rec in results['searchconsole']['recommendations']:
                    if rec not in recommendations:
                        recommendations.append(rec)
            
            if 'analytics' in results and 'recommendations' in results['analytics']:
                for rec in results['analytics']['recommendations']:
                    if rec not in recommendations:
                        recommendations.append(rec)
            
            # 重複を削除し、最大10個の提案に制限
            recommendations = list(set(recommendations))[:10]
            
            # 総合結果の作成
            result = {
                'url': url,
                'domain': results['seo']['domain'],
                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'comprehensive_score': comprehensive_score,
                'comprehensive_rating': comprehensive_rating,
                'recommendations': recommendations,
                'detailed_results': results
            }
        else:
            return jsonify({'error': '不明な分析タイプです'}), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports', methods=['GET'])
def api_list_reports():
    """
    保存されたレポートの一覧を取得する
    
    Returns:
        Response: JSON形式のレポート一覧
    """
    reports = []
    
    for filename in os.listdir(RESULTS_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(RESULTS_DIR, filename)
            created_at = datetime.datetime.fromtimestamp(os.path.getctime(filepath))
            
            # ファイル名から分析タイプを判断
            if filename.startswith('seo_'):
                report_type = 'seo'
            elif filename.startswith('ad_'):
                report_type = 'ad'
            elif filename.startswith('mobile_'):
                report_type = 'mobile'
            elif filename.startswith('pagespeed_'):
                report_type = 'pagespeed'
            elif filename.startswith('searchconsole_'):
                report_type = 'searchconsole'
            elif filename.startswith('analytics_'):
                report_type = 'analytics'
            elif filename.startswith('comprehensive_'):
                report_type = 'comprehensive'
            else:
                report_type = 'unknown'
            
            reports.append({
                'filename': filename,
                'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'size': os.path.getsize(filepath),
                'type': report_type
            })
    
    # 作成日時の降順でソート
    reports.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify(reports)

def run_app(host='0.0.0.0', port=5000, debug=False):
    """
    Flaskアプリケーションを実行する
    
    Args:
        host (str, optional): ホスト名
        port (int, optional): ポート番号
        debug (bool, optional): デバッグモードの有効/無効
    """
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_app(debug=True)
