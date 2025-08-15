# GitHub セットアップガイド - コピーライターAIシステム

## 1. 初回GitHubアップロード手順

### GitHubリポジトリ作成
1. GitHubにログインし、「New repository」をクリック
2. リポジトリ名: `copywriter-ai-system` または `ai-copywriting-tool`
3. Description: `AI駆動のコピーライティングシステム - 世界の著名コピーライターのスタイル分析と再現`
4. Public または Private を選択
5. 「Create repository」をクリック

### ローカルリポジトリとの接続
```bash
cd /Users/naoki/copy_writer

# リモートリポジトリを追加
git remote add origin https://github.com/[ユーザー名]/[リポジトリ名].git

# ブランチ名をmainに変更（推奨）
git branch -M main

# 初回プッシュ
git push -u origin main
```

## 2. 継続的な開発・運用ルール

### ブランチ戦略
```bash
# 新しいコピーライター追加時
git checkout -b feature/add-copywriter-name
git add .
git commit -m "feat: [コピーライター名]のスタイル分析を追加"
git push origin feature/add-copywriter-name

# 新キャンペーン開発時
git checkout -b campaign/brand-name-campaign
git commit -m "campaign: [ブランド名]キャンペーン戦略を追加"

# バグ修正時
git checkout -b hotfix/fix-style-analysis
git commit -m "fix: スタイル分析エンジンのバグ修正"
```

### コミットメッセージ規約
- `feat: 新機能追加`
- `campaign: 新キャンペーン戦略`
- `copywriter: 新コピーライター追加`
- `style: スタイル分析改善`
- `ai: AI機能強化`
- `fix: バグ修正`
- `docs: ドキュメント更新`
- `test: テスト追加・修正`

### 開発フロー

#### 新コピーライター追加時
1. **ブランチ作成**
   ```bash
   git checkout -b feature/add-john-caples
   ```

2. **データ収集・分析**
   ```bash
   # 作品データ収集
   python core_systems/tcc_data_scraper.py --copywriter "John Caples"
   
   # スタイル分析実行
   python core_systems/copywriter_style_analyzer.py --analyze "John Caples"
   
   # データベース更新
   python core_systems/japanese_copywriters_database.py --add-copywriter
   ```

3. **検証・テスト**
   ```bash
   # システム検証
   python core_systems/final_system_validation.py --test-new-copywriter
   
   # キャンペーン生成テスト
   python campaign_examples/test_new_copywriter_campaign.py
   ```

4. **コミット・プッシュ**
   ```bash
   git add .
   git commit -m "copywriter: John Caplesのスタイル分析とデータベースエントリを追加"
   git push origin feature/add-john-caples
   ```

### データ管理ルール

#### コピーライターデータ管理
```bash
# データファイルの命名規則
data_analysis/copywriter_[名前]_analysis_YYYYMMDD.json
databases/copywriter_[名前]_works.csv

# 重要なデータのみコミット
git add data_analysis/significant_analyses/
git commit -m "data: 高精度スタイル分析結果を追加"
```

#### .gitignore重要項目
- ✅ `*.log` - システムログ
- ✅ `data_analysis/*.json` - 一時的な分析結果
- ✅ `databases/*.db` - データベースファイル
- ✅ `api_keys.py` - APIキー
- ✅ `.cache/` - AIモデルキャッシュ

## 3. プロジェクト管理

### Issue分類
- **🎨 Style**: スタイル分析機能
- **✍️ Copywriter**: 新コピーライター追加
- **🎪 Campaign**: キャンペーン開発
- **🤖 AI**: AI機能強化
- **🐛 Bug**: システムの不具合
- **📚 Documentation**: ドキュメント整備

### スタイル品質基準
```python
# コピー品質評価基準
quality_metrics = {
    "style_accuracy": 0.8,      # スタイル再現精度 80%以上
    "readability_score": 0.7,   # 読みやすさ 70%以上
    "persuasion_power": 0.75,   # 説得力 75%以上
    "brand_fit": 0.8           # ブランド適合性 80%以上
}
```

### GitHub Actions設定例
```yaml
# .github/workflows/copywriter-ai-ci.yml
name: Copywriter AI CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run style analysis tests
        run: |
          python core_systems/copywriter_style_analyzer.py --test
      - name: Run system validation
        run: |
          python core_systems/final_system_validation.py --ci-mode
```

## 4. セキュリティ・ベストプラクティス

### APIキー管理
```bash
# config.py.example を用意
OPENAI_API_KEY = "your_openai_key_here"
CLAUDE_API_KEY = "your_claude_key_here"
TCC_API_ACCESS = "your_tcc_access_token"
```

