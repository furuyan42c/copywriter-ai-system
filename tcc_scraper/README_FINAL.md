# TCC コピーライターズクラブ データベース完全取得プロジェクト

## 📊 最終成果

### 取得データ概要
- **総データ数**: 37,244件 (99.96%達成)
- **HTML保存数**: 36,638件
- **コピー本文抽出**: 37,242件 (100%成功)
- **処理期間**: 2025年8月17日-18日 (約15時間)

### 📁 ディレクトリ構造

```
tcc_scraper/
├── README_FINAL.md              # このファイル
├── requirements.txt              # 必要なPythonパッケージ
│
├── complete_html_data/           # 【重要】HTMLアーカイブ (36,638ファイル)
│   └── tcc_[ID].html.gz         # 各詳細ページのHTML (gzip圧縮)
│
├── complete_parsed_data/         # 【重要】最終データ
│   ├── tcc_complete_with_html_20250818_100008.json  # 完全JSON (37,244件)
│   ├── tcc_complete_with_html_20250818_100008.csv   # CSV版
│   ├── tcc_complete_final_stats_20250818_100008.txt # 統計レポート
│   └── tcc_complete_errors_20250818_100008.json     # エラーログ
│
├── final_tcc_crawler.py          # 初回25,000件取得スクリプト
├── complete_remaining_crawler.py # 残り12,259件取得スクリプト
├── complete_html_crawler.py      # 全データHTML保存スクリプト
├── copy_text_extractor.py        # コピー本文抽出改善スクリプト
├── html_saver_crawler.py         # HTML保存テストスクリプト
│
└── archive/                      # アーカイブフォルダ
    ├── old_crawlers/            # 使用済みスクリプト
    ├── test_data/               # テストデータ
    ├── interim_data/            # 中間保存ファイル
    ├── tcc_complete_data/       # 初期データ
    ├── tcc_corrected_data/      # 修正版データ
    └── tcc_final_data/          # 最終版データ
```

## 📈 データ品質

### フィールド充足率
- 広告主 (advertiser): 99.9%
- コピーライター (copywriter): 99.8%
- 年度 (year): 100%
- 媒体 (media_type): 100%
- **コピー本文 (copy_text): 100%** ✨
- 業種 (industry): 99.9%
- 受賞情報 (award): 23.2%
- サブタイトル (subtitle): 20.4%

### 媒体別内訳
- 新聞: 9,745件
- TVCM: 9,074件
- ポスター: 8,746件
- 雑誌: 3,588件
- その他: 3,054件
- ラジオCM: 1,567件
- WEB: 1,029件
- パンフレット: 235件
- ネーミング: 201件

## 📂 重要ファイル一覧

### 📊 最終データファイル（必須）
| ファイル名 | 説明 | 用途 |
|------------|------|------|
| `tcc_complete_with_html_20250818_100008.json` | 全37,244件の完全データ（JSON） | プログラム処理、データ分析 |
| `tcc_complete_with_html_20250818_100008.csv` | 全37,244件の完全データ（CSV） | Excel、表計算ソフト用 |
| `tcc_complete_final_stats_20250818_100008.txt` | 詳細統計レポート | データ概要把握 |
| `tcc_complete_errors_20250818_100008.json` | エラーログ（14件） | 失敗データの確認 |

### 💾 HTMLアーカイブ（研究用）
| ディレクトリ/ファイル | 説明 | 用途 |
|----------------------|------|------|
| `complete_html_data/` | 36,638件のHTMLファイル | 原本データ、再解析 |
| `tcc_[ID].html.gz` | 各詳細ページのHTML（gzip圧縮） | 元データの参照、構造分析 |

### 🛠️ 実行スクリプト（参考用）
| ファイル名 | 説明 | 用途 |
|------------|------|------|
| `complete_html_crawler.py` | 最終完全クローラー | 全データ取得の実行 |
| `final_tcc_crawler.py` | 初回25,000件取得 | 初期データ収集 |
| `complete_remaining_crawler.py` | 残り12,259件取得 | 補完データ収集 |
| `copy_text_extractor.py` | コピー本文抽出改善 | テキスト抽出ロジック |
| `html_saver_crawler.py` | HTML保存テスト | 保存機能テスト |

### ⚙️ 設定・依存関係
| ファイル名 | 説明 | 用途 |
|------------|------|------|
| `requirements.txt` | Pythonパッケージ一覧 | 環境構築 |
| `README_FINAL.md` | このファイル | プロジェクト説明書 |

### 📁 アーカイブフォルダ
| ディレクトリ | 説明 | 内容 |
|-------------|------|------|
| `archive/old_crawlers/` | 使用済みスクリプト | 開発履歴 |
| `archive/test_data/` | テストデータ | 動作確認用 |
| `archive/interim_data/` | 中間保存ファイル | 処理途中データ |
| `archive/tcc_complete_data/` | 初期完全データ | 第1段階成果 |
| `archive/tcc_corrected_data/` | 修正版データ | 第2段階成果 |
| `archive/tcc_final_data/` | 最終版データ | 第3段階成果 |

## 🔧 データ活用方法

### JSONファイルの読み込み
```python
import json

# データ読み込み
with open('complete_parsed_data/tcc_complete_with_html_20250818_100008.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# サンプル表示
for item in data[:5]:
    print(f"広告主: {item.get('advertiser')}")
    print(f"コピー: {item.get('copy_text')}")
    print(f"年度: {item.get('year')}")
    print("---")
```

### CSVファイルの活用
```python
import pandas as pd

# CSV読み込み
df = pd.read_csv('complete_parsed_data/tcc_complete_with_html_20250818_100008.csv', encoding='utf-8-sig')

# 年度別集計
year_counts = df['year'].value_counts()
print(year_counts.head(10))
```

### 保存されたHTMLの解凍と参照
```python
import gzip

# HTMLファイルの解凍と読み込み
with gzip.open('complete_html_data/tcc_2017493.html.gz', 'rt', encoding='utf-8') as f:
    html_content = f.read()
```

## 📝 主要な成果

1. **完全なコピー本文抽出**: これまで困難だったコピー本文の100%抽出に成功
2. **HTMLアーカイブ**: 36,638件の詳細ページHTMLを圧縮保存（将来の再解析可能）
3. **構造化データ**: 全フィールドを正規化した使いやすいJSON/CSV形式
4. **高い成功率**: 99.96%のデータ取得成功率

## ⚠️ 注意事項

- HTMLファイルは圧縮されています（.gz形式）
- データの商用利用については、TCCの利用規約を確認してください
- 大量のファイルがあるため、操作時は注意してください

## 🛠️ 環境構築

```bash
# 仮想環境作成
python3 -m venv venv
source venv/bin/activate

# パッケージインストール
pip install -r requirements.txt
```

## 📞 問い合わせ

このデータセットに関する質問や問題がある場合は、プロジェクト管理者にお問い合わせください。

---

最終更新: 2025年8月18日