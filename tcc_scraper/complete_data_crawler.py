import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime, timedelta
import os
from urllib.parse import urljoin, urlparse, parse_qs
import signal
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue

class CompleteTCCCrawler:
    def __init__(self, output_dir="tcc_complete_data", delay=0.3, max_workers=2):
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
        self.processed_items = 0
        self.failed_items = 0
        self.start_time = None
        self.stop_crawling = False
        
        # 進捗追跡
        self.all_urls = set()
        self.processed_urls = set()
        
        # 出力ディレクトリを作成
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 中断処理
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # 状態ファイル
        self.state_file = os.path.join(self.output_dir, "crawler_state.json")
        self.data_file = os.path.join(self.output_dir, "complete_data.json")
        self.batch_counter = 0
    
    def signal_handler(self, signum, frame):
        print(f"\n⚠️ 停止信号を受信。安全に終了中...")
        self.stop_crawling = True
        self.save_state()
    
    def save_state(self):
        """現在の状態を保存"""
        state = {
            'total_items': self.total_items,
            'processed_items': self.processed_items,
            'failed_items': self.failed_items,
            'all_urls': list(self.all_urls),
            'processed_urls': list(self.processed_urls),
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'last_update': datetime.now().isoformat()
        }
        
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        print(f"💾 状態保存: {len(self.processed_urls)}/{len(self.all_urls)} 完了")
    
    def load_state(self):
        """保存された状態を復元"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                
                self.total_items = state.get('total_items', 0)
                self.processed_items = state.get('processed_items', 0)
                self.failed_items = state.get('failed_items', 0)
                self.all_urls = set(state.get('all_urls', []))
                self.processed_urls = set(state.get('processed_urls', []))
                
                start_time_str = state.get('start_time')
                if start_time_str:
                    self.start_time = datetime.fromisoformat(start_time_str)
                
                print(f"📊 状態復元: {len(self.processed_urls)}/{len(self.all_urls)} 完了")
                return True
            except Exception as e:
                print(f"⚠️ 状態復元エラー: {e}")
        return False
    
    def fetch_page_robust(self, url, retries=3):
        """堅牢なページ取得"""
        for attempt in range(retries):
            try:
                # セッションを使用してconnection poolingを活用
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response.text
            except Exception as e:
                if attempt == retries - 1:
                    print(f"❌ 最終的に失敗: {url}")
                    return None
                print(f"⚠️ リトライ {attempt + 1}/{retries}: {url}")
                time.sleep(2 ** attempt)  # 指数バックオフ
        return None
    
    def discover_all_pagination_patterns(self):
        """全てのページネーションパターンを発見"""
        print("🔍 ページネーション構造の完全調査...")
        
        base_url = "https://www.tcc.gr.jp/copira/"
        params_base = {
            'copy': '',
            'copywriter': '',
            'ad': '',
            'biz': '',
            'media': '',
            'start': '1960',
            'end': '2025',
            'target_prize': 'all'
        }
        
        # 異なる表示件数設定を試す
        items_per_page_options = [10, 15, 20, 50]
        max_discovered_page = 0
        best_pattern = None
        
        for items_per_page in items_per_page_options:
            print(f"📊 {items_per_page}件/ページ設定をテスト中...")
            
            # 最初のページで総件数と構造を確認
            url = f"{base_url}?" + "&".join([f"{k}={v}" for k, v in params_base.items()]) + f"&limit={items_per_page}"
            html = self.fetch_page_robust(url)
            
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                
                # 総件数を取得
                result_text = soup.find(string=re.compile(r'\d+件が検索されました'))
                if result_text:
                    match = re.search(r'(\d+)件が検索されました', result_text)
                    if match:
                        self.total_items = int(match.group(1))
                        print(f"  📈 総件数: {self.total_items:,}件")
                
                # ページネーションリンクを分析
                pagination_links = soup.find_all('a', href=True)
                page_numbers = []
                
                for link in pagination_links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    # 数字のリンクを探す
                    if text.isdigit():
                        page_numbers.append(int(text))
                    
                    # URLパターンからページ数を抽出
                    page_match = re.search(r'[?&](?:page|p)=(\d+)', href)
                    if page_match:
                        page_numbers.append(int(page_match.group(1)))
                    
                    # page/123/ パターン
                    path_match = re.search(r'/page/(\d+)/', href)
                    if path_match:
                        page_numbers.append(int(path_match.group(1)))
                
                if page_numbers:
                    discovered_max = max(page_numbers)
                    print(f"  📄 発見最大ページ: {discovered_max}")
                    
                    if discovered_max > max_discovered_page:
                        max_discovered_page = discovered_max
                        best_pattern = {
                            'items_per_page': items_per_page,
                            'max_page': discovered_max,
                            'total_estimated': discovered_max * items_per_page
                        }
                
                # 推定最大ページ数も計算
                if self.total_items > 0:
                    estimated_pages = (self.total_items + items_per_page - 1) // items_per_page
                    print(f"  🧮 推定ページ数: {estimated_pages}")
                    
                    if estimated_pages > max_discovered_page:
                        max_discovered_page = estimated_pages
                        best_pattern = {
                            'items_per_page': items_per_page,
                            'max_page': estimated_pages,
                            'total_estimated': self.total_items
                        }
        
        if best_pattern:
            print(f"✅ 最適パターン発見:")
            print(f"  - {best_pattern['items_per_page']}件/ページ")
            print(f"  - 最大ページ: {best_pattern['max_page']:,}")
            print(f"  - 推定総件数: {best_pattern['total_estimated']:,}")
        
        return best_pattern
    
    def extract_all_urls_comprehensive(self):
        """包括的URL抽出"""
        print("🌐 全URL抽出開始 (包括的アプローチ)")
        
        # 既存のURLをロード
        if self.all_urls:
            print(f"📁 既存URL: {len(self.all_urls)}件")
        
        # 最適なページネーション設定を発見
        best_pattern = self.discover_all_pagination_patterns()
        
        if not best_pattern:
            print("❌ ページネーション設定の発見に失敗")
            return False
        
        base_url = "https://www.tcc.gr.jp/copira/"
        items_per_page = best_pattern['items_per_page']
        max_page = best_pattern['max_page']
        
        # 複数のURLパターンを生成
        url_patterns = [
            lambda p: f"{base_url}?copy=&copywriter=&ad=&biz=&media=&start=1960&end=2025&target_prize=all&limit={items_per_page}&page={p}",
            lambda p: f"{base_url}page/{p}/?copy=&copywriter=&ad=&biz=&media=&start=1960&end=2025&target_prize=all&limit={items_per_page}",
            lambda p: f"{base_url}?copy=&copywriter=&ad=&biz=&media=&start=1960&end=2025&target_prize=all&p={p}&limit={items_per_page}"
        ]
        
        print(f"🔄 {max_page:,}ページを処理中...")
        
        urls_found = 0
        consecutive_failures = 0
        max_consecutive_failures = 10
        
        for page_num in range(1, max_page + 1):
            if self.stop_crawling:
                break
            
            if page_num % 100 == 0:
                print(f"📊 進捗: {page_num:,}/{max_page:,} ({page_num/max_page*100:.1f}%) - 発見URL: {urls_found:,}")
                self.save_state()
            
            page_urls = []
            
            # 複数のURLパターンを試行
            for pattern_idx, pattern in enumerate(url_patterns):
                if page_urls:  # 成功したらループを抜ける
                    break
                
                url = pattern(page_num)
                html = self.fetch_page_robust(url)
                
                if html:
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # 詳細ページリンクを抽出
                    links = soup.find_all('a', href=True)
                    for link in links:
                        href = link.get('href', '')
                        if '/copira/id/' in href:
                            if not href.startswith('http'):
                                href = f"https://www.tcc.gr.jp{href}"
                            page_urls.append(href)
                    
                    if page_urls:
                        consecutive_failures = 0
                    else:
                        # コンテンツがあるがリンクがない場合
                        if len(soup.get_text()) > 1000:  # 有意なコンテンツがある
                            consecutive_failures = 0
                        else:
                            consecutive_failures += 1
            
            if page_urls:
                new_urls = [url for url in page_urls if url not in self.all_urls]
                self.all_urls.update(new_urls)
                urls_found += len(new_urls)
                
                if page_num % 50 == 0:
                    print(f"  📄 ページ {page_num}: {len(page_urls)}件 (新規: {len(new_urls)}件)")
            else:
                consecutive_failures += 1
                if consecutive_failures >= max_consecutive_failures:
                    print(f"⚠️ 連続失敗 {consecutive_failures}回 - 早期終了")
                    break
            
            time.sleep(self.delay)
        
        print(f"✅ URL抽出完了: {len(self.all_urls):,}件")
        return True
    
    def parse_detail_page_comprehensive(self, url):
        """包括的詳細ページ解析"""
        html = self.fetch_page_robust(url)
        if not html:
            return {'error': 'fetch_failed', 'url': url}
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            data = {
                'url': url,
                'scraped_at': datetime.now().isoformat()
            }
            
            # IDを抽出
            id_match = re.search(r'/id/(\d+)', url)
            if id_match:
                data['id'] = id_match.group(1)
            
            # ページタイトル
            title_elem = soup.find('h1') or soup.find('title')
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                # 「| 東京コピーライターズクラブ」などを除去
                title_text = re.sub(r'\s*[|｜]\s*東京コピーライターズクラブ.*$', '', title_text)
                data['title'] = title_text
            
            # メイン情報テーブル
            info_tables = soup.find_all('table')
            for table in info_tables:
                if table.find('th') and table.find('td'):  # テーブルの構造を確認
                    rows = table.find_all('tr')
                    for row in rows:
                        th = row.find('th')
                        td = row.find('td')
                        if th and td:
                            key = th.get_text(strip=True).replace('：', '').replace(':', '')
                            value = td.get_text(strip=True)
                            
                            # 正規化されたキーマッピング
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
                                '作品': 'work_title',
                                'クリエイティブディレクター': 'creative_director',
                                'アートディレクター': 'art_director'
                            }
                            
                            normalized_key = key_mapping.get(key, key.lower().replace(' ', '_').replace('　', '_'))
                            if value and value.strip():
                                data[normalized_key] = value
            
            # コピーライターリンク情報
            copywriter_links = soup.find_all('a', href=lambda x: x and '/copitan/' in x)
            if copywriter_links:
                data['copywriter_details'] = []
                for link in copywriter_links:
                    cw_info = {
                        'name': link.get_text(strip=True),
                        'url': link.get('href', '')
                    }
                    # コピーライターIDを抽出
                    id_match = re.search(r'/id/(\d+)', link.get('href', ''))
                    if id_match:
                        cw_info['id'] = id_match.group(1)
                    data['copywriter_details'].append(cw_info)
            
            # 年度を正規化
            if 'publication_year' in data:
                year_match = re.search(r'(\d{4})', data['publication_year'])
                if year_match:
                    data['year'] = int(year_match.group(1))
            
            # 画像情報
            images = soup.find_all('img', src=True)
            image_urls = []
            for img in images:
                src = img.get('src', '')
                if src and not src.startswith('data:') and 'icon' not in src.lower() and 'logo' not in src.lower():
                    if not src.startswith('http'):
                        src = urljoin(url, src)
                    image_urls.append({
                        'src': src,
                        'alt': img.get('alt', ''),
                        'title': img.get('title', '')
                    })
            
            if image_urls:
                data['images'] = image_urls
            
            # メインコンテンツテキスト抽出
            main_content = soup.find('main') or soup.find('div', class_='main') or soup.find('article')
            if main_content:
                # ナビゲーション等を除去
                for unwanted in main_content.find_all(['nav', 'header', 'footer', 'script', 'style']):
                    unwanted.decompose()
                
                content_text = main_content.get_text(separator='\n', strip=True)
                # 長すぎる場合は制限
                if len(content_text) > 3000:
                    content_text = content_text[:3000] + "..."
                data['content'] = content_text
            
            return data
            
        except Exception as e:
            return {'error': str(e), 'url': url}
    
    def process_urls_parallel(self):
        """並列でURLを処理"""
        remaining_urls = [url for url in self.all_urls if url not in self.processed_urls]
        
        if not remaining_urls:
            print("✅ 全URLが既に処理済みです")
            return []
        
        print(f"🔄 {len(remaining_urls):,}件の詳細データを並列取得中...")
        
        all_data = []
        processed_count = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 未来のタスクを作成
            future_to_url = {
                executor.submit(self.parse_detail_page_comprehensive, url): url 
                for url in remaining_urls[:1000]  # 最初の1000件から開始
            }
            
            for future in as_completed(future_to_url):
                if self.stop_crawling:
                    break
                
                url = future_to_url[future]
                try:
                    result = future.result()
                    all_data.append(result)
                    self.processed_urls.add(url)
                    
                    if 'error' not in result:
                        self.processed_items += 1
                    else:
                        self.failed_items += 1
                    
                    processed_count += 1
                    
                    # 進捗表示
                    if processed_count % 50 == 0:
                        elapsed = datetime.now() - self.start_time if self.start_time else timedelta(0)
                        rate = processed_count / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0
                        
                        print(f"📊 {processed_count:,}/{len(remaining_urls):,} "
                              f"({processed_count/len(remaining_urls)*100:.1f}%) "
                              f"速度: {rate:.1f}件/秒")
                    
                    # バッチ保存
                    if processed_count % 100 == 0:
                        self.save_batch_data(all_data[-100:])
                        self.save_state()
                    
                except Exception as e:
                    print(f"❌ 処理エラー {url}: {e}")
                    self.failed_items += 1
                
                time.sleep(self.delay)
        
        return all_data
    
    def save_batch_data(self, batch_data):
        """バッチデータを保存"""
        self.batch_counter += 1
        batch_file = os.path.join(self.output_dir, f"batch_{self.batch_counter:04d}.json")
        
        with open(batch_file, 'w', encoding='utf-8') as f:
            json.dump(batch_data, f, ensure_ascii=False, indent=2)
    
    def consolidate_all_batches(self):
        """全バッチを統合"""
        print("🔄 バッチデータ統合中...")
        
        all_data = []
        batch_files = [f for f in os.listdir(self.output_dir) if f.startswith('batch_') and f.endswith('.json')]
        batch_files.sort()
        
        for batch_file in batch_files:
            file_path = os.path.join(self.output_dir, batch_file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    batch_data = json.load(f)
                    all_data.extend(batch_data)
                print(f"  📁 統合: {batch_file} ({len(batch_data)}件)")
            except Exception as e:
                print(f"  ❌ エラー: {batch_file} - {e}")
        
        return all_data
    
    def save_final_complete_dataset(self, data):
        """最終完全データセットを保存"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 完全データセット
        complete_file = os.path.join(self.output_dir, f"tcc_complete_dataset_{timestamp}.json")
        with open(complete_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 統計サマリー
        summary_file = os.path.join(self.output_dir, f"tcc_summary_{timestamp}.json")
        summary = self.create_comprehensive_summary(data)
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        # CSV形式
        csv_file = os.path.join(self.output_dir, f"tcc_complete_{timestamp}.csv")
        self.save_as_comprehensive_csv(data, csv_file)
        
        print(f"\n💾 最終データセット保存:")
        print(f"  📋 完全JSON: {complete_file}")
        print(f"  📊 統計JSON: {summary_file}")
        print(f"  📈 CSV: {csv_file}")
        
        return complete_file, summary_file, csv_file
    
    def create_comprehensive_summary(self, data):
        """包括的サマリーを作成"""
        valid_data = [item for item in data if 'error' not in item]
        
        summary = {
            'metadata': {
                'total_items': len(data),
                'valid_items': len(valid_data),
                'error_items': len(data) - len(valid_data),
                'success_rate': len(valid_data) / len(data) * 100 if data else 0,
                'crawl_date': datetime.now().isoformat()
            },
            'statistics': {}
        }
        
        # 各フィールドの統計
        fields_to_analyze = [
            'publication_year', 'media_type', 'industry', 'award', 
            'advertiser', 'agency', 'production_company'
        ]
        
        for field in fields_to_analyze:
            field_stats = {}
            for item in valid_data:
                value = item.get(field, 'Unknown')
                if value and str(value).strip():
                    field_stats[str(value)] = field_stats.get(str(value), 0) + 1
            
            if field_stats:
                summary['statistics'][field] = dict(
                    sorted(field_stats.items(), key=lambda x: x[1], reverse=True)
                )
        
        return summary
    
    def save_as_comprehensive_csv(self, data, csv_file):
        """包括的CSVファイルを作成"""
        import csv
        
        if not data:
            return
        
        # 全フィールドを収集
        all_fields = set()
        for item in data:
            all_fields.update(item.keys())
        
        # 複雑なフィールドを除外
        simple_fields = [field for field in sorted(all_fields) 
                        if field not in ['copywriter_details', 'images', 'content']]
        
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=simple_fields)
            writer.writeheader()
            
            for item in data:
                row = {}
                for field in simple_fields:
                    value = item.get(field, '')
                    if isinstance(value, (list, dict)):
                        value = str(value)
                    row[field] = str(value)[:1000]  # 長すぎる値を制限
                writer.writerow(row)
    
    def run_complete_extraction(self):
        """完全抽出を実行"""
        print("🚀 TCC コピラ 完全データ抽出開始")
        print("=" * 60)
        
        # 状態復元
        resumed = self.load_state()
        if not resumed:
            self.start_time = datetime.now()
        
        try:
            # フェーズ1: 全URL抽出
            if not self.all_urls:
                success = self.extract_all_urls_comprehensive()
                if not success:
                    print("❌ URL抽出に失敗")
                    return
            
            print(f"✅ URL抽出完了: {len(self.all_urls):,}件")
            
            # フェーズ2: 詳細データ取得
            all_data = self.process_urls_parallel()
            
            # フェーズ3: バッチ統合
            if not all_data:
                all_data = self.consolidate_all_batches()
            
            # フェーズ4: 最終保存
            if all_data:
                files = self.save_final_complete_dataset(all_data)
                self.print_final_summary(all_data)
                print(f"🎉 全データ抽出完了! ファイル: {files[0]}")
            
        except KeyboardInterrupt:
            print("\n⚠️ ユーザーによる中断")
            self.save_state()
        except Exception as e:
            print(f"\n❌ 予期しないエラー: {e}")
            self.save_state()
        finally:
            self.save_state()
    
    def print_final_summary(self, data):
        """最終サマリーを表示"""
        elapsed = datetime.now() - self.start_time if self.start_time else timedelta(0)
        valid_data = [item for item in data if 'error' not in item]
        
        print(f"\n🎉 完全データ抽出完了!")
        print("=" * 60)
        print(f"📊 総取得件数: {len(data):,}")
        print(f"✅ 有効データ: {len(valid_data):,}")
        print(f"❌ エラー件数: {len(data) - len(valid_data):,}")
        print(f"📈 成功率: {len(valid_data)/len(data)*100:.1f}%")
        print(f"⏱️ 総所要時間: {elapsed}")
        if elapsed.total_seconds() > 0:
            print(f"🚀 平均速度: {len(data)/elapsed.total_seconds():.2f}件/秒")
        print("=" * 60)

def main():
    """メイン実行"""
    print("TCC コピラ 完全データクローラー v3.0")
    print("=" * 50)
    print("🎯 37,259件の完全取得を目指します")
    print("⚡ 高速・並列処理対応")
    print("🛡️ 堅牢性・復旧機能付き")
    print("🛑 Ctrl+C で安全に中断できます")
    print("")
    
    crawler = CompleteTCCCrawler(
        output_dir="tcc_complete_data",
        delay=0.3,  # 0.3秒間隔（高速化）
        max_workers=2  # 並列処理
    )
    
    crawler.run_complete_extraction()

if __name__ == "__main__":
    main()