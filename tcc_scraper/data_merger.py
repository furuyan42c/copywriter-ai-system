#!/usr/bin/env python3
"""
TCC データ統合器 - 最終版
元の完全データと詳細分類データを統合
"""
import json
import csv
from datetime import datetime
import sys
from collections import defaultdict

class DataMerger:
    def __init__(self):
        self.merged_data = []
        self.stats = defaultdict(int)
        
    def log(self, message):
        """ログ出力（即座に表示）"""
        print(message)
        sys.stdout.flush()
    
    def load_original_data(self, original_file):
        """元の完全データを読み込み"""
        self.log(f"📂 元データ読み込み: {original_file}")
        
        with open(original_file, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
        
        self.log(f"   読み込み完了: {len(original_data):,}件")
        return original_data
    
    def load_classified_data(self, classified_file):
        """詳細分類データを読み込み"""
        self.log(f"📂 分類データ読み込み: {classified_file}")
        
        with open(classified_file, 'r', encoding='utf-8') as f:
            classified_data = json.load(f)
        
        self.log(f"   読み込み完了: {len(classified_data):,}件")
        return classified_data
    
    def create_tcc_id_mapping(self, classified_data):
        """TCC IDによるマッピング辞書を作成"""
        self.log("🔗 TCC IDマッピング作成中...")
        
        mapping = {}
        for item in classified_data:
            tcc_id = item.get('tcc_id')
            if tcc_id:
                mapping[tcc_id] = item
        
        self.log(f"   マッピング完了: {len(mapping):,}件")
        return mapping
    
    def merge_data(self, original_data, classified_mapping):
        """データを統合"""
        self.log("🔄 データ統合開始...")
        
        merged_count = 0
        unmatched_count = 0
        
        for original_item in original_data:
            # 元データから基本情報を取得
            merged_item = original_item.copy()
            
            # URLからTCC IDを抽出
            url = original_item.get('url', '')
            tcc_id = None
            
            if '/copira/id/' in url:
                try:
                    tcc_id = int(url.split('/copira/id/')[1].split('/')[0])
                except (ValueError, IndexError):
                    pass
            
            # 分類データとマッチング
            if tcc_id and tcc_id in classified_mapping:
                classified_item = classified_mapping[tcc_id]
                
                # 詳細分類フィールドを追加
                merged_item.update({
                    'main_headline': classified_item.get('main_headline'),
                    'sub_headline': classified_item.get('sub_headline'),
                    'body_copy': classified_item.get('body_copy'),
                    'dialogue': classified_item.get('dialogue'),
                    'tagline': classified_item.get('tagline'),
                    'product_info_classified': classified_item.get('product_info'),
                    'notes_classified': classified_item.get('notes'),
                    'raw_copy_text_classified': classified_item.get('raw_copy_text')
                })
                
                merged_count += 1
                
                # 統計更新
                for field in ['main_headline', 'sub_headline', 'body_copy', 'dialogue', 'tagline', 'product_info', 'notes']:
                    if classified_item.get(field):
                        self.stats[field] += 1
                        
            else:
                unmatched_count += 1
                # 分類データがない場合は空のフィールドを追加
                merged_item.update({
                    'main_headline': None,
                    'sub_headline': None,
                    'body_copy': None,
                    'dialogue': None,
                    'tagline': None,
                    'product_info_classified': None,
                    'notes_classified': None,
                    'raw_copy_text_classified': None
                })
            
            self.merged_data.append(merged_item)
        
        self.log(f"✅ 統合完了:")
        self.log(f"   総データ数: {len(self.merged_data):,}件")
        self.log(f"   分類済み: {merged_count:,}件")
        self.log(f"   未分類: {unmatched_count:,}件")
        
        return self.merged_data
    
    def save_merged_data(self, merged_data):
        """統合データを保存"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        self.log("💾 統合データ保存中...")
        
        # JSONファイル保存
        json_file = f"tcc_complete_merged_dataset_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
        # CSVファイル保存
        csv_file = f"tcc_complete_merged_dataset_{timestamp}.csv"
        if merged_data:
            # 全フィールドを収集
            all_fields = set()
            for item in merged_data:
                all_fields.update(item.keys())
            
            fieldnames = sorted(all_fields)
            
            with open(csv_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for item in merged_data:
                    row = {}
                    for field in fieldnames:
                        value = item.get(field, '')
                        # 長すぎるテキストは制限
                        if isinstance(value, str) and len(value) > 8000:
                            value = value[:8000] + '...'
                        row[field] = value
                    writer.writerow(row)
        
        self.log(f"💾 保存完了:")
        self.log(f"   📊 JSON: {json_file}")
        self.log(f"   📋 CSV: {csv_file}")
        
        return json_file, csv_file
    
    def run_merge(self, original_file, classified_file):
        """統合処理を実行"""
        try:
            self.log("🚀 TCC データ統合開始")
            self.log("=" * 60)
            self.log("目標: 元の完全データ + 詳細分類データの統合")
            self.log("=" * 60)
            
            # データ読み込み
            original_data = self.load_original_data(original_file)
            classified_data = self.load_classified_data(classified_file)
            
            # マッピング作成
            classified_mapping = self.create_tcc_id_mapping(classified_data)
            
            # データ統合
            merged_data = self.merge_data(original_data, classified_mapping)
            
            # 結果保存
            files = self.save_merged_data(merged_data)
            
            # 統計表示
            self.log(f"\n📊 最終統合結果:")
            total = len(merged_data)
            for classification, count in sorted(self.stats.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total * 100) if total > 0 else 0
                self.log(f"   {classification:15s}: {count:6,d}件 ({percentage:5.1f}%)")
            
            self.log(f"\n🎉 統合完了: {len(merged_data):,}件の統合データを生成しました")
            self.log("=" * 60)
            
        except Exception as e:
            self.log(f"\n❌ エラー発生: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("🔄 TCC データ統合ツール")
    print("📂 元データと詳細分類データを統合します")
    print("")
    
    merger = DataMerger()
    # 使用例: merger.run_merge(original_file, classified_file)