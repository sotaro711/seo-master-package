# SEOマスターパッケージ

包括的なSEO分析と競合広告分析のための統合ツールパッケージです。

## 概要

SEOマスターパッケージは、以下の3つのツールを統合した包括的なSEO分析ソリューションです：

1. **基本SEO分析ツール** - コンテンツ分析、リンク分析、技術的SEO分析などの基本機能
2. **高度SEO分析ツール** - 被リンク分析、高度なキーワード調査、API連携などの高度な機能
3. **競合広告分析ツール** - 競合サイトの広告戦略分析機能

このパッケージを使用することで、Webサイトの総合的なSEO状況を分析し、改善点を特定できます。

## 主な機能

### SEO分析機能

- **コンテンツ分析**: 文字数、見出し構造、キーワード密度など
- **リンク分析**: 内部/外部リンク、リンク切れ検出
- **技術的SEO分析**: メタタグ、モバイルフレンドリー、ページ速度要因
- **被リンク分析**: 外部サイトからの被リンク（バックリンク）分析
- **Link Intersect分析**: 競合が獲得しているが自社が獲得できていないリンクの特定
- **キーワード分析**: 検索ボリューム、キーワード難易度、キーワードトラッキング
- **競合分析**: 競合サイトのSEO状況の分析

### 広告分析機能

- **Google広告分析**: 検索広告、ディスプレイ広告の収集と分析
- **ソーシャルメディア広告分析**: Facebook、Instagram、Twitter、LinkedInなどの広告収集と分析
- **広告データの総合分析**: プラットフォーム別分析、広告種類・フォーマット分析、キーワード分析、テキスト分析

### API連携

- **Google Search Console API連携**: 検索パフォーマンスデータの取得と分析
- **Google Analytics API連携**: アクセス解析データの取得と分析

## インストール

```bash
# リポジトリのクローン
git clone https://github.com/yourusername/seo-master-package.git
cd seo-master-package

# 依存パッケージのインストール
pip install -r requirements.txt
```

## 使用方法

### コマンドラインからの実行

```bash
# 基本的なSEO分析
python main.py seo --url https://example.com

# 高度なSEO分析（被リンク分析を含む）
python main.py seo-advanced --url https://example.com

# 広告分析
python main.py ads --url https://example.com

# 総合分析（すべての分析を実行）
python main.py all --url https://example.com
```

### Webインターフェースからの実行

```bash
python main.py --web
```

ブラウザで http://localhost:5000 にアクセスし、分析対象のURLを入力して分析タイプを選択します。

## ディレクトリ構造

```
seo_master_package/
├── src/                   # ソースコード
│   ├── core/              # コア機能
│   ├── analyzers/         # 分析モジュール
│   ├── collectors/        # データ収集モジュール
│   ├── api/               # API連携モジュール
│   ├── processors/        # データ処理モジュール
│   ├── reporters/         # レポート生成モジュール
│   ├── utils/             # ユーティリティ
│   └── web/               # Webインターフェース
├── tests/                 # テストコード
├── data/                  # データディレクトリ
└── docs/                  # ドキュメント
```

## ドキュメント

詳細な使用方法については、以下のドキュメントを参照してください：

- [ユーザーガイド](docs/user_guide.md): 使用方法、機能、レポートの見方などの詳細
- [技術仕様書](docs/technical_spec.md): システムアーキテクチャ、実装詳細、拡張方法など
- [API参照ドキュメント](docs/api_reference.md): API連携の詳細
- [使用例](docs/examples/): 具体的な使用例

## 注意事項

- このツールは分析を目的としており、収集したデータは社内での分析にのみ使用してください
- 一部の機能では、APIの制限により完全なデータが取得できない場合があります
- 分析対象サイトのロボット排除方針（robots.txt）を尊重してください

## ライセンス

このプロジェクトは [MIT License](LICENSE) のもとで公開されています。

## 貢献

バグ報告や機能リクエストは、GitHubのIssueトラッカーを使用してください。プルリクエストも歓迎します。
