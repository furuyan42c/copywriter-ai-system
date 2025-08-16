#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from urllib3.exceptions import ReadTimeoutError
import socket

class UltimateTCCCrawler:
    def __init__(self):
        # セッション設定
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # タイムアウト設定
        self.session.timeout = (10, 15)  # (接続, 読み取り)
        
        # アダプター設定でリトライを追加
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.base_url = "https://www.tcc.gr.jp/copira/"
        self.all_urls = set()
        self.all_data = []
        self.processed = 0
        self.failed = 0
        self.lock = threading.Lock()
        
        # 出力ディレクトリ
        os.makedirs("tcc_ultimate_data", exist_ok=True)
        
        print("🚀 Ultimate TCC Crawler Starting...")
        print(f"📅 Start time: {datetime.now().strftime('%H:%M:%S')}")
        print("🛡️ Enhanced with timeout handling and retry mechanisms")
        print("🎯 Goal: Complete collection of all TCC data")
        print("=" * 60)
    
    def robust_get_page(self, url, max_retries=3):
        """超堅牢なページ取得"""
        for attempt in range(max_retries):
            try:
                # 短いタイムアウトで高速化
                response = self.session.get(url, timeout=(5, 10))
                response.raise_for_status()
                return response.text
            except (requests.exceptions.Timeout, ReadTimeoutError, socket.timeout) as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"⏰ Timeout {attempt+1}/{max_retries} for {url}, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"❌ Final timeout for {url}")
                    return None
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ Request error {attempt+1}/{max_retries} for {url}: {e}")
                    time.sleep(1)
                    continue
                else:
                    print(f"❌ Final error for {url}: {e}")
                    return None
            except Exception as e:
                print(f"❌ Unexpected error for {url}: {e}")
                return None
        
        return None
    
    def get_total_items_estimate(self):
        """総件数推定（タイムアウト対応）"""
        print("📊 Estimating total items...")
        
        # 複数のエンドポイントを試す
        test_urls = [
            f"{self.base_url}?copy=&copywriter=&ad=&biz=&media=&start=1960&end=2025&target_prize=all&limit=20",
            f"{self.base_url}?target_prize=all&limit=20",
            f"{self.base_url}?limit=20"
        ]
        
        for url in test_urls:
            html = self.robust_get_page(url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                text = soup.get_text()
                
                # 件数パターンを検索
                patterns = [
                    r'(\d{1,3}(?:,\d{3})*)件が検索されました',
                    r'(\d{1,3}(?:,\d{3})*)件の検索結果',
                    r'全(\d{1,3}(?:,\d{3})*)件'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text)
                    if match:
                        total_str = match.group(1).replace(',', '')
                        total = int(total_str)
                        print(f"📊 Found total: {total:,} items")
                        return total
                
                # HTMLから推定
                links = soup.find_all('a', href=lambda x: x and '/copira/id/' in x)
                if links:
                    print(f"📄 Found {len(links)} detail links on first page")
                    return 37259  # 既知の推定値を使用
        
        print("📊 Using conservative estimate: 37,259 items")
        return 37259
    
    def smart_year_search(self):
        """スマート年度検索"""
        print("📅 Starting smart year-by-year search...")
        
        all_urls = set()
        successful_years = 0
        
        # 最近の年から順番に検索（データが多い可能性が高い）
        years = list(range(2025, 1959, -1))
        
        for year in years:
            try:
                print(f"📅 Year {year}...", end=' ')
                
                year_urls = set()
                base_url = f"{self.base_url}?start={year}&end={year}&target_prize=all&limit=20"
                
                # その年の全ページを取得
                page = 1
                empty_pages = 0
                max_empty = 3
                
                while empty_pages < max_empty and page <= 100:  # 安全上限
                    page_url = f"{base_url}&page={page}"
                    html = self.robust_get_page(page_url)
                    
                    if html:
                        soup = BeautifulSoup(html, 'html.parser')
                        links = soup.find_all('a', href=lambda x: x and '/copira/id/' in x)
                        
                        page_found = 0
                        for link in links:
                            href = link.get('href', '')
                            if not href.startswith('http'):
                                href = f"https://www.tcc.gr.jp{href}"
                            year_urls.add(href)
                            page_found += 1
                        
                        if page_found > 0:
                            empty_pages = 0
                        else:
                            empty_pages += 1
                    else:
                        empty_pages += 1
                    
                    page += 1
                    time.sleep(0.2)  # レート制限
                
                all_urls.update(year_urls)
                if year_urls:
                    successful_years += 1
                print(f"{len(year_urls)} URLs (Total: {len(all_urls):,})")
                
                # 進捗保存
                if year % 5 == 0:
                    self.save_checkpoint(all_urls, f"year_{year}")
                
            except Exception as e:
                print(f"Error in year {year}: {e}")
                continue
        
        print(f"✅ Year search complete: {successful_years} years, {len(all_urls):,} URLs")
        return all_urls
    
    def smart_pagination_search(self):
        """スマートページネーション検索"""
        print("📄 Starting smart pagination search...")
        
        all_urls = set()
        base_url = f"{self.base_url}?copy=&copywriter=&ad=&biz=&media=&start=1960&end=2025&target_prize=all&limit=20"
        
        page = 1
        consecutive_failures = 0
        max_failures = 5
        
        while consecutive_failures < max_failures and page <= 2000:  # 安全上限
            try:
                print(f"📄 Page {page}...", end=' ')
                
                # 複数のURLパターンを試す
                url_patterns = [
                    f"{base_url}&page={page}",
                    f"{self.base_url}page/{page}/?copy=&copywriter=&ad=&biz=&media=&start=1960&end=2025&target_prize=all&limit=20"
                ]
                
                page_urls = set()
                for url_pattern in url_patterns:
                    html = self.robust_get_page(url_pattern)
                    if html:
                        soup = BeautifulSoup(html, 'html.parser')
                        links = soup.find_all('a', href=lambda x: x and '/copira/id/' in x)
                        
                        for link in links:
                            href = link.get('href', '')
                            if not href.startswith('http'):
                                href = f"https://www.tcc.gr.jp{href}"
                            page_urls.add(href)
                        
                        if page_urls:
                            break  # 成功したらパターンループを抜ける
                
                if page_urls:
                    all_urls.update(page_urls)
                    consecutive_failures = 0
                    print(f"{len(page_urls)} URLs (Total: {len(all_urls):,})")
                else:
                    consecutive_failures += 1
                    print("No URLs")
                
                # 定期保存
                if page % 50 == 0:
                    self.save_checkpoint(all_urls, f"page_{page}")
                
                page += 1
                time.sleep(0.3)
                
            except Exception as e:
                consecutive_failures += 1
                print(f"Error: {e}")
                continue
        
        print(f"✅ Pagination search complete: {len(all_urls):,} URLs")
        return all_urls
    
    def save_checkpoint(self, urls, suffix):
        """チェックポイント保存"""
        filename = f"tcc_ultimate_data/checkpoint_{suffix}_{datetime.now().strftime('%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(list(urls), f, ensure_ascii=False, indent=2)
        print(f"💾 Checkpoint: {filename}")
    
    def collect_all_urls(self):
        """全URL収集（複数戦略）"""
        print("🌐 Collecting all URLs with multiple strategies...")
        
        # 総件数推定
        estimated_total = self.get_total_items_estimate()
        
        # 戦略1: 年度別検索
        year_urls = self.smart_year_search()
        self.all_urls.update(year_urls)
        print(f"📅 After year search: {len(self.all_urls):,} URLs")
        
        # 戦略2: ページネーション検索
        pagination_urls = self.smart_pagination_search()
        new_pagination_urls = pagination_urls - self.all_urls
        self.all_urls.update(new_pagination_urls)
        print(f"📄 After pagination search: +{len(new_pagination_urls):,} new URLs (Total: {len(self.all_urls):,})")
        
        # 最終保存
        self.save_checkpoint(self.all_urls, "final_urls")
        
        coverage = len(self.all_urls) / estimated_total * 100 if estimated_total > 0 else 0
        print(f"🎯 URL collection complete: {len(self.all_urls):,} / {estimated_total:,} ({coverage:.1f}%)")
        
        return list(self.all_urls)
    
    def parse_detail_page_robust(self, url):
        """超堅牢な詳細ページ解析"""
        html = self.robust_get_page(url)
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
            title_selectors = ['h1', 'title', '.page-title', '.entry-title']
            for selector in title_selectors:
                title = soup.select_one(selector)
                if title:
                    title_text = title.get_text(strip=True)
                    if title_text and len(title_text) > 5:  # 有効なタイトル
                        data['title'] = title_text
                        break
            
            # テーブルデータ抽出（複数テーブル対応）
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['th', 'td'])
                    if len(cells) >= 2:
                        key_cell = cells[0]
                        value_cell = cells[1]
                        
                        key = key_cell.get_text(strip=True).replace('：', '').replace(':', '')
                        value = value_cell.get_text(strip=True)
                        
                        if key and value:
                            # キー正規化マッピング
                            key_map = {
                                '広告主': 'advertiser',
                                'クライアント': 'advertiser',
                                '受賞': 'award',
                                '業種': 'industry',
                                '媒体': 'media_type',
                                '掲載年度': 'publication_year',
                                '掲載ページ': 'page_number',
                                'コピーライター': 'copywriter',
                                '広告会社': 'agency',
                                '制作会社': 'production_company',
                                'ディレクター': 'director',
                                'プロデューサー': 'producer'
                            }
                            
                            normalized_key = key_map.get(key, key.lower().replace(' ', '_').replace('　', '_'))
                            data[normalized_key] = value
            
            # 年度を数値化
            year_fields = ['publication_year', 'year']
            for field in year_fields:
                if field in data:
                    year_match = re.search(r'(\d{4})', str(data[field]))
                    if year_match:
                        data['year'] = int(year_match.group(1))
                        break
            
            # コピーライターリンク
            cw_links = soup.find_all('a', href=lambda x: x and '/copitan/' in x)
            if cw_links:
                data['copywriter_links'] = []
                for link in cw_links:
                    cw_data = {
                        'name': link.get_text(strip=True),
                        'url': link.get('href', '')
                    }
                    id_match = re.search(r'/id/(\d+)', link.get('href', ''))
                    if id_match:
                        cw_data['id'] = id_match.group(1)
                    data['copywriter_links'].append(cw_data)
            
            return data
            
        except Exception as e:
            return {'error': f'parse_error: {str(e)}', 'url': url}
    
    def process_urls_ultimate(self, urls):
        """究極の並列URL処理"""
        print(f"⚡ Ultimate processing of {len(urls):,} URLs...")
        
        start_time = datetime.now()
        batch_size = 50
        
        # バッチ処理で進捗を細かく管理
        for i in range(0, len(urls), batch_size):
            batch_urls = urls[i:i+batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(urls) + batch_size - 1) // batch_size
            
            print(f"📦 Batch {batch_num}/{total_batches} ({len(batch_urls)} URLs)...")
            
            # 各バッチを並列処理
            with ThreadPoolExecutor(max_workers=2) as executor:  # 控えめな並列数
                future_to_url = {
                    executor.submit(self.parse_detail_page_robust, url): url 
                    for url in batch_urls
                }
                
                batch_results = []
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        result = future.result(timeout=30)
                        batch_results.append(result)
                        
                        with self.lock:
                            if 'error' not in result:
                                self.processed += 1
                            else:
                                self.failed += 1
                    
                    except Exception as e:
                        with self.lock:
                            self.failed += 1
                        batch_results.append({'error': f'future_error: {str(e)}', 'url': url})
                
                # バッチ結果を追加
                self.all_data.extend(batch_results)
            
            # バッチごとの進捗表示
            total_processed = len(self.all_data)
            elapsed = datetime.now() - start_time
            rate = total_processed / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0
            eta_seconds = (len(urls) - total_processed) / rate if rate > 0 else 0
            eta_minutes = eta_seconds / 60
            
            success_rate = self.processed / total_processed * 100 if total_processed > 0 else 0
            
            print(f"📊 Progress: {total_processed:,}/{len(urls):,} ({total_processed/len(urls)*100:.1f}%)")
            print(f"   Success: {success_rate:.1f}% | Speed: {rate:.1f}/s | ETA: {eta_minutes:.1f}min")
            
            # 定期保存
            if batch_num % 10 == 0:
                self.save_batch_data(batch_num)
            
            # レート制限
            time.sleep(1)
        
        print(f"✅ Ultimate processing complete!")
        print(f"   Total: {len(self.all_data):,} | Success: {self.processed:,} | Failed: {self.failed:,}")
        print(f"   Duration: {datetime.now() - start_time}")
    
    def save_batch_data(self, batch_num):
        """バッチデータ保存"""
        filename = f"tcc_ultimate_data/batch_{batch_num:04d}_{datetime.now().strftime('%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.all_data, f, ensure_ascii=False, indent=2)
        print(f"💾 Batch saved: {filename}")
    
    def save_ultimate_data(self):
        """究極データ保存"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 完全JSON
        json_file = f"tcc_ultimate_data/tcc_ultimate_complete_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.all_data, f, ensure_ascii=False, indent=2)
        
        # 成功データのみのJSON
        valid_data = [item for item in self.all_data if 'error' not in item]
        valid_json_file = f"tcc_ultimate_data/tcc_ultimate_valid_{timestamp}.json"
        with open(valid_json_file, 'w', encoding='utf-8') as f:
            json.dump(valid_data, f, ensure_ascii=False, indent=2)
        
        # CSV
        csv_file = f"tcc_ultimate_data/tcc_ultimate_{timestamp}.csv"
        self.save_as_csv(csv_file, valid_data)
        
        # 詳細統計
        stats_file = f"tcc_ultimate_data/tcc_ultimate_stats_{timestamp}.txt"
        self.save_ultimate_stats(stats_file, valid_data)
        
        print(f"💾 Ultimate data saved:")
        print(f"   📋 Complete JSON: {json_file}")
        print(f"   ✅ Valid JSON: {valid_json_file}")
        print(f"   📊 CSV: {csv_file}")
        print(f"   📈 Stats: {stats_file}")
        
        return json_file, valid_json_file, csv_file, stats_file
    
    def save_as_csv(self, filename, data):
        """CSV保存"""
        import csv
        
        if not data:
            return
        
        # フィールド収集
        all_fields = set()
        for item in data:
            all_fields.update(item.keys())
        
        # 複雑なフィールドを除外してソート
        simple_fields = sorted([f for f in all_fields if f not in ['copywriter_links']])
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=simple_fields)
            writer.writeheader()
            
            for item in data:
                row = {}
                for field in simple_fields:
                    value = item.get(field, '')
                    if isinstance(value, (list, dict)):
                        value = str(value)
                    row[field] = str(value)[:1000]  # 長さ制限
                writer.writerow(row)
    
    def save_ultimate_stats(self, filename, data):
        """究極統計保存"""
        total_data = len(self.all_data)
        valid_data = len(data)
        
        stats = []
        stats.append("TCC コピラ 究極クローリング結果")
        stats.append("=" * 60)
        stats.append(f"完了時刻: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        stats.append(f"総件数: {total_data:,}")
        stats.append(f"有効件数: {valid_data:,}")
        stats.append(f"エラー件数: {total_data - valid_data:,}")
        stats.append(f"成功率: {valid_data/total_data*100:.1f}%" if total_data > 0 else "N/A")
        stats.append(f"目標達成率: {valid_data/37259*100:.1f}%")
        stats.append("")
        
        if data:
            # 年度統計
            years = {}
            for item in data:
                year = item.get('year', item.get('publication_year', 'Unknown'))
                years[year] = years.get(year, 0) + 1
            
            stats.append("📅 年度別統計 (上位30):")
            year_items = sorted(years.items(), key=lambda x: x[0] if isinstance(x[0], int) else 0, reverse=True)
            for year, count in year_items[:30]:
                stats.append(f"  {year}: {count:,}件")
            
            # 媒体統計
            media_types = {}
            for item in data:
                media = item.get('media_type', 'Unknown')
                media_types[media] = media_types.get(media, 0) + 1
            
            stats.append("\n📺 媒体別統計:")
            for media, count in sorted(media_types.items(), key=lambda x: x[1], reverse=True):
                stats.append(f"  {media}: {count:,}件")
            
            # 受賞統計
            awards = {}
            for item in data:
                award = item.get('award', 'なし')
                awards[award] = awards.get(award, 0) + 1
            
            stats.append("\n🏆 受賞統計 (上位20):")
            for award, count in sorted(awards.items(), key=lambda x: x[1], reverse=True)[:20]:
                stats.append(f"  {award}: {count:,}件")
            
            # 広告主統計
            advertisers = {}
            for item in data:
                advertiser = item.get('advertiser', 'Unknown')
                advertisers[advertiser] = advertisers.get(advertiser, 0) + 1
            
            stats.append("\n🏢 広告主統計 (上位20):")
            for advertiser, count in sorted(advertisers.items(), key=lambda x: x[1], reverse=True)[:20]:
                if advertiser != 'Unknown':
                    stats.append(f"  {advertiser}: {count:,}件")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(stats))
    
    def run_ultimate_crawl(self):
        """究極クローリング実行"""
        try:
            print("🎯 Starting ultimate comprehensive crawl...")
            
            # ステップ1: 全URL収集
            urls = self.collect_all_urls()
            
            if not urls:
                print("❌ No URLs collected!")
                return
            
            print(f"\n⚡ Starting data extraction for {len(urls):,} URLs...")
            
            # ステップ2: データ処理
            self.process_urls_ultimate(urls)
            
            # ステップ3: 最終保存
            files = self.save_ultimate_data()
            
            print("\n🎉 ULTIMATE CRAWL COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print(f"📊 Final Results:")
            print(f"   Total URLs processed: {len(self.all_data):,}")
            print(f"   Successful extractions: {self.processed:,}")
            print(f"   Failed extractions: {self.failed:,}")
            print(f"   Success rate: {self.processed/len(self.all_data)*100:.1f}%")
            print(f"   Target coverage: {self.processed/37259*100:.1f}%")
            print("=" * 60)
            
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user - saving current progress...")
            if self.all_data:
                self.save_ultimate_data()
        except Exception as e:
            print(f"\n❌ Ultimate error: {e}")
            if self.all_data:
                self.save_ultimate_data()

if __name__ == "__main__":
    print("🚀 Starting TCC Ultimate Crawler...")
    print("⚡ This is the most comprehensive and robust version")
    print("🛡️ Enhanced with timeout handling, retry mechanisms, and error recovery")
    print("")
    
    crawler = UltimateTCCCrawler()
    crawler.run_ultimate_crawl()