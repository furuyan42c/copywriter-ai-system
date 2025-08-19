# TCC コピーライターズクラブ データベース完全取得プロジェクト

## 📊 最終成果

- **総データ数**: 37,244件 (99.96%達成)
- **HTMLアーカイブ**: 36,638件
- **詳細分類**: 7カテゴリに体系的分類
- **処理期間**: 2025年8月17日-18日

## 📁 最終ファイル

### 🎯 最重要データ
- `tcc_complete_merged_dataset_20250818_135115.json` - 完全統合データ (JSON)
- `tcc_complete_merged_dataset_20250818_135115.csv` - 完全統合データ (CSV)
- `tcc_merged_dataset_report_20250818_135115.txt` - 統計レポート

### 💾 HTMLアーカイブ
- `complete_html_data/` - 36,638件の圧縮HTMLファイル（研究用原本データ）

### 📄 ドキュメント
- `README_FINAL.md` - 詳細プロジェクト説明
- `requirements.txt` - Python依存関係
- `PROJECT_FINAL_SUMMARY.md` - このファイル

## 🏷️ 詳細分類カテゴリ

| カテゴリ | 説明 | 件数 | 割合 |
|---------|------|------|------|
| 📦 product_info | 商品・企業情報 | 36,594件 | 98.3% |
| 💬 dialogue | 会話・ナレーション | 29,919件 | 80.3% |
| 🏷️ tagline | タグライン・クロージング | 17,514件 | 47.0% |
| 📢 main_headline | メインキャッチフレーズ | 16,819件 | 45.2% |
| 📄 notes | 注釈・備考 | 7,541件 | 20.2% |
| 📖 body_copy | ボディコピー | 2,249件 | 6.0% |
| 📝 sub_headline | サブキャッチフレーズ | 168件 | 0.5% |

## 💡 データ活用方法

### JSON読み込み例
```python
import json
with open('tcc_complete_merged_dataset_20250818_135115.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    
# 特定の分類のみ抽出
headlines = [item for item in data if item.get('main_headline')]
dialogues = [item for item in data if item.get('dialogue')]
taglines = [item for item in data if item.get('tagline')]
```

### CSV活用例
```python
import pandas as pd
df = pd.read_csv('tcc_complete_merged_dataset_20250818_135115.csv', encoding='utf-8-sig')
print(f'総データ数: {len(df):,}件')
```

## ⚠️ 注意事項

- このデータセットは研究・学習目的での利用を想定しています
- 商用利用については、TCC（東京コピーライターズクラブ）の利用規約を確認してください
- データの著作権は各広告主・コピーライターに帰属します

---
最終更新: 2025年08月18日
