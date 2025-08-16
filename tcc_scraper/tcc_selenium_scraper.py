import requests
from bs4 import BeautifulSoup
import json
import time
import re

def fetch_page_content(page_num=1):
    """特定のページのHTMLコンテンツを取得"""
    base_url = "https://www.tcc.gr.jp/copira/"
    
    # ページ番号付きのURLを構築
    if page_num == 1:
        url = f"{base_url}?copy=&copywriter=&ad=&biz=&media=&start=1960&end=2025&target_prize=all"
    else:
        url = f"{base_url}?copy=&copywriter=&ad=&biz=&media=&start=1960&end=2025&target_prize=all&page={page_num}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching page {page_num}: {e}")
        return None

def parse_entries(html_content):
    """HTMLから広告エントリーを抽出"""
    soup = BeautifulSoup(html_content, 'html.parser')
    entries = []
    
    # 検索結果のテーブルを探す
    table = soup.find('table', {'class': 'search-result'}) or soup.find('table')
    
    if table:
        # テーブル形式でデータが存在する場合
        rows = table.find_all('tr')[1:]  # ヘッダー行をスキップ
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 4:
                entry = {
                    'title': cols[0].get_text(strip=True),
                    'advertiser': cols[1].get_text(strip=True),
                    'copywriter': cols[2].get_text(strip=True),
                    'media': cols[3].get_text(strip=True) if len(cols) > 3 else '',
                }
                
                # 詳細リンクがあれば取得
                link = cols[0].find('a')
                if link:
                    entry['detail_url'] = link.get('href', '')
                
                entries.append(entry)
    else:
        # リスト形式でデータを探す
        # 複数のパターンを試す
        patterns = [
            ('div', {'class': 'result-item'}),
            ('div', {'class': 'entry'}),
            ('article', {}),
            ('li', {'class': 'item'}),
            ('div', {'class': 'work-item'}),
        ]
        
        for tag, attrs in patterns:
            items = soup.find_all(tag, attrs)
            if items:
                for item in items:
                    entry = extract_entry_data(item)
                    if entry and any(entry.values()):  # 少なくとも1つの値があれば追加
                        entries.append(entry)
                break
    
    # もしエントリーが見つからない場合、より汎用的な方法を試す
    if not entries:
        # すべてのリンクから広告データを探す
        links = soup.find_all('a', href=True)
        for link in links:
            if 'detail' in link.get('href', '') or 'id=' in link.get('href', ''):
                parent = link.parent
                if parent:
                    entry = extract_entry_data(parent)
                    if entry and entry.get('title'):
                        entries.append(entry)
    
    return entries

