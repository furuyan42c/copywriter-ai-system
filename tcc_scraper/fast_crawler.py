#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime
import os
import sys

class FastTCCCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.base_url = "https://www.tcc.gr.jp/copira/"
        self.all_urls = set()
        self.all_data = []
        self.processed = 0
        self.failed = 0
        
        # 即座に出力するための設定
        sys.stdout.flush()
        
        # 出力ディレクトリ
        os.makedirs("tcc_fast_data", exist_ok=True)
        
        print("🚀 Fast TCC Crawler Starting...")
        print(f"📅 Start time: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 50)
    
    def get_page(self, url, timeout=15):
        """高速ページ取得"""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except:
            return None
    
    def discover_pagination_urls(self):
        """ページネーションURLを発見"""
        print("🔍 Discovering pagination URLs...")
        
        # 基本URL
        base_params = "?copy=&copywriter=&ad=&biz=&media=&start=1960&end=2025&target_prize=all"
        
        # 最初のページで総件数を確認
        first_url = f"{self.base_url}{base_params}&limit=20"
        html = self.get_page(first_url)
        
        if not html:
            print("❌ Failed to get first page")
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 総件数を取得
        result_text = soup.get_text()
        total_match = re.search(r'(\d{1,3}(?:,\d{3})*)件が検索されました', result_text)
        if total_match:
            total_str = total_match.group(1).replace(',', '')
            total_items = int(total_str)
            print(f"📊 Total items found: {total_items:,}")
        else:
            total_items = 37259  # フォールバック
            print(f"📊 Using estimated total: {total_items:,}")
        
        # ページネーションリンクを探す
        urls = []
        
        # 複数の戦略でURLパターンを試す
        patterns = [
            lambda p: f"{self.base_url}{base_params}&page={p}&limit=20",
            lambda p: f"{self.base_url}page/{p}/{base_params}&limit=20",
            lambda p: f"{self.base_url}{base_params}&p={p}&limit=20"
        ]
        
        # 推定ページ数
        estimated_pages = (total_items + 19) // 20  # 20件ずつ、切り上げ
        print(f"📄 Estimated pages: {estimated_pages:,}")
        
        # 各パターンで最初の数ページをテスト
        working_pattern = None
        for i, pattern in enumerate(patterns):
            print(f"🔄 Testing pattern {i+1}...")
            test_url = pattern(2)  # 2ページ目をテスト
            if self.get_page(test_url):
                working_pattern = pattern
                print(f"✅ Pattern {i+1} works!")
                break
        
        if not working_pattern:
            print("❌ No working pagination pattern found")
            return []
        
        # 動作するパターンでURLを生成
        for page in range(1, min(estimated_pages + 1, 2000)):  # 安全上限
            urls.append(working_pattern(page))
        
        print(f"✅ Generated {len(urls):,} pagination URLs")
        return urls
    
    def extract_detail_urls_from_page(self, page_url):
        """ページから詳細URLを抽出"""
        html = self.get_page(page_url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        detail_urls = []
        
        # 詳細ページへのリンクを探す
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            if '/copira/id/' in href:
                if not href.startswith('http'):
                    href = f"https://www.tcc.gr.jp{href}"
                detail_urls.append(href)
        
        return detail_urls
    
    def collect_all_detail_urls(self):
        """全詳細URLを収集"""
        print("📥 Collecting all detail URLs...")
        
        # ページネーションURLを取得
        pagination_urls = self.discover_pagination_urls()
        
        if not pagination_urls:
            return []
        
        # 各ページから詳細URLを抽出
        batch_size = 10
        total_found = 0
        
        for i in range(0, len(pagination_urls), batch_size):
            batch = pagination_urls[i:i+batch_size]
            
            print(f"📄 Processing pages {i+1}-{min(i+batch_size, len(pagination_urls))}...", end=' ')
            
            batch_urls = set()
            for page_url in batch:
                detail_urls = self.extract_detail_urls_from_page(page_url)
                batch_urls.update(detail_urls)
                time.sleep(0.1)  # 軽いレート制限
            
            new_urls = batch_urls - self.all_urls
            self.all_urls.update(new_urls)
            total_found += len(new_urls)
            
            print(f"Found {len(new_urls)} new URLs (Total: {len(self.all_urls):,})")
            
            # 定期的に保存
            if i % 100 == 0 and self.all_urls:
                self.save_urls_checkpoint()
        
        print(f"✅ Total detail URLs collected: {len(self.all_urls):,}")
        return list(self.all_urls)
    
    def save_urls_checkpoint(self):
        """URLのチェックポイント保存"""
        urls_file = "tcc_fast_data/all_urls.json"
        with open(urls_file, 'w', encoding='utf-8') as f:
            json.dump(list(self.all_urls), f, ensure_ascii=False, indent=2)
        print(f"💾 URLs saved: {urls_file}")
    
    def parse_detail_page(self, url):
        """詳細ページを解析"""
        html = self.get_page(url)
        if not html:
            return {'error': 'fetch_failed', 'url': url}
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            data = {
                'url': url,
                'scraped_at': datetime.now().isoformat()
            }
            
            # ID抽出
            id_match = re.search(r'/id/(\d+)', url)
            if id_match:
                data['id'] = id_match.group(1)
            
            # タイトル
            title = soup.find('h1')
            if title:
                data['title'] = title.get_text(strip=True)
            
            # テーブルデータ抽出
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    th = row.find('th')
                    td = row.find('td')
                    if th and td:
                        key = th.get_text(strip=True).replace('：', '').replace(':', '')
                        value = td.get_text(strip=True)
                        
                        # キー正規化
                        key_map = {
                            '広告主': 'advertiser',
                            '受賞': 'award',
                            '業種': 'industry',
                            '媒体': 'media_type',
                            '掲載年度': 'publication_year',
                            '掲載ページ': 'page_number',
                            'コピーライター': 'copywriter',
                            '広告会社': 'agency',
                            '制作会社': 'production_company'
                        }
                        
                        normalized_key = key_map.get(key, key.lower().replace(' ', '_'))
                        if value:
                            data[normalized_key] = value
            
            # 年度を数値化
            if 'publication_year' in data:
                year_match = re.search(r'(\d{4})', data['publication_year'])
                if year_match:
                    data['year'] = int(year_match.group(1))
            
            return data
            
        except Exception as e:
            return {'error': str(e), 'url': url}
    
    def process_urls_fast(self, urls):
        """高速URL処理"""
        print(f"⚡ Fast processing {len(urls):,} URLs...")
        
        start_time = datetime.now()
        
        for i, url in enumerate(urls, 1):
            data = self.parse_detail_page(url)
            self.all_data.append(data)
            
            if 'error' not in data:
                self.processed += 1
            else:
                self.failed += 1
            
            # 進捗表示
            if i % 50 == 0:
                elapsed = datetime.now() - start_time
                rate = i / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0
                eta_seconds = (len(urls) - i) / rate if rate > 0 else 0
                eta_minutes = eta_seconds / 60
                
                success_rate = self.processed / i * 100
                print(f"📊 {i:,}/{len(urls):,} ({i/len(urls)*100:.1f}%) - "
                      f"Success: {success_rate:.1f}% - "
                      f"Speed: {rate:.1f}/s - "
                      f"ETA: {eta_minutes:.1f}min")
                
                # バッチ保存
                if i % 100 == 0:
                    self.save_batch(i)
            
            time.sleep(0.3)  # レート制限
        
        print(f"✅ Processing complete!")
        print(f"   Success: {self.processed:,}")
        print(f"   Failed: {self.failed:,}")
        print(f"   Total time: {datetime.now() - start_time}")
    
    def save_batch(self, count):
        """バッチ保存"""
        filename = f"tcc_fast_data/batch_{count:06d}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.all_data, f, ensure_ascii=False, indent=2)
        print(f"💾 Batch saved: {filename}")
    
    def save_final_complete_data(self):
        """最終完全データを保存"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # JSON
        json_file = f"tcc_fast_data/tcc_complete_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.all_data, f, ensure_ascii=False, indent=2)
        
        # CSV
        csv_file = f"tcc_fast_data/tcc_complete_{timestamp}.csv"
        self.save_as_csv(csv_file)
        
        # 統計
        stats_file = f"tcc_fast_data/tcc_stats_{timestamp}.txt"
        self.save_stats(stats_file)
        
        print(f"💾 Final data saved:")
        print(f"   📋 JSON: {json_file}")
        print(f"   📊 CSV: {csv_file}")
        print(f"   📈 Stats: {stats_file}")
        
        return json_file, csv_file, stats_file
    
    def save_as_csv(self, filename):
        """CSV保存"""
        import csv
        
        valid_data = [item for item in self.all_data if 'error' not in item]
        if not valid_data:
            return
        
        # フィールド収集
        all_fields = set()
        for item in valid_data:
            all_fields.update(item.keys())
        
        simple_fields = sorted([f for f in all_fields if f != 'copywriter_links'])
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=simple_fields)
            writer.writeheader()
            
            for item in valid_data:
                row = {}
                for field in simple_fields:
                    value = item.get(field, '')
                    if isinstance(value, (list, dict)):
                        value = str(value)
                    row[field] = str(value)[:500]
                writer.writerow(row)
    
    def save_stats(self, filename):
        """統計保存"""
        valid_data = [item for item in self.all_data if 'error' not in item]
        
        stats = []
        stats.append("TCC コピラ 高速クローリング結果")
        stats.append("=" * 50)
        stats.append(f"完了時刻: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        stats.append(f"総件数: {len(self.all_data):,}")
        stats.append(f"成功: {len(valid_data):,}")
        stats.append(f"失敗: {len(self.all_data) - len(valid_data):,}")
        stats.append(f"成功率: {len(valid_data)/len(self.all_data)*100:.1f}%" if self.all_data else "N/A")
        stats.append("")
        
        # 年度統計
        years = {}
        for item in valid_data:
            year = item.get('year', 'Unknown')
            years[year] = years.get(year, 0) + 1
        
        stats.append("年度別統計 (上位20):")
        for year, count in sorted(years.items(), key=lambda x: x[0] if isinstance(x[0], int) else 0, reverse=True)[:20]:
            stats.append(f"  {year}: {count:,}件")
        
        # 媒体統計
        media = {}
        for item in valid_data:
            media_type = item.get('media_type', 'Unknown')
            media[media_type] = media.get(media_type, 0) + 1
        
        stats.append("\n媒体別統計:")
        for media_type, count in sorted(media.items(), key=lambda x: x[1], reverse=True):
            stats.append(f"  {media_type}: {count:,}件")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(stats))
    
    def run_fast_crawl(self):
        """高速クローリング実行"""
        try:
            # ステップ1: URL収集
            urls = self.collect_all_detail_urls()
            
            if not urls:
                print("❌ No URLs collected!")
                return
            
            # ステップ2: データ処理
            self.process_urls_fast(urls)
            
            # ステップ3: 最終保存
            files = self.save_final_complete_data()
            
            print("\n🎉 Fast crawl completed successfully!")
            print(f"📊 Final stats: {self.processed:,} success, {self.failed:,} failed")
            
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user")
            if self.all_data:
                self.save_final_complete_data()
        except Exception as e:
            print(f"\n❌ Error: {e}")
            if self.all_data:
                self.save_final_complete_data()

if __name__ == "__main__":
    crawler = FastTCCCrawler()
    crawler.run_fast_crawl()