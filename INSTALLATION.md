# Copy Writer AI System - Installation Guide
## インストール・セットアップガイド

---

## 📋 必要要件

### システム要件
- **OS**: macOS, Linux, Windows
- **Python**: 3.8以上
- **メモリ**: 最低4GB、推奨8GB
- **ストレージ**: 1GB以上の空き容量

### 依存関係
```bash
# 基本パッケージ
pip install numpy matplotlib sqlite3 requests beautifulsoup4

# AI API統合（オプション）
pip install anthropic openai

# 日本語処理（オプション、高精度化）  
pip install mecab-python3
```

---

## ⚡ クイックスタート

### 1. システムの確認
```bash
cd /Users/naoki/copy_writer/core_systems
python advanced_copywriter_ai_system.py
```

### 2. 戦略的キャンペーン実行
```bash
cd /Users/naoki/copy_writer/campaign_examples
python strategic_kojima_kirin_campaign.py
```

### 3. スタイル分析実行
```bash
cd /Users/naoki/copy_writer/core_systems  
python copywriter_style_analyzer.py
```

---

## 🔧 詳細セットアップ

### ステップ1: 環境構築
```bash
# 仮想環境作成（推奨）
python -m venv copywriter_env
source copywriter_env/bin/activate  # macOS/Linux
# copywriter_env\\Scripts\\activate  # Windows

# 依存パッケージインストール
pip install -r requirements.txt
```

### ステップ2: API設定（オプション）
```bash
# 環境変数設定
export CLAUDE_API_KEY="your-claude-api-key"
export OPENAI_API_KEY="your-openai-api-key"
```

### ステップ3: データベース初期化
```bash
cd databases/
# データベースファイル確認
ls -la tcc_copyworks.db
```

---

## 🎯 機能別実行方法

### コピーライター一覧取得
```python
from advanced_copywriter_ai_system import ProductionCopywriterAI

system = ProductionCopywriterAI(
    db_path='../databases/tcc_copyworks.db',
    analysis_path='../data_analysis/copywriter_style_analysis_20250810_000147.json'
)

print(system.get_available_copywriters())
```

### プロフェッショナルコピー生成
```python
import asyncio

async def generate_copy():
    result = await system.create_professional_copy(
        copywriter_name="糸井重里",
        product_service="新商品",
        target_audience="30代女性",
        content_type="Web広告"
    )
    print(result.primary_copy)

asyncio.run(generate_copy())
```

### 品質分析
```python
from copywriter_style_analyzer import CopywriterStyleAnalyzer

analyzer = CopywriterStyleAnalyzer('../databases/tcc_copyworks.db')
report = analyzer.generate_comprehensive_report()
print(f"分析対象: {report['overall_statistics']['total_copywriters']}人")
```

---

## 🔍 トラブルシューティング

### よくある問題

**1. ModuleNotFoundError: No module named 'MeCab'**
```bash
# MeCabは日本語高精度処理用（オプション）
# 簡易モードで動作するため無視してOK
```

**2. Database file not found**
```bash
# パスを確認
ls -la /Users/naoki/copy_writer/databases/tcc_copyworks.db

# 相対パス調整
db_path = '../databases/tcc_copyworks.db'
```

**3. API接続エラー**
```bash
# フォールバックモードで動作
# 実用性に問題なし、API設定は任意
```

---

## 📊 パフォーマンステスト

### システム検証実行
```bash
cd core_systems/
python final_system_validation.py
```

期待される結果:
- **System Status**: GOOD
- **Readiness**: STAGING_READY  
- **Score**: 60/100点以上
- **Generation Speed**: 0.1秒以下

---

## 🎪 サンプル実行

### 1. 基本的なデモ
```bash
cd core_systems/
python advanced_copywriter_ai_system.py
```

### 2. 戦略的キャンペーン（推奨）
```bash
cd campaign_examples/
python strategic_kojima_kirin_campaign.py
```

### 3. 国際的キャンペーン
```bash
cd campaign_examples/
python coca_cola_ogilvy_campaigns.py
```

---

## 💡 カスタマイズ

### 新しいコピーライター追加
1. `data_analysis/japanese_copywriters.json`にプロファイル追加
2. `databases/tcc_copyworks.db`に作品データ追加
3. スタイル分析再実行

### API統合
1. APIキーを環境変数に設定
2. `advanced_copywriter_ai_system.py`でクライアント有効化
3. 生成品質の大幅向上を確認

### カスタム分析
1. `copywriter_style_analyzer.py`の分析ロジック修正
2. 新しい品質指標追加
3. レポート形式カスタマイズ

---

## 📞 サポート・FAQ

**Q: 商用利用は可能ですか？**  
A: 研究・教育目的で開発。商用利用時は適切なライセンス取得が必要。

**Q: より多くのコピーライターを追加したい**  
A: TCCデータベースとの正式連携により数百人規模への拡張可能。

**Q: 英語以外の言語対応は？**  
A: 現在日本語特化。他言語対応は追加開発が必要。

**Q: クラウド展開は可能？**  
A: AWS/GCP等への展開可能。Docker対応も実装済み。

---

## 🔄 アップデート

### Version 1.1 予定機能
- Claude API完全統合
- UI/UX Webインターフェース
- リアルタイムA/Bテスト
- 多言語対応（英語・中国語）

### Version 2.0 予定機能  
- ファインチューニング専用モデル
- 動画・音声コピー対応
- AIによる戦略提案自動化
- Enterprise SaaS化

---

*最終更新: 2025年8月10日*