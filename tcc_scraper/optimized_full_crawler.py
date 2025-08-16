import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime, timedelta
import os
from urllib.parse import urljoin
import signal
import sys
import threading
from queue import Queue, Empty

class OptimizedTCCFullCrawler:
    def __init__(self, output_dir="tcc_complete_data", delay=0.5, batch_size=100):
        self.output_dir = output_dir
        self.delay = delay
        self.batch_size = batch_size
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
        self.current_phase = "準備中"
        self.phase_progress = 0
        
        # 出力ディレクトリを作成
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 中断処理
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # チェックポイントファイル
        self.checkpoint_file = os.path.join(self.output_dir, "crawl_checkpoint.json")
        self.urls_file = os.path.join(self.output_dir, "all_urls.json")
        self.progress_file = os.path.join(self.output_dir, "progress.json")
    
    def signal_handler(self, signum, frame):
        print(f"\n⚠️ 停止信号を受信。安全に終了中...")
        self.stop_crawling = True
    
    def save_progress(self):
        """進捗を保存"""
        progress_data = {
            'total_items': self.total_items,
            'processed_items': self.processed_items,
            'failed_items': self.failed_items,
            'current_phase': self.current_phase,
            'phase_progress': self.phase_progress,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'last_update': datetime.now().isoformat()
        }
        
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)
    
    def load_progress(self):
        """進捗を復元"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    progress_data = json.load(f)
                    self.total_items = progress_data.get('total_items', 0)
                    self.processed_items = progress_data.get('processed_items', 0)
                    self.failed_items = progress_data.get('failed_items', 0)
                    self.current_phase = progress_data.get('current_phase', '準備中')
                    self.phase_progress = progress_data.get('phase_progress', 0)
                    start_time_str = progress_data.get('start_time')
                    if start_time_str:
                        self.start_time = datetime.fromisoformat(start_time_str)
                print(f"📊 進捗を復元: {self.processed_items}/{self.total_items} 完了")
                return True
            except Exception as e:
                print(f"⚠️ 進捗復元エラー: {e}")
        return False
    
    def fetch_page_optimized(self, url, retries=2):
        """最適化されたページ取得"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=20)
                response.raise_for_status()
                return response.text
            except Exception as e:
                if attempt == retries - 1:
                    print(f"❌ 取得失敗: {url}")
                    return None
                time.sleep(1)
        return None
    
    def get_pagination_info(self):
        """ページネーション情報を正確に取得"""
        base_url = "https://www.tcc.gr.jp/copira/"
        params = {
            'copy': '',
            'copywriter': '',
            'ad': '',
            'biz': '',
            'media': '',
            'start': '1960',
            'end': '2025',
            'target_prize': 'all'
        }
        
        url = f"{base_url}?" + "&".join([f"{k}={v}" for k, v in params.items()])
        html = self.fetch_page_optimized(url)
        
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 総件数を取得
            result_text = soup.find(string=re.compile(r'\d+件が検索されました'))
            if result_text:
                match = re.search(r'(\d+)件が検索されました', result_text)
                if match:
                    self.total_items = int(match.group(1))
            
            # 実際のページネーション構造を確認
            # URLパターンを調査
            pagination_links = soup.find_all('a', href=True)
            page_urls = []
            
            for link in pagination_links:
                href = link.get('href', '')
                if 'page/' in href or 'p=' in href:
                    page_urls.append(href)
            
            # 最大ページ数を推定
            if page_urls:
                page_numbers = []
                for url in page_urls:
                    # page/123/ のパターン
                    match = re.search(r'page/(\d+)', url)
                    if match:
                        page_numbers.append(int(match.group(1)))
                    # p=123 のパターン
                    match = re.search(r'[?&]p=(\d+)', url)
                    if match:
                        page_numbers.append(int(match.group(1)))
                
                if page_numbers:
                    max_page = max(page_numbers)
                    return max_page
            
            # ページネーションが見つからない場合は件数から推定
            items_per_page = len(soup.find_all('tr')) - 1  # ヘッダー行を除く
            if items_per_page > 0:
                estimated_pages = (self.total_items + items_per_page - 1) // items_per_page
                return estimated_pages
        
        return 0
    
    def extract_all_urls_smart(self):
        """スマートな方法で全URLを抽出"""
        print("🔍 全データのURL抽出を開始...")
        self.current_phase = "URL抽出"
        
        # 既存のURLファイルをチェック
        if os.path.exists(self.urls_file):
            try:
                with open(self.urls_file, 'r', encoding='utf-8') as f:
                    existing_urls = json.load(f)
                if existing_urls:
                    print(f"📁 既存URLファイル発見: {len(existing_urls)}件")
                    return existing_urls
            except:
                pass
        
        all_urls = []
        max_pages = self.get_pagination_info()
        
        if max_pages == 0:
            print("❌ ページネーション情報の取得に失敗")
            return []
        
        print(f"📊 推定総件数: {self.total_items:,}件")
        print(f"📄 推定ページ数: {max_pages:,}ページ")
        
        base_url = "https://www.tcc.gr.jp/copira/"
        
        # 複数のURLパターンを試行
        url_patterns = [
            lambda p: f"{base_url}page/{p}/?copy=&copywriter=&ad=&biz=&media=&start=1960&end=2025&target_prize=all",
            lambda p: f"{base_url}?p={p}&copy=&copywriter=&ad=&biz=&media=&start=1960&end=2025&target_prize=all",
            lambda p: f"{base_url}?page={p}&copy=&copywriter=&ad=&biz=&media=&start=1960&end=2025&target_prize=all"
        ]
        
        for page_num in range(1, max_pages + 1):
            if self.stop_crawling:
                break
            
            print(f"\r📄 ページ {page_num:,}/{max_pages:,} 処理中... ", end='', flush=True)
            
            page_urls = []
            
            # 複数のURLパターンを試行
            for pattern in url_patterns:
                if page_urls:  # 成功したらループを抜ける
                    break
                
                url = pattern(page_num)
                html = self.fetch_page_optimized(url)
                
                if html:
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # 詳細ページのリンクを抽出
                    links = soup.find_all('a', href=True)
                    for link in links:
                        href = link.get('href', '')
                        if '/copira/id/' in href:
                            if not href.startswith('http'):
                                href = f"https://www.tcc.gr.jp{href}"
                            page_urls.append(href)
            
            if page_urls:
                all_urls.extend(page_urls)
                print(f"✅ {len(page_urls)}件", end='')
            else:
                print(f"❌ 0件", end='')
                # 連続で失敗する場合は早期終了
                if page_num > 10:  # 最初の10ページは確実に存在するはず
                    break
            
            # 進捗保存
            if page_num % 50 == 0:
                self.save_urls_checkpoint(all_urls, page_num)
                self.phase_progress = page_num / max_pages * 100
                self.save_progress()
            
            time.sleep(self.delay * 0.5)  # URL抽出は高速化
        
        print(f"\n✅ URL抽出完了: {len(all_urls)}件")
        
        # 重複除去
        unique_urls = list(set(all_urls))
        print(f"🔄 重複除去後: {len(unique_urls)}件")
        
        # URLを保存
        with open(self.urls_file, 'w', encoding='utf-8') as f:
            json.dump(unique_urls, f, ensure_ascii=False, indent=2)
        
        return unique_urls
    
    def save_urls_checkpoint(self, urls, page_num):
        """URL抽出のチェックポイント"""
        checkpoint_data = {
            'urls': urls,
            'last_page': page_num,
            'timestamp': datetime.now().isoformat()
        }
        checkpoint_file = os.path.join(self.output_dir, f"url_checkpoint_p{page_num}.json")
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
    
    def parse_detail_page_optimized(self, html_content, url):
        """最適化された詳細ページ解析"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            data = {
                'url': url,
                'scraped_at': datetime.now().isoformat()
            }
            
            # IDを抽出
            id_match = re.search(r'/id/(\d+)', url)
            if id_match:
                data['id'] = id_match.group(1)
            
            # メイン情報テーブル
            info_table = soup.find('table', class_='table1__table')
            if info_table:
                rows = info_table.find_all('tr')
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
                            '制作会社': 'production_company'
                        }
                        
                        normalized_key = key_mapping.get(key, key.lower().replace(' ', '_'))
                        data[normalized_key] = value
            
            # ページタイトル
            title_elem = soup.find('h1') or soup.find('title')
            if title_elem:
                data['title'] = title_elem.get_text(strip=True)
            
            # コピーライターリンク
            copywriter_links = soup.find_all('a', href=lambda x: x and '/copitan/' in x)
            if copywriter_links:
                data['copywriter_links'] = []
                for link in copywriter_links:
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
            return {'error': str(e), 'url': url}
    
    def crawl_details_batch(self, urls):
        """詳細データを効率的にバッチ取得"""
        print(f"\n📥 詳細データ取得開始: {len(urls):,}件")
        self.current_phase = "詳細データ取得"
        
        all_data = []
        
        for i, url in enumerate(urls, 1):
            if self.stop_crawling:
                break
            
            if i % 100 == 0 or i == 1:
                elapsed = datetime.now() - self.start_time if self.start_time else timedelta(0)
                rate = i / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0
                eta_seconds = (len(urls) - i) / rate if rate > 0 else 0
                eta = str(timedelta(seconds=int(eta_seconds)))
                
                print(f"📊 {i:,}/{len(urls):,} ({i/len(urls)*100:.1f}%) "
                      f"速度:{rate:.1f}件/秒 ETA:{eta}")
            
            html = self.fetch_page_optimized(url)
            if html:
                data = self.parse_detail_page_optimized(html, url)
                all_data.append(data)
                self.processed_items += 1
            else:
                self.failed_items += 1
            
            # バッチ保存
            if i % self.batch_size == 0:
                self.save_batch_data(all_data, i)
                self.phase_progress = i / len(urls) * 100
                self.save_progress()
            
            time.sleep(self.delay)
        
        return all_data
    
    def save_batch_data(self, data, batch_num):
        """バッチデータを保存"""
        batch_file = os.path.join(self.output_dir, f"batch_data_{batch_num:06d}.json")
        with open(batch_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 バッチ保存: {batch_file}")
    
    def consolidate_all_data(self):
        """全バッチデータを統合"""
        print("\n🔄 データ統合開始...")
        self.current_phase = "データ統合"
        
        all_data = []
        batch_files = [f for f in os.listdir(self.output_dir) if f.startswith('batch_data_')]
        batch_files.sort()
        
        for batch_file in batch_files:
            file_path = os.path.join(self.output_dir, batch_file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    batch_data = json.load(f)
                    all_data.extend(batch_data)
                print(f"📁 統合: {batch_file} ({len(batch_data)}件)")
            except Exception as e:
                print(f"❌ エラー: {batch_file} - {e}")
        
        return all_data
    
    def save_final_complete_data(self, data):
        """最終完全データを保存"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 完全JSONファイル
        json_file = os.path.join(self.output_dir, f"tcc_complete_data_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 統計CSVファイル
        csv_file = os.path.join(self.output_dir, f"tcc_complete_summary_{timestamp}.csv")
        self.create_summary_csv(data, csv_file)
        
        # 完全分析レポート
        analysis_file = os.path.join(self.output_dir, f"tcc_complete_analysis_{timestamp}.txt")
        self.create_complete_analysis(data, analysis_file)
        
        print(f"\n💾 最終データ保存完了:")
        print(f"  📋 完全JSON: {json_file}")
        print(f"  📊 統計CSV: {csv_file}")
        print(f"  📈 分析レポート: {analysis_file}")
        
        return json_file, csv_file, analysis_file
    
    def create_summary_csv(self, data, csv_file):
        """統計サマリーCSVを作成"""
        import csv
        
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = [
                'id', 'title', 'advertiser', 'award', 'industry', 'media_type',
                'publication_year', 'page_number', 'copywriter', 'agency',
                'production_company', 'copywriter_count', 'has_award',
                'url', 'has_error'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in data:
                copywriter_count = len(item.get('copywriter_links', []))
                
                row = {
                    'id': item.get('id', ''),
                    'title': item.get('title', ''),
                    'advertiser': item.get('advertiser', ''),
                    'award': item.get('award', ''),
                    'industry': item.get('industry', ''),
                    'media_type': item.get('media_type', ''),
                    'publication_year': item.get('publication_year', ''),
                    'page_number': item.get('page_number', ''),
                    'copywriter': item.get('copywriter', ''),
                    'agency': item.get('agency', ''),
                    'production_company': item.get('production_company', ''),
                    'copywriter_count': copywriter_count,
                    'has_award': 'Yes' if item.get('award') else 'No',
                    'url': item.get('url', ''),
                    'has_error': 'Yes' if 'error' in item else 'No'
                }
                writer.writerow(row)
    
    def create_complete_analysis(self, data, analysis_file):
        """完全分析レポートを作成"""
        valid_data = [item for item in data if 'error' not in item]
        
        lines = []
        lines.append("=" * 80)
        lines.append("TCC コピラ 完全データ分析レポート")
        lines.append("=" * 80)
        lines.append(f"作成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        lines.append(f"総データ件数: {len(data):,}件")
        lines.append(f"有効データ件数: {len(valid_data):,}件")
        lines.append(f"エラー件数: {len(data) - len(valid_data):,}件")
        lines.append("")
        
        # 年度別分析
        year_stats = {}
        for item in valid_data:
            year = item.get('publication_year', 'Unknown')
            year_stats[year] = year_stats.get(year, 0) + 1
        
        lines.append("📅 年度別統計 (上位20年):")
        lines.append("-" * 40)
        for year, count in sorted(year_stats.items(), key=lambda x: x[1], reverse=True)[:20]:
            if year != 'Unknown':
                lines.append(f"{year}年: {count:,}件")
        lines.append("")
        
        # 媒体別分析
        media_stats = {}
        for item in valid_data:
            media = item.get('media_type', 'Unknown')
            media_stats[media] = media_stats.get(media, 0) + 1
        
        lines.append("📺 媒体別統計:")
        lines.append("-" * 40)
        for media, count in sorted(media_stats.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(valid_data)) * 100
            lines.append(f"{media:15s}: {count:,}件 ({percentage:5.1f}%)")
        lines.append("")
        
        # 業種別分析
        industry_stats = {}
        for item in valid_data:
            industry = item.get('industry', 'Unknown')
            industry_stats[industry] = industry_stats.get(industry, 0) + 1
        
        lines.append("🏢 業種別統計 (上位20業種):")
        lines.append("-" * 40)
        for industry, count in sorted(industry_stats.items(), key=lambda x: x[1], reverse=True)[:20]:
            if industry != 'Unknown':
                lines.append(f"{industry:30s}: {count:,}件")
        lines.append("")
        
        # 受賞統計
        award_stats = {}
        for item in valid_data:
            award = item.get('award', 'None')
            if award and award != 'None':
                award_stats[award] = award_stats.get(award, 0) + 1
        
        lines.append("🏆 受賞統計:")
        lines.append("-" * 40)
        for award, count in sorted(award_stats.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"{award:30s}: {count:,}件")
        
        lines.append("\n" + "=" * 80)
        
        with open(analysis_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    
    def run_complete_crawl(self):
        """完全クローリングを実行"""
        print("🚀 TCC コピラ 完全データクローリング開始")
        print("=" * 60)
        
        # 進捗復元を試行
        resumed = self.load_progress()
        if not resumed:
            self.start_time = datetime.now()
        
        try:
            # フェーズ1: URL抽出
            if not os.path.exists(self.urls_file):
                urls = self.extract_all_urls_smart()
            else:
                with open(self.urls_file, 'r', encoding='utf-8') as f:
                    urls = json.load(f)
                print(f"📁 既存URLファイル使用: {len(urls)}件")
            
            if not urls:
                print("❌ URLの取得に失敗しました")
                return
            
            # フェーズ2: 詳細データ取得
            all_data = self.crawl_details_batch(urls)
            
            # フェーズ3: データ統合
            if len(all_data) == 0:
                all_data = self.consolidate_all_data()
            
            # フェーズ4: 最終保存
            if all_data:
                self.save_final_complete_data(all_data)
                self.print_final_summary(all_data)
            
        except KeyboardInterrupt:
            print("\n⚠️ ユーザーによる中断")
        except Exception as e:
            print(f"\n❌ 予期しないエラー: {e}")
        finally:
            self.save_progress()
    
    def print_final_summary(self, data):
        """最終サマリーを表示"""
        elapsed = datetime.now() - self.start_time if self.start_time else timedelta(0)
        valid_data = [item for item in data if 'error' not in item]
        
        print(f"\n🎉 完全クローリング完了!")
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
    """メイン実行関数"""
    print("TCC コピラ 完全データクローラー v2.0")
    print("=" * 50)
    print("⚠️ 37,259件の完全取得を開始します")
    print("⏱️ 推定所要時間: 5-8時間")
    print("🛑 Ctrl+C で安全に中断できます")
    print("")
    
    crawler = OptimizedTCCFullCrawler(
        output_dir="tcc_complete_data",
        delay=0.5,  # 0.5秒間隔
        batch_size=100
    )
    
    crawler.run_complete_crawl()

if __name__ == "__main__":
    main()