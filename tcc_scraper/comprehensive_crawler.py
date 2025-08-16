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

class ComprehensiveTCCCrawler:
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
        self.lock = threading.Lock()
        
        # 出力ディレクトリ
        os.makedirs("tcc_comprehensive_data", exist_ok=True)
        
        print("🚀 Comprehensive TCC Crawler Starting...")
        print(f"📅 Start time: {datetime.now().strftime('%H:%M:%S')}")
        print("🎯 Goal: Complete collection of all 37,259+ items")
        print("=" * 60)
    
    def get_page(self, url, timeout=20):
        """堅牢なページ取得"""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"⚠️ Error fetching {url}: {e}")
            return None
    
    def investigate_search_structure(self):
        """検索構造を詳細調査"""
        print("🔍 Investigating search structure...")
        
        # 1. デフォルト検索での総件数を確認
        default_url = f"{self.base_url}?copy=&copywriter=&ad=&biz=&media=&start=1960&end=2025&target_prize=all"
        html = self.get_page(default_url)
        
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 総件数を探す
            page_text = soup.get_text()
            
            # 複数のパターンで総件数を検索
            patterns = [
                r'(\d{1,3}(?:,\d{3})*)件が検索されました',
                r'(\d{1,3}(?:,\d{3})*)件の検索結果',
                r'全(\d{1,3}(?:,\d{3})*)件',
                r'(\d{1,3}(?:,\d{3})*)作品'
            ]
            
            total_items = None
            for pattern in patterns:
                match = re.search(pattern, page_text)
                if match:
                    total_str = match.group(1).replace(',', '')
                    total_items = int(total_str)
                    print(f"📊 Found total items: {total_items:,} (pattern: {pattern})")
                    break
            
            if not total_items:
                print("⚠️ Could not find total item count in text")
                # HTMLから件数を推定
                print("🔍 Analyzing page structure for estimation...")
                
                # ページ内のリンクから推定
                detail_links = soup.find_all('a', href=lambda x: x and '/copira/id/' in x)
                print(f"📄 Detail links on this page: {len(detail_links)}")
                
                # ページネーションから推定
                pagination_links = soup.find_all('a', href=True)
                page_numbers = []
                for link in pagination_links:
                    text = link.get_text(strip=True)
                    if text.isdigit():
                        page_numbers.append(int(text))
                
                if page_numbers:
                    max_page = max(page_numbers)
                    estimated_total = max_page * len(detail_links) if detail_links else max_page * 20
                    print(f"📄 Max page found: {max_page}, Estimated total: {estimated_total:,}")
                    total_items = estimated_total
                else:
                    print("⚠️ No pagination found, using conservative estimate")
                    total_items = 40000  # 保守的な推定
        
        return total_items or 37259  # フォールバック値
    
    def strategy_year_by_year_search(self):
        """年度別検索戦略"""
        print("🗓️ Starting year-by-year comprehensive search...")
        all_urls = set()
        
        # 1960年から2025年まで各年度を検索
        for year in range(1960, 2026):
            print(f"📅 Searching year {year}...", end=' ')
            
            year_urls = set()
            
            # その年度の全データを取得
            base_url = f"{self.base_url}?copy=&copywriter=&ad=&biz=&media=&start={year}&end={year}&target_prize=all"
            
            # ページネーション
            page = 1
            consecutive_empty = 0
            max_consecutive_empty = 3
            
            while consecutive_empty < max_consecutive_empty:
                page_url = f"{base_url}&page={page}"
                html = self.get_page(page_url)
                
                if html:
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # 詳細URLを抽出
                    detail_links = soup.find_all('a', href=lambda x: x and '/copira/id/' in x)
                    page_found = 0
                    
                    for link in detail_links:
                        href = link.get('href', '')
                        if not href.startswith('http'):
                            href = f"https://www.tcc.gr.jp{href}"
                        year_urls.add(href)
                        page_found += 1
                    
                    if page_found > 0:
                        consecutive_empty = 0
                    else:
                        consecutive_empty += 1
                        
                    page += 1
                    time.sleep(0.2)  # レート制限
                    
                    # 安全上限
                    if page > 500:
                        break
                else:
                    consecutive_empty += 1
            
            all_urls.update(year_urls)
            print(f"Found {len(year_urls)} URLs (Total: {len(all_urls):,})")
            
            # 定期保存
            if year % 10 == 0:
                self.save_urls_checkpoint(all_urls, f"year_{year}")
        
        return all_urls
    
    def strategy_award_category_search(self):
        """受賞カテゴリ別検索戦略"""
        print("🏆 Starting award category search...")
        all_urls = set()
        
        # 受賞カテゴリ別に検索
        award_categories = [
            'all',  # 全ての賞
            'tcc',  # TCC賞
            'new',  # 新人賞
            'student'  # 学生賞
        ]
        
        for category in award_categories:
            print(f"🏆 Searching award category: {category}...", end=' ')
            
            category_urls = set()
            base_url = f"{self.base_url}?copy=&copywriter=&ad=&biz=&media=&start=1960&end=2025&target_prize={category}"
            
            page = 1
            consecutive_empty = 0
            
            while consecutive_empty < 5:
                page_url = f"{base_url}&page={page}"
                html = self.get_page(page_url)
                
                if html:
                    soup = BeautifulSoup(html, 'html.parser')
                    detail_links = soup.find_all('a', href=lambda x: x and '/copira/id/' in x)
                    
                    page_found = 0
                    for link in detail_links:
                        href = link.get('href', '')
                        if not href.startswith('http'):
                            href = f"https://www.tcc.gr.jp{href}"
                        category_urls.add(href)
                        page_found += 1
                    
                    if page_found > 0:
                        consecutive_empty = 0
                    else:
                        consecutive_empty += 1
                        
                    page += 1
                    time.sleep(0.2)
                    
                    if page > 1000:
                        break
                else:
                    consecutive_empty += 1
            
            all_urls.update(category_urls)
            print(f"Found {len(category_urls)} URLs (Total: {len(all_urls):,})")
        
        return all_urls
    
    def strategy_media_type_search(self):
        """媒体別検索戦略"""
        print("📺 Starting media type search...")
        all_urls = set()
        
        # 媒体タイプ別検索
        media_types = [
            'tv',      # テレビ
            'radio',   # ラジオ
            'print',   # 印刷
            'web',     # ウェブ
            'outdoor', # 屋外
            'other'    # その他
        ]
        
        for media in media_types:
            print(f"📺 Searching media type: {media}...", end=' ')
            
            media_urls = set()
            base_url = f"{self.base_url}?copy=&copywriter=&ad=&biz=&media={media}&start=1960&end=2025&target_prize=all"
            
            page = 1
            consecutive_empty = 0
            
            while consecutive_empty < 5:
                page_url = f"{base_url}&page={page}"
                html = self.get_page(page_url)
                
                if html:
                    soup = BeautifulSoup(html, 'html.parser')
                    detail_links = soup.find_all('a', href=lambda x: x and '/copira/id/' in x)
                    
                    page_found = 0
                    for link in detail_links:
                        href = link.get('href', '')
                        if not href.startswith('http'):
                            href = f"https://www.tcc.gr.jp{href}"
                        media_urls.add(href)
                        page_found += 1
                    
                    if page_found > 0:
                        consecutive_empty = 0
                    else:
                        consecutive_empty += 1
                        
                    page += 1
                    time.sleep(0.2)
                    
                    if page > 1000:
                        break
                else:
                    consecutive_empty += 1
            
            all_urls.update(media_urls)
            print(f"Found {len(media_urls)} URLs (Total: {len(all_urls):,})")
        
        return all_urls
    
    def strategy_direct_id_enumeration(self):
        """直接ID列挙戦略"""
        print("🔢 Starting direct ID enumeration...")
        all_urls = set()
        
        # 既知のIDパターンを分析
        # 2023001, 2023352, 2024001 などのパターンから推測
        
        id_ranges = [
            (1, 10000),           # 初期のID
            (2020001, 2020999),   # 2020年
            (2021001, 2021999),   # 2021年
            (2022001, 2022999),   # 2022年
            (2023001, 2023999),   # 2023年
            (2024001, 2024999),   # 2024年
            (2025001, 2025999),   # 2025年
        ]
        
        for start_id, end_id in id_ranges:
            print(f"🔢 Checking ID range {start_id}-{end_id}...")
            
            range_urls = set()
            batch_size = 100
            
            for i in range(start_id, end_id + 1, batch_size):
                batch_end = min(i + batch_size - 1, end_id)
                
                # バッチでHEADリクエストを送信
                with ThreadPoolExecutor(max_workers=5) as executor:
                    futures = []
                    for id_num in range(i, batch_end + 1):
                        url = f"https://www.tcc.gr.jp/copira/id/{id_num}/"
                        future = executor.submit(self.check_url_exists, url)
                        futures.append((future, url))
                    
                    for future, url in futures:
                        if future.result():
                            range_urls.add(url)
                
                if i % 1000 == 0:
                    print(f"  Checked up to ID {i}, found {len(range_urls)} URLs")
                
                time.sleep(0.5)  # レート制限
            
            all_urls.update(range_urls)
            print(f"ID range {start_id}-{end_id}: Found {len(range_urls)} URLs (Total: {len(all_urls):,})")
        
        return all_urls
    
    def check_url_exists(self, url):
        """URLの存在チェック（HEADリクエスト）"""
        try:
            response = self.session.head(url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def save_urls_checkpoint(self, urls, suffix=""):
        """URL収集のチェックポイント保存"""
        filename = f"tcc_comprehensive_data/urls_checkpoint_{suffix}_{datetime.now().strftime('%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(list(urls), f, ensure_ascii=False, indent=2)
        print(f"💾 URLs checkpoint saved: {filename}")
    
    def comprehensive_url_collection(self):
        """包括的URL収集"""
        print("🌐 Starting comprehensive URL collection...")
        
        # 調査
        estimated_total = self.investigate_search_structure()
        print(f"🎯 Target: {estimated_total:,} items")
        
        # 複数戦略を実行
        strategies = [
            ("Year-by-year search", self.strategy_year_by_year_search),
            ("Award category search", self.strategy_award_category_search),
            ("Media type search", self.strategy_media_type_search),
            # ("Direct ID enumeration", self.strategy_direct_id_enumeration),  # 時間がかかるため最後に
        ]
        
        for strategy_name, strategy_func in strategies:
            print(f"\n🔄 Executing: {strategy_name}")
            try:
                strategy_urls = strategy_func()
                new_urls = strategy_urls - self.all_urls
                self.all_urls.update(new_urls)
                print(f"✅ {strategy_name}: +{len(new_urls):,} new URLs (Total: {len(self.all_urls):,})")
                
                # 中間保存
                self.save_urls_checkpoint(self.all_urls, strategy_name.replace(' ', '_').lower())
                
            except Exception as e:
                print(f"❌ {strategy_name} failed: {e}")
        
        print(f"\n🎉 URL collection complete: {len(self.all_urls):,} total URLs")
        return list(self.all_urls)
    
    def parse_detail_page(self, url):
        """詳細ページ解析"""
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
            
            # テーブルデータ
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
    
    def process_urls_parallel(self, urls):
        """並列URL処理"""
        print(f"⚡ Processing {len(urls):,} URLs in parallel...")
        
        start_time = datetime.now()
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            # タスクを送信
            future_to_url = {executor.submit(self.parse_detail_page, url): url for url in urls}
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    
                    with self.lock:
                        self.all_data.append(result)
                        
                        if 'error' not in result:
                            self.processed += 1
                        else:
                            self.failed += 1
                        
                        # 進捗表示
                        total_processed = len(self.all_data)
                        if total_processed % 100 == 0:
                            elapsed = datetime.now() - start_time
                            rate = total_processed / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0
                            eta_seconds = (len(urls) - total_processed) / rate if rate > 0 else 0
                            eta_minutes = eta_seconds / 60
                            
                            success_rate = self.processed / total_processed * 100
                            print(f"📊 {total_processed:,}/{len(urls):,} ({total_processed/len(urls)*100:.1f}%) - "
                                  f"Success: {success_rate:.1f}% - "
                                  f"Speed: {rate:.1f}/s - "
                                  f"ETA: {eta_minutes:.1f}min")
                            
                            # バッチ保存
                            if total_processed % 500 == 0:
                                self.save_batch(total_processed)
                
                except Exception as e:
                    with self.lock:
                        self.failed += 1
                        print(f"❌ Error processing {url}: {e}")
        
        print(f"✅ Parallel processing complete!")
        print(f"   Success: {self.processed:,}")
        print(f"   Failed: {self.failed:,}")
        print(f"   Total time: {datetime.now() - start_time}")
    
    def save_batch(self, count):
        """バッチ保存"""
        filename = f"tcc_comprehensive_data/batch_{count:06d}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.all_data, f, ensure_ascii=False, indent=2)
        print(f"💾 Batch saved: {filename}")
    
    def save_final_comprehensive_data(self):
        """最終包括データ保存"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # JSON
        json_file = f"tcc_comprehensive_data/tcc_comprehensive_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.all_data, f, ensure_ascii=False, indent=2)
        
        # CSV
        csv_file = f"tcc_comprehensive_data/tcc_comprehensive_{timestamp}.csv"
        self.save_as_csv(csv_file)
        
        # 統計
        stats_file = f"tcc_comprehensive_data/tcc_comprehensive_stats_{timestamp}.txt"
        self.save_comprehensive_stats(stats_file)
        
        print(f"💾 Comprehensive data saved:")
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
        
        simple_fields = sorted([f for f in all_fields])
        
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
    
    def save_comprehensive_stats(self, filename):
        """包括統計保存"""
        valid_data = [item for item in self.all_data if 'error' not in item]
        
        stats = []
        stats.append("TCC コピラ 包括クローリング結果")
        stats.append("=" * 60)
        stats.append(f"完了時刻: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        stats.append(f"総件数: {len(self.all_data):,}")
        stats.append(f"成功: {len(valid_data):,}")
        stats.append(f"失敗: {len(self.all_data) - len(valid_data):,}")
        stats.append(f"成功率: {len(valid_data)/len(self.all_data)*100:.1f}%" if self.all_data else "N/A")
        stats.append("")
        
        # 詳細統計
        if valid_data:
            # 年度統計
            years = {}
            for item in valid_data:
                year = item.get('year', item.get('publication_year', 'Unknown'))
                years[year] = years.get(year, 0) + 1
            
            stats.append("年度別統計 (上位30):")
            for year, count in sorted(years.items(), key=lambda x: x[0] if isinstance(x[0], int) else 0, reverse=True)[:30]:
                stats.append(f"  {year}: {count:,}件")
            
            # 媒体統計
            media = {}
            for item in valid_data:
                media_type = item.get('media_type', 'Unknown')
                media[media_type] = media.get(media_type, 0) + 1
            
            stats.append("\n媒体別統計:")
            for media_type, count in sorted(media.items(), key=lambda x: x[1], reverse=True):
                stats.append(f"  {media_type}: {count:,}件")
            
            # 受賞統計
            awards = {}
            for item in valid_data:
                award = item.get('award', 'なし')
                awards[award] = awards.get(award, 0) + 1
            
            stats.append("\n受賞統計 (上位20):")
            for award, count in sorted(awards.items(), key=lambda x: x[1], reverse=True)[:20]:
                stats.append(f"  {award}: {count:,}件")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(stats))
    
    def run_comprehensive_crawl(self):
        """包括クローリング実行"""
        try:
            # ステップ1: 包括的URL収集
            urls = self.comprehensive_url_collection()
            
            if not urls:
                print("❌ No URLs collected!")
                return
            
            print(f"\n🎯 Target URLs: {len(urls):,}")
            
            # ステップ2: 並列データ処理
            self.process_urls_parallel(urls)
            
            # ステップ3: 最終包括保存
            files = self.save_final_comprehensive_data()
            
            print("\n🎉 Comprehensive crawl completed successfully!")
            print(f"📊 Final stats: {self.processed:,} success, {self.failed:,} failed")
            print(f"🎯 Coverage: {len(self.all_data):,} / 37,259 ({len(self.all_data)/37259*100:.1f}%)")
            
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user")
            if self.all_data:
                self.save_final_comprehensive_data()
        except Exception as e:
            print(f"\n❌ Error: {e}")
            if self.all_data:
                self.save_final_comprehensive_data()

if __name__ == "__main__":
    crawler = ComprehensiveTCCCrawler()
    crawler.run_comprehensive_crawl()