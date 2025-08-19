#!/usr/bin/env python3
"""
TCC コピーテキスト詳細分類器 - 最終版
コピーテキストを7つのカテゴリに詳細分類
"""
import gzip
import json
import os
import re
from bs4 import BeautifulSoup, NavigableString, Tag
from collections import defaultdict
from datetime import datetime
import csv

class CopyTextDetailedClassifier:
    def __init__(self):
        self.html_dir = "complete_html_data"
        
    def extract_and_classify_copy(self, html_content, tcc_id):
        """HTMLからコピー要素を抽出・詳細分類"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        result = {
            'tcc_id': int(tcc_id),
            'main_headline': None,      # メインキャッチフレーズ
            'sub_headline': None,       # サブキャッチフレーズ
            'body_copy': None,          # ボディコピー
            'dialogue': None,           # 会話・ナレーション
            'tagline': None,           # タグライン・クロージング
            'product_info': None,      # 商品・企業情報
            'notes': None,             # 注釈・備考
            'raw_copy_text': None,     # 全体のコピーテキスト
        }
        
        # メインキャッチコピー要素を分析
        catch_elem = soup.find('p', class_='block5-1__catch')
        if catch_elem:
            copy_analysis = self.analyze_catch_structure(catch_elem)
            result.update(copy_analysis)
        
        # ノート要素
        notes_elem = soup.find('p', class_='block5-1__notes')
        if notes_elem:
            notes_text = notes_elem.get_text(strip=True)
            if notes_text:
                result['notes'] = notes_text
        
        # タイトル（商品情報として）
        title_elem = soup.find('h1')
        if title_elem:
            title_text = title_elem.get_text(strip=True)
            if title_text:
                result['product_info'] = title_text
        
        return result
    
    def analyze_catch_structure(self, catch_elem):
        """キャッチコピー要素の詳細構造分析"""
        # 全テキストを取得
        full_text = catch_elem.get_text(strip=True)
        
        # 直接テキストとspan内テキストを分離
        direct_texts = []
        span_texts = []
        
        for content in catch_elem.contents:
            if isinstance(content, NavigableString):
                text = str(content).strip()
                if text:
                    direct_texts.append(text)
            elif isinstance(content, Tag):
                if content.name == 'span':
                    # span内のテキストを抽出
                    span_content = self.extract_span_content(content)
                    span_texts.extend(span_content)
                elif content.name == 'br':
                    # 改行は無視
                    continue
        
        # 直接テキストを結合
        main_text = ' '.join(direct_texts) if direct_texts else None
        
        # span内テキストを結合
        dialogue_text = '\n'.join(span_texts) if span_texts else None
        
        # 分類結果
        result = {
            'raw_copy_text': full_text,
        }
        
        # 分類に基づいてフィールドに配置
        if main_text:
            classification = self.classify_text_type(main_text)
            if classification == 'main_headline':
                result['main_headline'] = main_text
            elif classification == 'sub_headline':
                result['sub_headline'] = main_text
            elif classification == 'tagline':
                result['tagline'] = main_text
            elif classification == 'product_info':
                if not result.get('product_info'):  # 既存のタイトルを上書きしない
                    result['product_info'] = main_text
            else:
                result['body_copy'] = main_text
        
        if dialogue_text:
            classification = self.classify_text_type(dialogue_text)
            if classification == 'dialogue':
                result['dialogue'] = dialogue_text
            elif classification == 'body_copy':
                result['body_copy'] = dialogue_text
            else:
                # dialogueとして保存
                result['dialogue'] = dialogue_text
        
        return result
    
    def extract_span_content(self, span_elem):
        """span要素からテキスト行を抽出"""
        lines = []
        current_line = ""
        
        for content in span_elem.contents:
            if isinstance(content, NavigableString):
                current_line += str(content)
            elif isinstance(content, Tag) and content.name == 'br':
                if current_line.strip():
                    lines.append(current_line.strip())
                current_line = ""
        
        # 最後の行を追加
        if current_line.strip():
            lines.append(current_line.strip())
        
        return lines
    
    def classify_text_type(self, text):
        """テキストタイプを分類"""
        if not text:
            return 'unknown'
        
        text_clean = text.strip()
        
        # 会話・ナレーション（対話形式）
        if re.search(r'[：:]\s*[「『"]|いとし|こいし|ナレーション|N:|S:|M:|NA|塙|桃太郎|浦島太郎|一寸法師|金太郎|かぐや姫', text_clean):
            return 'dialogue'
        
        # 商品名・ブランド情報（会社名、商品名パターン）
        if re.search(r'株式会社|会社|製薬|産業|電器|自動車|ビール|食品|コカ・コーラ|除虫菊|マクドナルド', text_clean):
            return 'product_info'
        
        # タグライン（短くてキャッチー、ブランドメッセージ）
        if len(text_clean) < 50 and (
            re.search(r'には|だけ|です|である|だ$|しよう|しましょう|好きです|あります|してる間は', text_clean) or
            not re.search(r'[。、]', text_clean)
        ):
            return 'tagline'
        
        # メインヘッドライン（中程度の長さ、商品名含む）
        if 10 <= len(text_clean) <= 100:
            return 'main_headline'
        
        # サブヘッドライン（やや長め）
        if 100 < len(text_clean) <= 200:
            return 'sub_headline'
        
        # ボディコピー（長文）
        if len(text_clean) > 200:
            return 'body_copy'
        
        # 短すぎる場合はその他
        return 'main_headline'
    
    def process_sample_files(self, num_samples=100):
        """サンプルファイルを処理"""
        html_files = [f for f in os.listdir(self.html_dir) if f.endswith('.html.gz')][:num_samples]
        
        results = []
        classification_stats = defaultdict(int)
        
        print(f"🔍 {len(html_files)}件のHTMLファイルを分析中...")
        
        for i, html_file in enumerate(html_files):
            tcc_id = html_file.replace('tcc_', '').replace('.html.gz', '')
            file_path = os.path.join(self.html_dir, html_file)
            
            try:
                with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                    html_content = f.read()
                
                result = self.extract_and_classify_copy(html_content, tcc_id)
                results.append(result)
                
                # 統計更新
                for field in ['main_headline', 'sub_headline', 'body_copy', 'dialogue', 'tagline', 'product_info', 'notes']:
                    if result.get(field):
                        classification_stats[field] += 1
                
                if (i + 1) % 20 == 0:
                    print(f"   進捗: {i+1}/{len(html_files)}")
                
            except Exception as e:
                print(f"❌ ID {tcc_id}: エラー - {e}")
        
        return results, classification_stats
    
    def save_enhanced_dataset(self, results, stats):
        """改良されたデータセットを保存"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 分類済みデータセット
        dataset_file = f"tcc_classified_copy_dataset_{timestamp}.json"
        with open(dataset_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # CSV形式も生成
        csv_file = f"tcc_classified_copy_dataset_{timestamp}.csv"
        
        if results:
            fieldnames = ['tcc_id', 'main_headline', 'sub_headline', 'body_copy', 'dialogue', 
                         'tagline', 'product_info', 'notes', 'raw_copy_text']
            
            with open(csv_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for result in results:
                    row = {}
                    for field in fieldnames:
                        value = result.get(field, '')
                        # 長すぎるテキストは制限
                        if isinstance(value, str) and len(value) > 5000:
                            value = value[:5000] + '...'
                        row[field] = value
                    writer.writerow(row)
        
        print(f"\n💾 結果を保存しました:")
        print(f"   📊 JSON: {dataset_file}")
        print(f"   📋 CSV: {csv_file}")
        
        return dataset_file, csv_file
    
    def run_classification(self):
        """分類処理を実行"""
        print("🎯 TCC コピーテキスト詳細分類開始")
        print("=" * 60)
        print("分類カテゴリ:")
        print("  📢 main_headline    : メインキャッチフレーズ")
        print("  📝 sub_headline     : サブキャッチフレーズ") 
        print("  📖 body_copy        : ボディコピー")
        print("  💬 dialogue         : 会話・ナレーション")
        print("  🏷️  tagline          : タグライン・クロージング")
        print("  📦 product_info     : 商品・企業情報")
        print("  📄 notes            : 注釈・備考")
        print("=" * 60)
        
        # サンプル処理
        results, stats = self.process_sample_files(200)
        
        # 結果保存
        files = self.save_enhanced_dataset(results, stats)
        
        # 統計表示
        print(f"\n📊 分類結果:")
        total = len(results)
        for classification, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            print(f"   {classification:15s}: {count:4d}件 ({percentage:5.1f}%)")
        
        print(f"\n✅ 完了: {len(results)}件のデータを詳細分類しました")
        
        return results, stats

if __name__ == "__main__":
    classifier = CopyTextDetailedClassifier()
    classifier.run_classification()