def extract_entry_data(element):
    """HTML要素から広告データを抽出"""
    entry = {}
    
    # タイトルを探す
    title_elem = element.find(['h2', 'h3', 'h4', 'a'])
    if title_elem:
        entry['title'] = title_elem.get_text(strip=True)
    
    # テキスト全体から情報を抽出
    text = element.get_text(separator=' ', strip=True)
    
    # パターンマッチングで情報を抽出
    patterns = {
        'advertiser': r'広告主[：:]\s*([^\s]+)',
        'copywriter': r'コピーライター[：:]\s*([^\s]+)',
        'media': r'媒体[：:]\s*([^\s]+)',
        'award': r'受賞[：:]\s*([^\s]+)',
        'year': r'(\d{4})年',
        'industry': r'業種[：:]\s*([^\s]+)',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            entry[key] = match.group(1)
    
    # メディアタイプを特定
    media_types = ['TVCM', 'ラジオCM', 'ポスター', 'WEB', '新聞', '雑誌', 'OOH']
    for media in media_types:
        if media in text:
            entry['media'] = media
            break
    
    return entry

def fetch_detail_page(detail_url):
    """詳細ページから追加情報を取得"""
    if not detail_url or not detail_url.startswith('http'):
        if detail_url and detail_url.startswith('/'):
            detail_url = f"https://www.tcc.gr.jp{detail_url}"
        else:
            return {}
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(detail_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        details = {}
        
        # 詳細ページから情報を抽出
        text = soup.get_text(separator=' ', strip=True)
        
        # 追加のパターンマッチング
        patterns = {
            'campaign': r'キャンペーン[：:]\s*([^、。\n]+)',
            'agency': r'広告会社[：:]\s*([^、。\n]+)',
            'production': r'制作会社[：:]\s*([^、。\n]+)',
            'director': r'ディレクター[：:]\s*([^、。\n]+)',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                details[key] = match.group(1)
        
        return details
    except Exception as e:
        print(f"Error fetching detail page: {e}")
        return {}

def scrape_tcc_copira(max_items=100, fetch_details=False):
    """TCCコピラから広告データをスクレイピング"""
    all_entries = []
    page = 1
    items_per_page = 20  # 推定値
    
    print(f"Starting to scrape {max_items} items from TCC Copira...")
    
    while len(all_entries) < max_items:
        print(f"\nFetching page {page}...")
        html_content = fetch_page_content(page)
        
        if not html_content:
            print(f"Failed to fetch page {page}")
            break
        
        entries = parse_entries(html_content)
        
        if not entries:
            print(f"No entries found on page {page}")
            # 次のページを試す
            if page < 10:  # 最初の10ページは試す
                page += 1
                continue
            else:
                break
        
        print(f"Found {len(entries)} entries on page {page}")
        
        for entry in entries:
            if len(all_entries) >= max_items:
                break
            
            # 詳細ページから追加情報を取得（オプション）
            if fetch_details and entry.get('detail_url'):
                details = fetch_detail_page(entry['detail_url'])
                entry.update(details)
                time.sleep(0.5)  # サーバーに優しく
            
            all_entries.append(entry)
            print(f"  [{len(all_entries)}] {entry.get('title', 'No title')} - {entry.get('media', 'Unknown media')}")
        
        page += 1
        time.sleep(1)  # ページ間で待機
    
    return all_entries

def analyze_data(entries):
    """スクレイピングしたデータを分析"""
    analysis = {
        'total_count': len(entries),
        'by_media': {},
        'by_year': {},
        'by_advertiser': {},
        'by_copywriter': {},
        'has_title': 0,
        'has_advertiser': 0,
        'has_copywriter': 0,
        'has_media': 0,
    }
    
    for entry in entries:
        # メディア別集計
        media = entry.get('media', 'Unknown')
        analysis['by_media'][media] = analysis['by_media'].get(media, 0) + 1
        
        # 年度別集計
        year = entry.get('year', 'Unknown')
        analysis['by_year'][year] = analysis['by_year'].get(year, 0) + 1
        
        # 広告主別集計
        advertiser = entry.get('advertiser', 'Unknown')
        analysis['by_advertiser'][advertiser] = analysis['by_advertiser'].get(advertiser, 0) + 1
        
        # コピーライター別集計
        copywriter = entry.get('copywriter', 'Unknown')
        analysis['by_copywriter'][copywriter] = analysis['by_copywriter'].get(copywriter, 0) + 1
        
        # データ完全性チェック
        if entry.get('title'):
            analysis['has_title'] += 1
        if entry.get('advertiser'):
            analysis['has_advertiser'] += 1
        if entry.get('copywriter'):
            analysis['has_copywriter'] += 1
        if entry.get('media'):
            analysis['has_media'] += 1
    
    return analysis

def main():
    # 100件のデータをスクレイピング
    entries = scrape_tcc_copira(max_items=100, fetch_details=False)
    
    if entries:
        # データを保存
        with open('tcc_data_100.json', 'w', encoding='utf-8') as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Saved {len(entries)} entries to tcc_data_100.json")
        
        # データ分析
        analysis = analyze_data(entries)
        
        # 分析結果を表示
        print("\n" + "="*50)
        print("📊 データ分析結果")
        print("="*50)
        print(f"総件数: {analysis['total_count']}")
        
        print(f"\n📝 データ完全性:")
        print(f"  タイトルあり: {analysis['has_title']}/{analysis['total_count']} ({analysis['has_title']/analysis['total_count']*100:.1f}%)")
        print(f"  広告主あり: {analysis['has_advertiser']}/{analysis['total_count']} ({analysis['has_advertiser']/analysis['total_count']*100:.1f}%)")
        print(f"  コピーライターあり: {analysis['has_copywriter']}/{analysis['total_count']} ({analysis['has_copywriter']/analysis['total_count']*100:.1f}%)")
        print(f"  媒体あり: {analysis['has_media']}/{analysis['total_count']} ({analysis['has_media']/analysis['total_count']*100:.1f}%)")
        
        print(f"\n📺 媒体別集計 (上位10):")
        for media, count in sorted(analysis['by_media'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {media}: {count}件")
        
        print(f"\n📅 年度別集計 (上位10):")
        for year, count in sorted(analysis['by_year'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {year}: {count}件")
        
        print(f"\n🏢 広告主別集計 (上位10):")
        for advertiser, count in sorted(analysis['by_advertiser'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {advertiser}: {count}件")
        
        print(f"\n✍️ コピーライター別集計 (上位10):")
        for copywriter, count in sorted(analysis['by_copywriter'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {copywriter}: {count}件")
        
        # 分析結果も保存
        with open('tcc_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 分析結果を tcc_analysis.json に保存しました")
        
    else:
        print("❌ データの取得に失敗しました")

if __name__ == "__main__":
    main()