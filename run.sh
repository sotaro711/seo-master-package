#!/bin/bash
# SEOマスターパッケージ起動スクリプト

# 環境変数の設定
export FLASK_APP=src.web.app
export FLASK_ENV=production
export FLASK_DEBUG=0

# Gunicornでアプリケーションを起動
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 "src.web.app:app"
