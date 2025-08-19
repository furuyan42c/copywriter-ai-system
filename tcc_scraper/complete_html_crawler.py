#!/usr/bin/env python3
"""
TCC 完全HTML保存付きクローラー - 最終版
全37,244件のHTMLデータ保存 + 完全構造解析を実行
"""
import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime
import os
import sys
import gzip
import csv

class CompleteHTMLCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
            'Connection': 'keep-alive'
        })
        
        self.processed = 0
        self.failed = 0
        self.saved_html = 0
        self.copy_extracted = 0
        
        # 出力ディレクトリ
        os.makedirs('complete_html_data', exist_ok=True)
        os.makedirs('complete_parsed_data', exist_ok=True)
        
    def log(self, message):
        """ログ出力（即座に表示）"""
        print(message)
        sys.stdout.flush()
        
    def get_and_save_html(self, url, timeout=10):
        """HTMLを取得して保存"""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            html_content = response.text
            
            # URLからIDを抽出
            id_match = re.search(r'/copira/id/(\d+)', url)
            if id_match:
                tcc_id = id_match.group(1)
                
                # HTMLファイルを圧縮保存
                html_file = f"complete_html_data/tcc_{tcc_id}.html.gz"
                with gzip.open(html_file, 'wt', encoding='utf-8') as f:
                    f.write(html_content)
                
                self.saved_html += 1
                return html_content
            
            return html_content
            
        except Exception as e:
            self.log(f"❌ Error fetching {url}: {e}")
            return None
    
    def extract_comprehensive_data(self, url, html):
        """包括的データ抽出（完全版）"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            data = {'url': url}
            
            # TCC IDを抽出
            id_match = re.search(r'/copira/id/(\d+)', url)
            if id_match:
                data['tcc_id'] = int(id_match.group(1))
            
            # タイトル
            title_elem = soup.find('h1')
            if title_elem:
                data['title'] = title_elem.get_text(strip=True)
            
            # メインコピーテキスト（block5-1__catch）
            catch_elem = soup.find('p', class_='block5-1__catch')
            if catch_elem:
                # テキスト部分とspan部分を分離して結合
                copy_parts = []
                
                # メインテキスト（spanを除く）
                main_text = catch_elem.get_text(strip=True)
                span_elem = catch_elem.find('span')
                if span_elem:
                    span_text = span_elem.get_text(strip=True)
                    main_text = main_text.replace(span_text, '').strip()
                
                if main_text:
                    copy_parts.append(main_text)
                
                # spanの詳細テキスト
                if span_elem:
                    # brタグを改行に変換
                    for br in span_elem.find_all('br'):
                        br.replace_with('\n')
                    span_text = span_elem.get_text(strip=True)
                    if span_text:
                        copy_parts.append(span_text)
                
                # コピーテキストを結合
                if copy_parts:
                    data['copy_text'] = '\n'.join(copy_parts)
                    self.copy_extracted += 1
            
            # サブタイトル（block5-1__notes）
            notes_elem = soup.find('p', class_='block5-1__notes')
            if notes_elem:
                notes_text = notes_elem.get_text(strip=True)
                if notes_text:
                    data['subtitle'] = notes_text
            
            # テーブルデータを抽出
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        
                        # フィールド名の正規化とマッピング
                        key_mappings = {
                            '広告主': 'advertiser',
                            'クライアント': 'advertiser', 
                            'Client': 'advertiser',
                            'コピーライター': 'copywriter',
                            'Copywriter': 'copywriter',
                            '年度': 'year',
                            '年': 'year',
                            'Year': 'year',
                            '媒体': 'media_type',
                            'Media': 'media_type',
                            '受賞': 'award',
                            '賞': 'award',
                            'Award': 'award',
                            '業種': 'industry',
                            'Industry': 'industry',
                            '広告会社': 'agency',
                            'Agency': 'agency',
                            'ディレクター': 'director',
                            'Director': 'director',
                            'プロデューサー': 'producer',
                            'Producer': 'producer',
                            'プランナー': 'planner',
                            'Planner': 'planner',
                            '掲載ページ': 'page_number',
                            'ページ': 'page_number'
                        }
                        
                        mapped_key = None
                        for k, v in key_mappings.items():
                            if k in key:
                                mapped_key = v
                                break
                        
                        if mapped_key:
                            if mapped_key == 'year':
                                year_match = re.search(r'(\d{4})', value)
                                if year_match:
                                    data[mapped_key] = int(year_match.group(1))
                            elif mapped_key == 'page_number':
                                page_match = re.search(r'(\d+)', value)
                                if page_match:
                                    data[mapped_key] = int(page_match.group(1))
                            else:
                                data[mapped_key] = value
            
            # NO.番号を抽出
            no_elem = soup.find('p', class_='table1__text')
            if no_elem:
                no_text = no_elem.get_text(strip=True)
                no_match = re.search(r'NO\.(\d+)', no_text)
                if no_match:
                    data['no_number'] = int(no_match.group(1))
            
            # 処理日時を記録
            data['processed_at'] = datetime.now().isoformat()
            
            return data
            
        except Exception as e:
            return {'error': f'Parse error: {str(e)}', 'url': url, 'processed_at': datetime.now().isoformat()}
    
    def process_all_urls_with_html_saving(self, urls):
        """全URLのHTML保存付きデータ処理"""
        total_urls = len(urls)
        start_time = datetime.now()
        all_data = []
        
        self.log(f"🚀 完全HTML保存付きデータ処理開始")
        self.log(f"📊 対象URL数: {total_urls:,}")
        self.log(f"💾 HTML保存先: complete_html_data/")
        self.log(f"📋 データ保存先: complete_parsed_data/")
        self.log("")
        
        for i, url in enumerate(urls):
            # HTMLを取得・保存
            html = self.get_and_save_html(url)
            
            if html:
                # データを抽出
                result = self.extract_comprehensive_data(url, html)
                all_data.append(result)
                
                if 'error' not in result:
                    self.processed += 1
                else:
                    self.failed += 1
            else:
                self.failed += 1
                all_data.append({
                    'error': 'HTML取得失敗', 
                    'url': url, 
                    'processed_at': datetime.now().isoformat()
                })
            
            # 進捗表示（100件ごと）
            if (i + 1) % 100 == 0:
                elapsed = datetime.now() - start_time
                rate = (i + 1) / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0
                eta_seconds = (total_urls - (i + 1)) / rate if rate > 0 else 0
                eta_hours = eta_seconds / 3600
                
                progress_pct = (i + 1) / total_urls * 100
                success_rate = self.processed / (i + 1) * 100
                copy_rate = self.copy_extracted / self.processed * 100 if self.processed > 0 else 0
                
                self.log(f"📊 進捗: {i+1:,}/{total_urls:,} ({progress_pct:.1f}%)")
                self.log(f"   成功: {self.processed:,} | 失敗: {self.failed:,} | 成功率: {success_rate:.1f}%")
                self.log(f"   HTML保存: {self.saved_html:,}件")
                self.log(f"   コピー抽出: {self.copy_extracted:,}件 ({copy_rate:.1f}%)")
                self.log(f"   速度: {rate:.1f}件/秒 | 推定残り時間: {eta_hours:.1f}時間")
                self.log("")
                
                # 中間保存（1000件ごと）
                if (i + 1) % 1000 == 0:
                    self.save_interim_data(all_data, i + 1)
            
            # レート制限（サーバー負荷軽減）
            time.sleep(0.3)
        
        self.log(f"✅ 処理完了: {len(all_data):,}件")
        return all_data
    
    def save_interim_data(self, data, count):
        """中間データ保存"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"complete_parsed_data/tcc_complete_interim_{count:06d}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        valid_count = len([item for item in data if 'error' not in item])
        self.log(f"💾 中間保存: {filename} ({valid_count:,}件の有効データ)")
    
    def save_final_data(self, data):
        """最終データ保存"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 有効データのみフィルタ
        valid_data = [item for item in data if 'error' not in item]
        error_data = [item for item in data if 'error' in item]
        
        self.log("💾 最終データ保存中...")
        
        # 完全JSONファイル保存
        json_file = f"complete_parsed_data/tcc_complete_with_html_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(valid_data, f, ensure_ascii=False, indent=2)
        
        # CSVファイル保存
        csv_file = f"complete_parsed_data/tcc_complete_with_html_{timestamp}.csv"
        if valid_data:
            all_fields = set()
            for item in valid_data:
                all_fields.update(item.keys())
            
            fields = sorted(all_fields)
            
            with open(csv_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fields)
                writer.writeheader()
                for item in valid_data:
                    row = {}
                    for field in fields:
                        value = item.get(field, '')
                        # 長すぎるテキストは切り詰め
                        row[field] = str(value)[:3000] if isinstance(value, str) else str(value)
                    writer.writerow(row)
        
        # エラーログ保存
        error_file = f"complete_parsed_data/tcc_complete_errors_{timestamp}.json"
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=2)
        
        # 統計ファイル保存
        stats_file = f"complete_parsed_data/tcc_complete_final_stats_{timestamp}.txt"
        self.save_comprehensive_stats(stats_file, valid_data)
        
        self.log("💾 最終保存完了:")
        self.log(f"   📋 完全JSON: {json_file}")
        self.log(f"   📊 CSV: {csv_file}")
        self.log(f"   ❌ エラーログ: {error_file}")
        self.log(f"   📈 統計: {stats_file}")
        
        return json_file, csv_file, stats_file

if __name__ == "__main__":
    print("🚀 TCC 完全HTML保存付きクローラー - 最終版")
    print("💾 全HTMLデータ保存 + 完全構造解析")
    print("🎯 目標: 37,244件完全処理")
    print("")
    
    crawler = CompleteHTMLCrawler()
    # 使用例: crawler.run_complete_html_crawl(data_file)