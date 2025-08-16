#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime
import os

class DirectTCCCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.base_url = "https://www.tcc.gr.jp/copira/"
        self.all_data = []
        self.processed = 0
        self.failed = 0
        
        # 出力ディレクトリ
        os.makedirs("tcc_final_data", exist_ok=True)
    
    def log(self, message):
        """ログ出力"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {message}")
        
    def get_page(self, url, retries=3):
        """ページを取得"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response.text
            except Exception as e:
                if attempt == retries - 1:
                    self.log(f"❌ Failed: {url}")
                    return None
                time.sleep(2)
        return None
    
    def find_all_detail_urls(self):
        """全ての詳細URLを発見"""
        self.log("🔍 Starting comprehensive URL discovery...")
        
        all_urls = set()
        
        # 複数の戦略を試行
        strategies = [
            self.strategy_pagination_links,
            self.strategy_direct_enumeration,
            self.strategy_search_by_year
        ]
        
        for strategy in strategies:
            self.log(f"🔄 Trying strategy: {strategy.__name__}")
            urls = strategy()
            all_urls.update(urls)
            self.log(f"✅ Found {len(urls)} URLs, Total: {len(all_urls)}")
            
            if len(all_urls) > 35000:  # 十分な数が見つかったら停止
                break
        
        self.log(f"🎯 Total URLs discovered: {len(all_urls)}")
        return list(all_urls)
    
    def strategy_pagination_links(self):
        """ページネーションリンクを辿る戦略"""
        urls = set()
        
        # 異なる表示件数で試行
        for limit in [10, 20, 50]:
            page = 1
            consecutive_failures = 0
            
            while consecutive_failures < 5:
                url = f"{self.base_url}?copy=&copywriter=&ad=&biz=&media=&start=1960&end=2025&target_prize=all&limit={limit}&page={page}"
                
                html = self.get_page(url)
                if html:
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # 詳細リンクを抽出
                    links = soup.find_all('a', href=True)
                    page_urls = []
                    for link in links:
                        href = link.get('href', '')
                        if '/copira/id/' in href:
                            if not href.startswith('http'):
                                href = f"https://www.tcc.gr.jp{href}"
                            page_urls.append(href)
                    
                    if page_urls:
                        urls.update(page_urls)
                        consecutive_failures = 0
                        if page % 100 == 0:
                            self.log(f"  Page {page}: {len(page_urls)} URLs")
                    else:
                        consecutive_failures += 1
                else:
                    consecutive_failures += 1
                
                page += 1
                time.sleep(0.5)
                
                # 安全な上限
                if page > 2000:
                    break
        
        return urls
    
    def strategy_direct_enumeration(self):
        """直接ID列挙戦略"""
        urls = set()
        
        # 既知のIDパターンを分析して範囲を推定
        sample_ids = [2023001, 2023352, 2024001]  # サンプル
        
        # 年度別にID範囲を推定
        for year in range(1960, 2026):
            start_id = year * 1000
            end_id = start_id + 999
            
            self.log(f"  Checking year {year}: {start_id}-{end_id}")
            
            found_in_year = 0
            for id_num in range(start_id, end_id + 1):
                url = f"https://www.tcc.gr.jp/copira/id/{id_num}/"
                
                # 軽量チェック（HEADリクエスト）
                try:
                    response = self.session.head(url, timeout=10)
                    if response.status_code == 200:
                        urls.add(url)
                        found_in_year += 1
                except:
                    pass
                
                if id_num % 50 == 0:
                    time.sleep(0.1)  # レート制限
            
            if found_in_year > 0:
                self.log(f"    Found {found_in_year} URLs for {year}")
        
        return urls
    
    def strategy_search_by_year(self):
        """年度別検索戦略"""
        urls = set()
        
        for year in range(1960, 2026):
            url = f"{self.base_url}?copy=&copywriter=&ad=&biz=&media=&start={year}&end={year}&target_prize=all"
            
            html = self.get_page(url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                
                # この年度の全ページを辿る
                page = 1
                while page < 1000:  # 安全上限
                    page_url = f"{url}&page={page}"
                    page_html = self.get_page(page_url)
                    
                    if page_html:
                        page_soup = BeautifulSoup(page_html, 'html.parser')
                        links = page_soup.find_all('a', href=True)
                        
                        page_urls = []
                        for link in links:
                            href = link.get('href', '')
                            if '/copira/id/' in href:
                                if not href.startswith('http'):
                                    href = f"https://www.tcc.gr.jp{href}"
                                page_urls.append(href)
                        
                        if page_urls:
                            urls.update(page_urls)
                        else:
                            break  # このページにデータがなければ終了
                    else:
                        break
                    
                    page += 1
                    time.sleep(0.3)
            
            self.log(f"  Year {year}: {len(urls)} total URLs so far")
        
        return urls
    
    def extract_detail_data(self, url):
        """詳細データを抽出"""
        html = self.get_page(url)
        if not html:
            return {'error': 'fetch_failed', 'url': url}
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            data = {'url': url, 'scraped_at': datetime.now().isoformat()}
            
            # ID抽出
            id_match = re.search(r'/id/(\d+)', url)
            if id_match:
                data['id'] = id_match.group(1)
            
            # タイトル
            title = soup.find('h1') or soup.find('title')
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
            
            # コピーライターリンク
            cw_links = soup.find_all('a', href=lambda x: x and '/copitan/' in x)
            if cw_links:
                data['copywriter_links'] = []
                for link in cw_links:
                    cw_data = {'name': link.get_text(strip=True), 'url': link.get('href', '')}
                    id_match = re.search(r'/id/(\d+)', link.get('href', ''))
                    if id_match:
                        cw_data['id'] = id_match.group(1)
                    data['copywriter_links'].append(cw_data)
            
            return data
            
        except Exception as e:
            return {'error': str(e), 'url': url}
    
    def process_all_urls(self, urls):
        """全URLを処理"""
        self.log(f"🔄 Processing {len(urls)} URLs...")
        
        for i, url in enumerate(urls, 1):
            data = self.extract_detail_data(url)
            self.all_data.append(data)
            
            if 'error' not in data:
                self.processed += 1
            else:
                self.failed += 1
            
            # 進捗表示
            if i % 100 == 0:
                success_rate = self.processed / i * 100
                self.log(f"📊 {i}/{len(urls)} ({i/len(urls)*100:.1f}%) - Success: {success_rate:.1f}%")
                
                # バッチ保存
                self.save_batch(i)
            
            time.sleep(0.5)  # サーバーに優しく
        
        self.log(f"✅ Processing complete: {self.processed} success, {self.failed} failed")
    
    def save_batch(self, count):
        """バッチデータを保存"""
        filename = f"tcc_final_data/batch_{count:06d}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.all_data, f, ensure_ascii=False, indent=2)
        self.log(f"💾 Batch saved: {filename}")
    
    def save_final_data(self):
        """最終データを保存"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 完全JSON
        json_file = f"tcc_final_data/tcc_complete_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.all_data, f, ensure_ascii=False, indent=2)
        
        # CSV
        csv_file = f"tcc_final_data/tcc_complete_{timestamp}.csv"
        self.save_as_csv(csv_file)
        
        # 統計
        stats_file = f"tcc_final_data/tcc_stats_{timestamp}.txt"
        self.save_statistics(stats_file)
        
        self.log(f"💾 Final data saved:")
        self.log(f"  📋 JSON: {json_file}")
        self.log(f"  📊 CSV: {csv_file}")
        self.log(f"  📈 Stats: {stats_file}")
    
    def save_as_csv(self, filename):
        """CSV形式で保存"""
        import csv
        
        if not self.all_data:
            return
        
        # 有効なデータのみ
        valid_data = [item for item in self.all_data if 'error' not in item]
        if not valid_data:
            return
        
        # フィールド収集
        all_fields = set()
        for item in valid_data:
            all_fields.update(item.keys())
        
        # 複雑なフィールドを除外
        simple_fields = [f for f in sorted(all_fields) if f not in ['copywriter_links']]
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=simple_fields)
            writer.writeheader()
            
            for item in valid_data:
                row = {}
                for field in simple_fields:
                    value = item.get(field, '')
                    if isinstance(value, (list, dict)):
                        value = str(value)
                    row[field] = str(value)[:500]  # 長さ制限
                writer.writerow(row)
    
    def save_statistics(self, filename):
        """統計情報を保存"""
        valid_data = [item for item in self.all_data if 'error' not in item]
        
        stats = []
        stats.append(f"TCC コピラ 完全データ統計")
        stats.append(f"=" * 50)
        stats.append(f"処理日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        stats.append(f"総件数: {len(self.all_data):,}")
        stats.append(f"成功: {len(valid_data):,}")
        stats.append(f"失敗: {len(self.all_data) - len(valid_data):,}")
        stats.append(f"成功率: {len(valid_data)/len(self.all_data)*100:.1f}%")
        stats.append("")
        
        # 年度別統計
        years = {}
        for item in valid_data:
            year = item.get('publication_year', 'Unknown')
            years[year] = years.get(year, 0) + 1
        
        stats.append("年度別統計:")
        for year, count in sorted(years.items(), key=lambda x: x[0], reverse=True)[:20]:
            stats.append(f"  {year}: {count:,}件")
        
        # 媒体別統計
        media = {}
        for item in valid_data:
            media_type = item.get('media_type', 'Unknown')
            media[media_type] = media.get(media_type, 0) + 1
        
        stats.append("\n媒体別統計:")
        for media_type, count in sorted(media.items(), key=lambda x: x[1], reverse=True):
            stats.append(f"  {media_type}: {count:,}件")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(stats))
    
    def run_complete_crawl(self):
        """完全クローリングを実行"""
        self.log("🚀 TCC Complete Data Crawler Starting...")
        
        # ステップ1: URL発見
        urls = self.find_all_detail_urls()
        
        if not urls:
            self.log("❌ No URLs found!")
            return
        
        # ステップ2: データ処理
        self.process_all_urls(urls)
        
        # ステップ3: 最終保存
        self.save_final_data()
        
        self.log("🎉 Complete crawl finished!")

if __name__ == "__main__":
    crawler = DirectTCCCrawler()
    crawler.run_complete_crawl()