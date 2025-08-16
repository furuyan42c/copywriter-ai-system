import json
import csv
import os
from datetime import datetime
import shutil

def create_final_data_package():
    """最終的なデータパッケージを作成"""
    print("📦 TCC データ 最終パッケージ作成")
    print("=" * 50)
    
    # パッケージディレクトリを作成
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    package_dir = f"TCC_DATA_PACKAGE_{timestamp}"
    os.makedirs(package_dir, exist_ok=True)
    
    # サブディレクトリを作成
    subdirs = ['basic_data', 'detailed_data', 'analysis', 'scripts']
    for subdir in subdirs:
        os.makedirs(os.path.join(package_dir, subdir), exist_ok=True)
    
    print(f"📁 パッケージディレクトリ: {package_dir}")
    
    # 1. 基本データファイルをコピー
    print("\n📋 基本データファイルをパッケージ...")
    basic_files = [
        'tcc_data_100items_20250816_004700.json',
        'tcc_analysis_20250816_004700.json',
        'tcc_export_20250816_005024.csv',
        'tcc_export_20250816_005024_pretty.json'
    ]
    
    for file in basic_files:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join(package_dir, 'basic_data'))
            print(f"  ✅ {file}")
        else:
            print(f"  ⚠️ {file} (見つかりません)")
    
    # 2. 詳細データファイルをコピー
    print("\n📊 詳細データファイルをパッケージ...")
    detailed_files = [
        'tcc_enhanced_20250816_005213.json',
        'tcc_detailed_20250816_005213.csv',
        'tcc_detailed_analysis_20250816_005213.txt'
    ]
    
    for file in detailed_files:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join(package_dir, 'detailed_data'))
            print(f"  ✅ {file}")
        else:
            print(f"  ⚠️ {file} (見つかりません)")
    
    # 3. 分析ファイルをコピー
    print("\n📈 分析ファイルをパッケージ...")
    analysis_files = [
        'tcc_export_20250816_005024_detailed.txt',
        'tcc_export_20250816_005024_copywriters.csv',
        'tcc_summary_report_20250816_004700.md'
    ]
    
    for file in analysis_files:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join(package_dir, 'analysis'))
            print(f"  ✅ {file}")
        else:
            print(f"  ⚠️ {file} (見つかりません)")
    
    # 4. スクリプトファイルをコピー
    print("\n🔧 スクリプトファイルをパッケージ...")
    script_files = [
        'tcc_table_scraper.py',
        'detail_scraper.py',
        'full_crawler.py',
        'simple_export.py'
    ]
    
    for file in script_files:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join(package_dir, 'scripts'))
            print(f"  ✅ {file}")
        else:
            print(f"  ⚠️ {file} (見つかりません)")
    
    # 5. READMEファイルを作成
    readme_content = create_readme_content()
    readme_file = os.path.join(package_dir, 'README.md')
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"\n📝 README.md を作成: {readme_file}")
    
    # 6. データサマリーを作成
    summary_content = create_data_summary()
    summary_file = os.path.join(package_dir, 'DATA_SUMMARY.txt')
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary_content)
    print(f"📊 DATA_SUMMARY.txt を作成: {summary_file}")
    
    # 7. 使用方法ガイドを作成
    guide_content = create_usage_guide()
    guide_file = os.path.join(package_dir, 'USAGE_GUIDE.md')
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    print(f"📖 USAGE_GUIDE.md を作成: {guide_file}")
    
    # パッケージサイズを計算
    total_size = 0
    file_count = 0
    for root, dirs, files in os.walk(package_dir):
        for file in files:
            file_path = os.path.join(root, file)
            total_size += os.path.getsize(file_path)
            file_count += 1
    
    print(f"\n🎉 パッケージ作成完了!")
    print("=" * 50)
    print(f"📁 パッケージディレクトリ: {package_dir}")
    print(f"📊 総ファイル数: {file_count}")
    print(f"💾 総サイズ: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
    
    # ディレクトリ構造を表示
    print(f"\n📂 ディレクトリ構造:")
    for root, dirs, files in os.walk(package_dir):
        level = root.replace(package_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            print(f"{subindent}{file}")
    
    return package_dir

def create_readme_content():
    """READMEファイルの内容を作成"""
    content = f"""# TCC コピラ データパッケージ

作成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}

## 📋 概要

このパッケージには、東京コピーライターズクラブ（TCC）のコピラデータベースから取得した広告データが含まれています。

## 📁 ディレクトリ構造

```
TCC_DATA_PACKAGE/
├── basic_data/          # 基本データ（100件のサンプル）
├── detailed_data/       # 詳細データ（詳細ページ情報付き）
├── analysis/            # 分析結果とレポート
├── scripts/             # データ取得用スクリプト
├── README.md            # このファイル
├── DATA_SUMMARY.txt     # データの概要
└── USAGE_GUIDE.md       # 使用方法ガイド
```

## 🎯 データの種類

### 基本データ
- **tcc_data_100items_*.json**: 一覧ページから取得した基本情報（100件）
- **tcc_export_*.csv**: CSV形式の基本データ
- **tcc_analysis_*.json**: 基本データの分析結果

### 詳細データ
- **tcc_enhanced_*.json**: 詳細ページ情報を含む拡張データ（20件）
- **tcc_detailed_*.csv**: 詳細情報を含むCSV
- **tcc_detailed_analysis_*.txt**: 詳細データの分析結果

### 分析結果
- **tcc_summary_report_*.md**: 全体のサマリーレポート
- **tcc_copywriters.csv**: コピーライター別集計
- **tcc_detailed.txt**: 詳細な統計情報

## 🔧 利用可能なスクリプト

### tcc_table_scraper.py
- 一覧ページから基本データを取得
- 指定件数分のサンプルデータを収集

### detail_scraper.py
- 詳細ページから詳細情報を取得
- 受賞情報、業種、制作会社などの詳細データ

### full_crawler.py
- 全37,259件のデータを取得（時間要）
- 中断・再開機能付き

### simple_export.py
- 既存データの各種形式エクスポート
- CSV、JSON、テキスト形式に対応

## ⚠️ 注意事項

1. **利用規約の遵守**: TCCの利用規約を必ず確認してください
2. **サーバー負荷**: スクレイピング時は適切な間隔を設けてください
3. **データの更新**: データは取得時点のものです
4. **商用利用**: 商用利用前にTCCに確認を取ってください

## 📞 問い合わせ

データに関する問い合わせは、TCCの公式サイトまでお願いします。
https://www.tcc.gr.jp/

## 📜 ライセンス

このパッケージに含まれるスクリプトはMITライセンスです。
データの権利はTCCに帰属します。
"""
    return content

def create_data_summary():
    """データサマリーファイルの内容を作成"""
    # 最新のJSONファイルから統計を取得
    try:
        with open('tcc_data_100items_20250816_004700.json', 'r', encoding='utf-8') as f:
            basic_data = json.load(f)
    except:
        basic_data = []
    
    try:
        with open('tcc_enhanced_20250816_005213.json', 'r', encoding='utf-8') as f:
            detailed_data = json.load(f)
    except:
        detailed_data = []
    
    content = f"""TCC コピラ データサマリー
{'='*60}
作成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}

📊 データ概要
{'-'*30}
基本データ件数: {len(basic_data)}件
詳細データ件数: {len(detailed_data)}件
TCCデータベース総件数: 37,259件（2025年8月時点）

📺 媒体別分布（基本データより）
{'-'*30}
"""
    
    # 媒体別統計
    if basic_data:
        media_count = {}
        for item in basic_data:
            media = item.get('media', 'Unknown')
            media_count[media] = media_count.get(media, 0) + 1
        
        for media, count in sorted(media_count.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(basic_data)) * 100
            content += f"{media:10s}: {count:3d}件 ({percentage:5.1f}%)\n"
    
    content += f"""
📅 年度別分布
{'-'*30}
"""
    
    # 年度別統計
    if basic_data:
        year_count = {}
        for item in basic_data:
            year = str(item.get('year', 'Unknown'))
            year_count[year] = year_count.get(year, 0) + 1
        
        for year, count in sorted(year_count.items(), key=lambda x: x[0] if x[0] != 'Unknown' else '0', reverse=True):
            if year != 'Unknown':
                percentage = (count / len(basic_data)) * 100
                content += f"{year}年: {count:3d}件 ({percentage:5.1f}%)\n"
    
    content += f"""
✍️ コピーライター情報
{'-'*30}
"""
    
    # コピーライター統計
    if basic_data:
        copywriter_count = {}
        for item in basic_data:
            for cw in item.get('copywriters', []):
                name = cw.get('name', 'Unknown')
                copywriter_count[name] = copywriter_count.get(name, 0) + 1
        
        for copywriter, count in sorted(copywriter_count.items(), key=lambda x: x[1], reverse=True)[:10]:
            if copywriter != 'Unknown':
                content += f"{copywriter:20s}: {count:2d}件\n"
    
    content += f"""
🏆 詳細データ情報（詳細取得済み分）
{'-'*30}
"""
    
    if detailed_data:
        award_count = {}
        industry_count = {}
        
        for item in detailed_data:
            detail_info = item.get('detail_info', {})
            if detail_info and 'error' not in detail_info:
                award = detail_info.get('award', '')
                if award:
                    award_count[award] = award_count.get(award, 0) + 1
                
                industry = detail_info.get('industry', '')
                if industry:
                    industry_count[industry] = industry_count.get(industry, 0) + 1
        
        if award_count:
            content += "受賞情報:\n"
            for award, count in sorted(award_count.items(), key=lambda x: x[1], reverse=True):
                content += f"  {award}: {count}件\n"
        
        if industry_count:
            content += "\n業種情報:\n"
            for industry, count in sorted(industry_count.items(), key=lambda x: x[1], reverse=True):
                content += f"  {industry}: {count}件\n"
    
    content += f"""
💡 データ活用のヒント
{'-'*30}
1. 媒体別トレンド分析: TVCM vs WEB の表現手法の違い
2. 年代別コピー変遷: 社会情勢とコピーの関連性
3. コピーライター研究: 個人のスタイルと作品傾向
4. クライアント戦略: ブランド別の一貫性と変化
5. 受賞作品分析: 評価基準と傾向の変化

📈 今後の拡張可能性
{'-'*30}
- 全データ取得（37,259件）
- テキスト解析による自動分類
- 画像データの収集と分析
- 時系列データの可視化
- 類似作品の検索システム

{'='*60}
"""
    
    return content

def create_usage_guide():
    """使用方法ガイドファイルの内容を作成"""
    content = """# TCC データ 使用方法ガイド

## 🚀 クイックスタート

### 1. データの確認
```bash
# 基本データ（JSON形式）
cat basic_data/tcc_data_100items_*.json | jq '.[0]'

# CSV形式で表形式表示
head -5 basic_data/tcc_export_*.csv
```

### 2. 分析結果の確認
```bash
# サマリーレポート
cat analysis/tcc_summary_report_*.md

# 詳細統計
cat analysis/tcc_export_*_detailed.txt
```

## 📊 データ形式

### 基本データ構造（JSON）
```json
{
  "id": "2023352",
  "title": "ファンケル　企業「10gの関係」篇",
  "client": "ファンケル",
  "media": "WEB",
  "year": 2024,
  "detail_url": "https://www.tcc.gr.jp/copira/id/2023352/",
  "copywriters": [
    {
      "name": "関陽子",
      "id": "34211997"
    }
  ]
}
```

### 詳細データ構造（JSON）
```json
{
  "detail_info": {
    "advertiser": "ファンケル",
    "award": "TCC賞",
    "industry": "健康・美容",
    "media_type": "WEB",
    "publication_year": "2024",
    "page_number": "42",
    "copywriter": "関陽子",
    "agency": "博報堂",
    "copy_content": "..."
  }
}
```

## 🔧 スクリプトの使用方法

### データ取得スクリプト

#### 基本データ取得
```bash
python scripts/tcc_table_scraper.py
```
- 最新100件のデータを取得
- CSV、JSON、分析レポートを自動生成

#### 詳細データ取得
```bash
python scripts/detail_scraper.py
```
- 詳細ページから追加情報を取得
- 受賞情報、業種、制作会社などを収集

#### 全データ取得（時間要）
```bash
python scripts/full_crawler.py
```
- 37,259件全てのデータを取得
- チェックポイント機能付き（中断・再開可能）

### データエクスポート

#### 各種形式でエクスポート
```bash
python scripts/simple_export.py
```
- CSV、JSON、テキスト形式に変換
- コピーライター別リストも生成

## 📈 データ分析のアイデア

### 1. 媒体別分析
```python
import json
import pandas as pd

# データ読み込み
with open('basic_data/tcc_data_100items_*.json') as f:
    data = json.load(f)

# 媒体別集計
df = pd.DataFrame(data)
media_counts = df['media'].value_counts()
print(media_counts)
```

### 2. 年代別トレンド
```python
# 年度別集計とグラフ化
import matplotlib.pyplot as plt

year_counts = df['year'].value_counts().sort_index()
year_counts.plot(kind='bar', title='年度別広告件数')
plt.show()
```

### 3. コピーライター分析
```python
# コピーライター別作品数
copywriter_data = []
for item in data:
    for cw in item.get('copywriters', []):
        copywriter_data.append({
            'name': cw['name'],
            'title': item['title'],
            'client': item['client'],
            'year': item['year']
        })

cw_df = pd.DataFrame(copywriter_data)
top_copywriters = cw_df['name'].value_counts().head(10)
print(top_copywriters)
```

### 4. クライアント別分析
```python
# クライアント別作品傾向
client_media = df.groupby('client')['media'].value_counts()
print(client_media)
```

## 🔍 高度な活用方法

### テキスト解析
- タイトルからキーワード抽出
- 感情分析による印象分類
- 類似作品の検索

### 機械学習応用
- 成功作品の特徴分析
- 自動タグ付け
- レコメンデーションシステム

### 可視化
- ネットワーク分析（コピーライター-クライアント関係）
- 時系列ダッシュボード
- インタラクティブな検索システム

## ⚠️ 注意事項

### 利用時の注意
1. **著作権**: データの著作権はTCCに帰属
2. **利用規約**: TCC公式サイトの利用規約を遵守
3. **商用利用**: 事前にTCCへの確認が必要
4. **スクレイピング**: 過度な負荷をかけない

### トラブルシューティング
- **文字化け**: UTF-8エンコーディングを確認
- **データ不整合**: 取得時期による差異の可能性
- **スクリプトエラー**: 依存ライブラリのインストール確認

## 📞 サポート

- TCC公式サイト: https://www.tcc.gr.jp/
- 技術的な質問: 各スクリプトのコメントを参照

## 🔄 アップデート

定期的にデータを更新する場合:
1. スクリプトを再実行
2. 新旧データの比較
3. 差分データの抽出・分析
"""
    return content

if __name__ == "__main__":
    package_dir = create_final_data_package()
    print(f"\n📦 パッケージが作成されました: {package_dir}")
    print("🎯 このパッケージにはスクレイピングしたデータと分析結果が含まれています")
    print("📖 詳細な使用方法は README.md をご確認ください")