### 著作権・コンプライアンス
- **重要**: 実際のコピー作品の取り扱いに注意
- **推奨**: 分析データのみ保存、原文は外部参照
- **禁止**: 著作権で保護された作品の無断使用

### データプライバシー
```python
# 良い例: 匿名化されたデータ
anonymized_data = {
    "copywriter_id": "CW001",
    "style_metrics": {...},
    "anonymized_samples": [...]
}

# 悪い例: 個人情報を含むデータ
# personal_data = {"real_name": "...", "contact": "..."}  # NG
```

## 5. リリース管理

### バージョン管理
```bash
# メジャーアップデート（新AI統合）
git tag -a v2.0.0 -m "Claude API統合バージョン"

# マイナーアップデート（新コピーライター追加）
git tag -a v1.1.0 -m "海外コピーライター5名追加"

# パッチ（バグ修正）
git tag -a v1.0.1 -m "スタイル分析精度改善"

git push origin --tags
```

### リリースノート例
```markdown
## v2.0.0 - Claude API統合バージョン

### 新機能
- Claude API統合による高精度コピー生成
- リアルタイムスタイル分析
- 戦略的キャンペーン生成機能

### 新コピーライター
- David Ogilvy（完全対応）
- Leo Burnett（スタイル分析追加）

### 改善
- スタイル再現精度: 75% → 88%
- 生成速度: 50%向上
```

## 6. キャンペーン開発プロセス

### 新キャンペーン開発手順
1. **ブリーフィング分析**
   ```bash
   python campaign_examples/analyze_brief.py --client "Brand Name"
   ```

2. **コピーライター選定**
   ```bash
   python core_systems/copywriter_matcher.py --brand-style "premium luxury"
   ```

3. **キャンペーン生成**
   ```bash
   python campaign_examples/generate_campaign.py --copywriter "Kojima Reiko" --brand "Kirin"
   ```

4. **品質評価**
   ```bash
   python core_systems/campaign_quality_evaluator.py --campaign-id "CMP001"
   ```

### キャンペーンファイル命名規則
```
campaign_examples/
├── [ブランド名]_[コピーライター名]_campaign.py
├── [ブランド名]_[コピーライター名]_presentation.md
└── [ブランド名]_[コピーライター名]_data.json
```

## 7. デプロイメント

### 本番環境セットアップ
```bash
# 依存関係インストール
pip install -r requirements.txt

# データベース初期化
python core_systems/database_initializer.py

# システム設定
cp config.py.example config.py
# config.pyを編集してAPIキーを設定

# 初回テスト実行
python core_systems/final_system_validation.py
```

### 推奨実行環境
- **開発環境**: ローカルマシン（Mac/Windows/Linux）
- **本番環境**: クラウドサーバー（GPU推奨）
- **AI処理**: 高メモリVPS または GPU インスタンス

## 8. 品質管理

### 日次チェック項目
```bash
# システム稼働状況
python core_systems/system_health_check.py

# スタイル分析精度
python core_systems/style_accuracy_monitor.py

# キャンペーン品質
python campaign_examples/quality_assessment.py --daily
```

### 週次分析
```bash
# 包括的品質評価
python core_systems/comprehensive_quality_assessment.py

# 新しいスタイルパターン検出
python core_systems/pattern_discovery.py

# コピーライターデータベース更新
python core_systems/database_updater.py --weekly-sync
```

## 9. トラブルシューティング

### よくある問題

#### 1. AI API接続エラー
```bash
# APIキー確認
python -c "import config; print('API Keys loaded successfully')"

# 接続テスト
python core_systems/api_connection_test.py
```

#### 2. スタイル分析精度低下
```bash
# データ整合性チェック
python core_systems/data_integrity_check.py

# 分析エンジン再較正
python core_systems/recalibrate_style_analyzer.py
```

#### 3. メモリ不足
```bash
# 軽量モード実行
python core_systems/lightweight_copywriter_ai.py

# メモリ使用量監視
python core_systems/memory_monitor.py
```

## 10. 貢献ガイドライン

### コードレビュー基準
- [ ] スタイル分析結果が改善されている
- [ ] 新コピーライターの品質基準クリア
- [ ] キャンペーン生成テスト通過
- [ ] 著作権・コンプライアンスチェック完了
- [ ] ドキュメント更新済み

### 新コピーライター追加プロセス
1. **コピーライター選定・調査**
2. **作品データ収集（適法性確認）**
3. **スタイル分析実装**
4. **品質評価テスト**
5. **コードレビュー**
6. **データベース統合**

---

**⚠️ 著作権注意**: このシステムで生成されたコンテンツの商用利用時は、適切な著作権確認を行ってください。