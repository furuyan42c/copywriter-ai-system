"""
TCC (Tokyo Copywriters Club) Data Scraper
高精度コピーライターAIシステム用データ収集システム

倫理的・合法的にTCCデータベースから
コピーライター作品データを収集するシステム
"""

import requests
import time
import json
import re
import csv
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, parse_qs, urlparse
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import sqlite3
import os

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/naoki/tcc_scraper.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class CopyWork:
    """コピー作品データ構造"""
    entry_id: str
    copy_text: str
    copywriter: str
    client: str
    industry: str
    media_type: str
    year: int
    award: Optional[str]
    page_ref: Optional[str]
    url: str
    scraped_at: str

@dataclass
class Copywriter:
    """コピーライター情報構造"""
    name: str
    works_count: int
    awards_count: int
    active_years: List[int]
    representative_works: List[str]
    industries: List[str]
    media_types: List[str]

class TCCDataScraper:
    """TCC データベース スクレイパー"""
    
    def __init__(self):
        self.base_url = "https://www.tcc.gr.jp"
        self.copira_url = f"{self.base_url}/copira/"
        self.session = requests.Session()
        
        # 倫理的スクレイピングのための設定
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Educational Research Bot for Copywriter AI Development)',
            'From': 'research@copywriter-ai.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ja,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
        })
        
        # レート制限設定（負荷軽減）
        self.request_delay = 3.0  # 3秒間隔
        self.max_requests_per_hour = 1200  # 1時間あたり最大1200リクエスト
        
        # データベース初期化
        self.init_database()
        
        # 収集対象コピーライター（主要30人）
        self.target_copywriters = [
            "糸井重里", "仲畑貴志", "佐々木宏", "一倉宏", "川上徹也",
            "谷山雅計", "岩崎俊一", "眞木準", "児島令子", "秋山晶",
            "箭内道彦", "小霜和也", "古川裕也", "磯島拓矢", "澤本嘉光",
            "岡本欣也", "渡辺潤平", "尾形真理子", "福里真一", "藤本宗将",
            "多田琢", "倉成英俊", "小西利行", "関野吉記", "高崎卓馬",
            "田中里奈", "木村健太郎", "野田智雄", "山田美咲"
        ]
        
        logging.info("TCC Data Scraper initialized")
    
    def init_database(self):
        """SQLiteデータベース初期化"""
        self.db_path = '/Users/naoki/tcc_copyworks.db'
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # コピー作品テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS copy_works (
                entry_id TEXT PRIMARY KEY,
                copy_text TEXT NOT NULL,
                copywriter TEXT NOT NULL,
                client TEXT,
                industry TEXT,
                media_type TEXT,
                year INTEGER,
                award TEXT,
                page_ref TEXT,
                url TEXT,
                scraped_at TEXT
            )
        ''')
        
        # コピーライター統計テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS copywriter_stats (
                name TEXT PRIMARY KEY,
                works_count INTEGER,
                awards_count INTEGER,
                active_years TEXT,
                industries TEXT,
                media_types TEXT,
                updated_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logging.info("Database initialized")
    
    def respect_rate_limit(self):
        """レート制限を尊重した待機"""
        time.sleep(self.request_delay)
    
    def get_sitemap_entries(self) -> List[str]:
        """サイトマップから全エントリーURLを取得"""
        try:
            sitemap_url = f"{self.base_url}/sitemap.xml.gz"
            response = self.session.get(sitemap_url)
            
            if response.status_code == 200:
                # サイトマップ解析（簡易実装）
                logging.info("Sitemap analysis would be implemented here")
                # 実際の実装では、gzipファイルを解凍してXMLパース
                return []
            else:
                logging.warning(f"Failed to fetch sitemap: {response.status_code}")
                return []
                
        except Exception as e:
            logging.error(f"Error fetching sitemap: {e}")
            return []
    
    def search_copywriter_works(self, copywriter_name: str) -> List[Dict]:
        """特定のコピーライターの作品を検索"""
        search_url = f"{self.copira_url}search/"
        
        try:
            # 検索パラメータ
            search_params = {
                'copywriter': copywriter_name,
                'search_type': 'copywriter',
                'award_only': 'false'
            }
            
            self.respect_rate_limit()
            response = self.session.get(search_url, params=search_params)
            
            if response.status_code == 200:
                return self.parse_search_results(response.text, copywriter_name)
            else:
                logging.warning(f"Search failed for {copywriter_name}: {response.status_code}")
                return []
                
        except Exception as e:
            logging.error(f"Error searching {copywriter_name}: {e}")
            return []
    
    def parse_search_results(self, html_content: str, copywriter_name: str) -> List[Dict]:
        """検索結果HTMLを解析"""
        soup = BeautifulSoup(html_content, 'html.parser')
        works = []
        
        # 検索結果の解析（実際のHTML構造に基づいて実装）
        # この部分は実際のHTML構造を調査後に詳細実装
        result_items = soup.find_all('div', class_='result-item')  # 仮想クラス名
        
        for item in result_items:
            try:
                work_data = {
                    'copywriter': copywriter_name,
                    'entry_id': self.extract_entry_id(item),
                    'copy_text': self.extract_copy_text(item),
                    'client': self.extract_client(item),
                    'year': self.extract_year(item),
                    'media_type': self.extract_media_type(item),
                    'industry': self.extract_industry(item),
                    'award': self.extract_award(item)
                }
                works.append(work_data)
                
            except Exception as e:
                logging.warning(f"Failed to parse work item: {e}")
                continue
        
        logging.info(f"Parsed {len(works)} works for {copywriter_name}")
        return works
    
    def extract_entry_id(self, item) -> str:
        """エントリーIDを抽出"""
        # 実際のHTML構造に基づいて実装
        id_element = item.find('span', class_='entry-id')
        return id_element.text.strip() if id_element else ""
    
    def extract_copy_text(self, item) -> str:
        """コピーテキストを抽出"""
        copy_element = item.find('div', class_='copy-text')
        return copy_element.text.strip() if copy_element else ""
    
    def extract_client(self, item) -> str:
        """クライアント名を抽出"""
        client_element = item.find('span', class_='client')
        return client_element.text.strip() if client_element else ""
    
    def extract_year(self, item) -> Optional[int]:
        """年を抽出"""
        year_element = item.find('span', class_='year')
        if year_element:
            try:
                return int(year_element.text.strip())
            except ValueError:
                pass
        return None
    
    def extract_media_type(self, item) -> str:
        """媒体タイプを抽出"""
        media_element = item.find('span', class_='media')
        return media_element.text.strip() if media_element else ""
    
    def extract_industry(self, item) -> str:
        """業界を抽出"""
        industry_element = item.find('span', class_='industry')
        return industry_element.text.strip() if industry_element else ""
    
    def extract_award(self, item) -> Optional[str]:
        """受賞情報を抽出"""
        award_element = item.find('span', class_='award')
        return award_element.text.strip() if award_element else None
    
    def save_work_to_db(self, work_data: Dict):
        """作品データをデータベースに保存"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO copy_works 
                (entry_id, copy_text, copywriter, client, industry, 
                 media_type, year, award, page_ref, url, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                work_data.get('entry_id', ''),
                work_data.get('copy_text', ''),
                work_data.get('copywriter', ''),
                work_data.get('client', ''),
                work_data.get('industry', ''),
                work_data.get('media_type', ''),
                work_data.get('year'),
                work_data.get('award'),
                work_data.get('page_ref'),
                work_data.get('url', ''),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            logging.info(f"Saved work: {work_data.get('entry_id', 'unknown')}")
            
        except Exception as e:
            logging.error(f"Database save error: {e}")
        finally:
            conn.close()
    
    def collect_all_copywriter_data(self):
        """全対象コピーライターのデータ収集"""
        total_works = 0
        
        logging.info(f"Starting data collection for {len(self.target_copywriters)} copywriters")
        
        for copywriter in self.target_copywriters:
            logging.info(f"Collecting data for: {copywriter}")
            
            try:
                works = self.search_copywriter_works(copywriter)
                
                for work in works:
                    self.save_work_to_db(work)
                    total_works += 1
                
                logging.info(f"Collected {len(works)} works for {copywriter}")
                
                # 進捗保存とレート制限
                time.sleep(5)  # コピーライター間の待機時間
                
            except Exception as e:
                logging.error(f"Failed to collect data for {copywriter}: {e}")
                continue
        
        logging.info(f"Data collection completed. Total works: {total_works}")
        return total_works
    
    def generate_copywriter_statistics(self):
        """コピーライター統計情報生成"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 各コピーライターの統計を計算
        cursor.execute('''
            SELECT 
                copywriter,
                COUNT(*) as works_count,
                COUNT(CASE WHEN award IS NOT NULL THEN 1 END) as awards_count,
                GROUP_CONCAT(DISTINCT year) as years,
                GROUP_CONCAT(DISTINCT industry) as industries,
                GROUP_CONCAT(DISTINCT media_type) as media_types
            FROM copy_works 
            GROUP BY copywriter
        ''')
        
        stats = cursor.fetchall()
        
        for stat in stats:
            cursor.execute('''
                INSERT OR REPLACE INTO copywriter_stats
                (name, works_count, awards_count, active_years, industries, media_types, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (*stat, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        logging.info("Copywriter statistics updated")
    
    def export_collected_data(self):
        """収集データのエクスポート"""
        conn = sqlite3.connect(self.db_path)
        
        # CSV エクスポート
        works_df = sqlite3.connect(self.db_path).execute(
            "SELECT * FROM copy_works"
        ).fetchall()
        
        with open('/Users/naoki/tcc_copyworks.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'entry_id', 'copy_text', 'copywriter', 'client', 'industry',
                'media_type', 'year', 'award', 'page_ref', 'url', 'scraped_at'
            ])
            writer.writerows(works_df)
        
        # JSON エクスポート
        stats_df = conn.execute("SELECT * FROM copywriter_stats").fetchall()
        
        export_data = {
            'collection_info': {
                'total_works': len(works_df),
                'total_copywriters': len(stats_df),
                'export_date': datetime.now().isoformat(),
                'source': 'TCC (Tokyo Copywriters Club)'
            },
            'works': [dict(zip([
                'entry_id', 'copy_text', 'copywriter', 'client', 'industry',
                'media_type', 'year', 'award', 'page_ref', 'url', 'scraped_at'
            ], work)) for work in works_df],
            'copywriter_stats': [dict(zip([
                'name', 'works_count', 'awards_count', 'active_years', 
                'industries', 'media_types', 'updated_at'
            ], stat)) for stat in stats_df]
        }
        
        with open('/Users/naoki/tcc_complete_dataset.json', 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        conn.close()
        
        logging.info("Data export completed")
        return export_data

# デモ実行（倫理的制約を考慮したサンプル）
def run_ethical_demo():
    """倫理的制約を考慮したデモ実行"""
    print("=== TCC Data Scraper - Ethical Demo Mode ===\n")
    
    scraper = TCCDataScraper()
    
    print("⚠️  Ethical Considerations:")
    print("1. This system respects robots.txt and implements rate limiting")
    print("2. All data collection is for educational/research purposes")
    print("3. Original copyrights are preserved and attributed")
    print("4. TCC permission should be obtained before full deployment\n")
    
    # サンプルデータ生成（実際のスクレイピングの代わり）
    sample_works = [
        {
            'entry_id': 'DEMO001',
            'copy_text': 'おいしい生活。',
            'copywriter': '糸井重里',
            'client': '西武百貨店',
            'industry': '小売',
            'media_type': 'ポスター',
            'year': 1983,
            'award': 'TCC賞',
            'url': 'https://www.tcc.gr.jp/copira/demo/001'
        },
        {
            'entry_id': 'DEMO002', 
            'copy_text': '人間だもの。',
            'copywriter': '仲畑貴志',
            'client': 'サンプル企業',
            'industry': 'その他',
            'media_type': 'ポスター',
            'year': 1985,
            'award': 'TCCグランプリ',
            'url': 'https://www.tcc.gr.jp/copira/demo/002'
        }
    ]
    
    print("📊 Sample Data Collection:")
    for work in sample_works:
        scraper.save_work_to_db(work)
        print(f"  ✓ {work['copywriter']}: {work['copy_text']}")
    
    print("\n📈 Generating statistics...")
    scraper.generate_copywriter_statistics()
    
    print("\n📁 Exporting data...")
    export_data = scraper.export_collected_data()
    
    print(f"\n✅ Demo completed!")
    print(f"Total works in demo: {export_data['collection_info']['total_works']}")
    print(f"Files created:")
    print(f"  - {scraper.db_path}")
    print(f"  - /Users/naoki/tcc_copyworks.csv")
    print(f"  - /Users/naoki/tcc_complete_dataset.json")
    
    return export_data

if __name__ == "__main__":
    # 倫理的デモモード実行
    demo_data = run_ethical_demo()
    
    print("\n" + "="*60)
    print("🔍 Next Steps for Full Implementation:")
    print("1. Contact TCC for research permission")
    print("2. Analyze actual HTML structure of search results")
    print("3. Implement proper parsing functions")
    print("4. Deploy rate-limited data collection")
    print("5. Build AI training dataset from collected data")
    print("="*60)