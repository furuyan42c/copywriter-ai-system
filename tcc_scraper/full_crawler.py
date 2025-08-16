import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime
import os
from urllib.parse import urljoin, urlparse
import threading
from queue import Queue
import signal
import sys

class TCCFullCrawler:
    def __init__(self, output_dir="tcc_full_data", delay=1.0, max_workers=3):
        self.output_dir = output_dir
        self.delay = delay
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3'
        })
        
        self.total_items = 0
        self.crawled_items = 0
        self.failed_items = 0
        self.start_time = None
        self.stop_crawling = False
        
        # 出力ディレクトリを作成
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 中断時の処理
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        print(f"\n⚠️ 中断信号を受信しました。安全に停止中...")
        self.stop_crawling = True
    
    def fetch_page(self, url, retries=3):
        """ページを取得"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response.text
            except Exception as e:
                if attempt == retries - 1:
                    print(f"❌ ページ取得失敗: {url} - {e}")
                    return None
                time.sleep(2 ** attempt)  # 指数バックオフ
        return None
    
    def parse_list_page(self, html_content):
        """一覧ページから詳細URLリストを抽出"""
        soup = BeautifulSoup(html_content, 'html.parser')
        detail_urls = []
        
        # テーブルから詳細リンクを抽出
        table = soup.find('table', class_='table2__table')
        if table:
            links = table.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                if '/copira/id/' in href:
                    if not href.startswith('http'):
                        href = f"https://www.tcc.gr.jp{href}"
                    detail_urls.append(href)
        
        return detail_urls
    
    def parse_detail_page(self, html_content, url):
        """詳細ページのデータを抽出"""
        soup = BeautifulSoup(html_content, 'html.parser')
        data = {
            'url': url,
            'scraped_at': datetime.now().isoformat()
        }
        
        # IDを抽出
        id_match = re.search(r'/id/(\d+)', url)
        if id_match:
            data['id'] = id_match.group(1)
        
        # ページタイトル
        title_elem = soup.find('h1')
        if title_elem:
            data['title'] = title_elem.get_text(strip=True)
        
        # メタ情報テーブル
        info_table = soup.find('table', class_='table1__table')
        if info_table:
            rows = info_table.find_all('tr')
            for row in rows:
                th = row.find('th')
                td = row.find('td')
                if th and td:
                    key = th.get_text(strip=True).replace('：', '').replace(':', '')
                    value = td.get_text(strip=True)
                    
                    # キーを正規化して保存
                    key_mapping = {
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
                        'プロデューサー': 'producer',
                        'キャンペーン': 'campaign',
                        '作品': 'work_title'
                    }
                    
                    normalized_key = key_mapping.get(key, key.lower().replace(' ', '_'))
                    data[normalized_key] = value
        
        # コピーライターのリンク情報
        copywriter_links = soup.find_all('a', href=lambda x: x and '/copitan/' in x)
        if copywriter_links:
            data['copywriter_links'] = []
            for link in copywriter_links:
                copywriter_info = {
                    'name': link.get_text(strip=True),
                    'url': link.get('href', '')
                }
                # コピーライターIDを抽出
                id_match = re.search(r'/id/(\d+)', link.get('href', ''))
                if id_match:
                    copywriter_info['id'] = id_match.group(1)
                data['copywriter_links'].append(copywriter_info)
        
        # ページ全体のテキスト（コピー内容など）
        # ナビゲーションやフッターを除外
        main_content = soup.find('main') or soup.find('div', class_='main') or soup
        if main_content:
            # 不要な要素を除去
            for elem in main_content.find_all(['nav', 'header', 'footer', 'script', 'style']):
                elem.decompose()
            
            content_text = main_content.get_text(separator='\n', strip=True)
            # 長すぎる場合は制限
            if len(content_text) > 5000:
                content_text = content_text[:5000] + "..."
            data['content_text'] = content_text
        
        # 画像情報
        images = soup.find_all('img', src=True)
        if images:
            data['images'] = []
            for img in images:
                src = img.get('src', '')
                if src and not src.startswith('data:') and 'icon' not in src.lower():
                    if not src.startswith('http'):
                        src = urljoin(url, src)
                    data['images'].append({
                        'src': src,
                        'alt': img.get('alt', ''),
                        'title': img.get('title', '')
                    })
        
        return data
    
    def get_total_pages(self):
        """総ページ数を取得"""
        base_url = "https://www.tcc.gr.jp/copira/"
        params = {
            'copy': '',
            'copywriter': '',
            'ad': '',
            'biz': '',
            'media': '',
            'start': '1960',
            'end': '2025',
            'target_prize': 'all',
            'limit': '20'  # 1ページあたり20件
        }
        
        url = f"{base_url}?" + "&".join([f"{k}={v}" for k, v in params.items()])
        html = self.fetch_page(url)
        
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 総件数を取得
            result_text = soup.find(string=re.compile(r'\d+件が検索されました'))
            if result_text:
                match = re.search(r'(\d+)件が検索されました', result_text)
                if match:
                    self.total_items = int(match.group(1))
                    total_pages = (self.total_items + 19) // 20  # 20件ずつ、切り上げ
                    return total_pages
        
        return 0
    
    def crawl_all_data(self):
        """全データをクローリング"""
        print("🚀 TCC コピラ 全データクローリング開始")
        print("=" * 60)
        
        # 総ページ数を取得
        total_pages = self.get_total_pages()
        if total_pages == 0:
            print("❌ 総ページ数の取得に失敗しました")
            return
        
        print(f"📊 推定総件数: {self.total_items:,}件")
        print(f"📄 総ページ数: {total_pages:,}ページ")
        print(f"⏱️ 推定所要時間: {total_pages * self.delay / 60:.1f}分")
        print(f"💾 出力ディレクトリ: {self.output_dir}")
        print("")
        
        self.start_time = datetime.now()
        all_detail_urls = []
        
        # 段階1: 一覧ページから詳細URLを収集
        print("📥 段階1: 詳細URLの収集")
        print("-" * 30)
        
        base_url = "https://www.tcc.gr.jp/copira/"
        
        for page_num in range(1, total_pages + 1):
            if self.stop_crawling:
                break
            
            # URLを構築
            if page_num == 1:
                url = f"{base_url}?copy=&copywriter=&ad=&biz=&media=&start=1960&end=2025&target_prize=all&limit=20"
            else:
                url = f"{base_url}page/{page_num}/?copy=&copywriter=&ad=&biz=&media=&start=1960&end=2025&target_prize=all&limit=20"
            
            print(f"  📄 ページ {page_num:4d}/{total_pages:4d} を処理中... ", end='')
            
            html = self.fetch_page(url)
            if html:
                detail_urls = self.parse_list_page(html)
                all_detail_urls.extend(detail_urls)
                print(f"✅ {len(detail_urls)}件のURL取得")
            else:
                print("❌ 取得失敗")
                self.failed_items += 1
            
            # 進捗を定期的に保存
            if page_num % 100 == 0:
                self.save_urls_checkpoint(all_detail_urls, page_num)
            
            time.sleep(self.delay)
        
        # URLリストを保存
        urls_file = os.path.join(self.output_dir, f"all_detail_urls_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(urls_file, 'w', encoding='utf-8') as f:
            json.dump(all_detail_urls, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 詳細URL収集完了: {len(all_detail_urls)}件")
        print(f"💾 URLリスト保存: {urls_file}")
        
        # 重複除去
        unique_urls = list(set(all_detail_urls))
        print(f"🔄 重複除去後: {len(unique_urls)}件")
        
        if not unique_urls:
            print("❌ 詳細URLが見つかりませんでした")
            return
        
        # 段階2: 詳細ページのデータを取得
        print(f"\n📥 段階2: 詳細データの取得 ({len(unique_urls)}件)")
        print("-" * 30)
        
        all_data = []
        
        for i, detail_url in enumerate(unique_urls, 1):
            if self.stop_crawling:
                break
            
            print(f"  📄 {i:5d}/{len(unique_urls):5d} {detail_url} ... ", end='')
            
            html = self.fetch_page(detail_url)
            if html:
                try:
                    data = self.parse_detail_page(html, detail_url)
                    all_data.append(data)
                    self.crawled_items += 1
                    print("✅")
                except Exception as e:
                    print(f"❌ 解析エラー: {e}")
                    self.failed_items += 1
            else:
                print("❌ 取得失敗")
                self.failed_items += 1
            
            # 進捗を定期的に保存
            if i % 100 == 0:
                self.save_data_checkpoint(all_data, i)
                self.print_progress(i, len(unique_urls))
            
            time.sleep(self.delay)
        
        # 最終データを保存
        self.save_final_data(all_data)
        self.print_final_summary(len(unique_urls))
    
    def save_urls_checkpoint(self, urls, page_num):
        """URLリストのチェックポイント保存"""
        checkpoint_file = os.path.join(self.output_dir, f"urls_checkpoint_page{page_num}.json")
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(urls, f, ensure_ascii=False, indent=2)
        print(f"    💾 チェックポイント保存: {checkpoint_file}")
    
    def save_data_checkpoint(self, data, count):
        """データのチェックポイント保存"""
        checkpoint_file = os.path.join(self.output_dir, f"data_checkpoint_{count}.json")
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"    💾 チェックポイント保存: {checkpoint_file}")
    
    def save_final_data(self, data):
        """最終データを保存"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # JSON形式
        json_file = os.path.join(self.output_dir, f"tcc_full_data_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # CSV形式
        csv_file = os.path.join(self.output_dir, f"tcc_full_data_{timestamp}.csv")
        self.save_as_csv(data, csv_file)
        
        print(f"\n💾 最終データ保存:")
        print(f"  📋 JSON: {json_file}")
        print(f"  📊 CSV:  {csv_file}")
    
    def save_as_csv(self, data, csv_file):
        """データをCSV形式で保存"""
        import csv
        
        if not data:
            return
        
        # すべてのキーを収集
        all_keys = set()
        for item in data:
            all_keys.update(item.keys())
        
        # 複雑なデータ型を除外
        simple_keys = []
        for key in sorted(all_keys):
            if key not in ['copywriter_links', 'images', 'content_text']:
                simple_keys.append(key)
        
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=simple_keys)
            writer.writeheader()
            
            for item in data:
                row = {}
                for key in simple_keys:
                    value = item.get(key, '')
                    # 複雑なデータは文字列化
                    if isinstance(value, (list, dict)):
                        value = str(value)
                    row[key] = value
                writer.writerow(row)
    
    def print_progress(self, current, total):
        """進捗を表示"""
        elapsed = datetime.now() - self.start_time
        rate = current / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0
        eta_seconds = (total - current) / rate if rate > 0 else 0
        eta = str(datetime.timedelta(seconds=int(eta_seconds)))
        
        print(f"    📊 進捗: {current}/{total} ({current/total*100:.1f}%) "
              f"取得速度: {rate:.1f}件/秒 ETA: {eta}")
    
    def print_final_summary(self, total_attempted):
        """最終サマリーを表示"""
        elapsed = datetime.now() - self.start_time
        
        print(f"\n🎉 クローリング完了!")
        print("=" * 60)
        print(f"📊 総試行件数    : {total_attempted:,}")
        print(f"✅ 成功件数      : {self.crawled_items:,}")
        print(f"❌ 失敗件数      : {self.failed_items:,}")
        print(f"📈 成功率        : {self.crawled_items/total_attempted*100:.1f}%")
        print(f"⏱️ 所要時間      : {elapsed}")
        print(f"🚀 平均取得速度   : {self.crawled_items/elapsed.total_seconds():.2f}件/秒")
        print("=" * 60)

def main():
    """メイン関数"""
    print("TCC コピラ 全データクローラー")
    print("=" * 40)
    print("注意: この処理は非常に時間がかかります（数時間）")
    print("Ctrl+C で安全に中断できます")
    print("")
    
    # 設定
    crawler = TCCFullCrawler(
        output_dir="tcc_full_data",
        delay=1.0,  # サーバーに優しい間隔
        max_workers=1  # 今回は単一スレッド
    )
    
    # クローリング開始
    crawler.crawl_all_data()

if __name__ == "__main__":
    main()