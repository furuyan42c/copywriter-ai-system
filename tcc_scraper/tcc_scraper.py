import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin

def scrape_tcc_copira(max_items=100):
    base_url = "https://www.tcc.gr.jp/copira/"
    items = []
    page = 1
    items_per_page = 20
    
    while len(items) < max_items:
        # URLパラメータを構築
        params = {
            'copy': '',
            'copywriter': '',
            'ad': '',
            'biz': '',
            'media': '',
            'start': '1960',
            'end': '2025',
            'target_prize': 'all',
            'page': page,
            'limit': items_per_page
        }
        
        # URLを構築
        url = base_url + '?'
        url += '&'.join([f"{k}={v}" for k, v in params.items()])
        
        print(f"Fetching page {page}: {url}")
        
        try:
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 各広告エントリーを探す
            # ページ構造に基づいて適切なセレクタを使用
            entries = soup.find_all('div', class_='entry') or soup.find_all('article') or soup.find_all('li', class_='item')
            
            if not entries:
                # より汎用的な方法で探す
                entries = soup.find_all(['div', 'article', 'li'], recursive=True)
                entries = [e for e in entries if 'copira' in str(e).lower() or 'tcc' in str(e).lower()][:items_per_page]
            
            if not entries:
                print(f"No entries found on page {page}")
                break
            
            for entry in entries:
                if len(items) >= max_items:
                    break
                
                item = {}
                
                # テキストから情報を抽出
                text = entry.get_text(separator='\n', strip=True)
                lines = text.split('\n')
                
                # 基本的な情報を抽出
                for line in lines:
                    if '広告主' in line:
                        item['advertiser'] = line.replace('広告主', '').strip()
                    elif '受賞' in line:
                        item['award'] = line.replace('受賞', '').strip()
                    elif '業種' in line:
                        item['industry'] = line.replace('業種', '').strip()
                    elif '媒体' in line or 'TVCM' in line or 'ラジオ' in line or 'ポスター' in line:
                        if 'media' not in item:
                            item['media'] = line.replace('媒体', '').strip()
                    elif 'コピーライター' in line:
                        item['copywriter'] = line.replace('コピーライター', '').strip()
                    elif '年度' in line or '年' in line:
                        item['year'] = line.replace('掲載年度', '').replace('年度', '').replace('年', '').strip()
                
                # タイトル/キャンペーン名を探す
                title_elem = entry.find('a') or entry.find('h3') or entry.find('h4')
                if title_elem:
                    item['title'] = title_elem.get_text(strip=True)
                
                if item:
                    items.append(item)
                    print(f"Scraped item {len(items)}: {item.get('title', 'Unknown')}")
            
            page += 1
            time.sleep(1)  # Be respectful to the server
            
        except Exception as e:
            print(f"Error on page {page}: {e}")
            break
    
    return items

def save_data(items, filename='tcc_data.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(items)} items to {filename}")

if __name__ == "__main__":
    print("Starting TCC Copira scraping...")
    scraped_items = scrape_tcc_copira(max_items=100)
    
    if scraped_items:
        save_data(scraped_items)
        
        # 統計情報を表示
        print(f"\n=== Scraping Summary ===")
        print(f"Total items scraped: {len(scraped_items)}")
        
        # 媒体別の集計
        media_count = {}
        for item in scraped_items:
            media = item.get('media', 'Unknown')
            media_count[media] = media_count.get(media, 0) + 1
        
        print("\nBy Media Type:")
        for media, count in sorted(media_count.items(), key=lambda x: x[1], reverse=True):
            print(f"  {media}: {count}")
        
        # 年度別の集計
        year_count = {}
        for item in scraped_items:
            year = item.get('year', 'Unknown')
            year_count[year] = year_count.get(year, 0) + 1
        
        print("\nBy Year:")
        for year, count in sorted(year_count.items(), key=lambda x: x[0] if x[0] != 'Unknown' else '0'):
            print(f"  {year}: {count}")
    else:
        print("No items were scraped.")