import requests
from bs4 import BeautifulSoup
import json
import time

def get_sample_data():
    """TCCコピラの最初のページからサンプルデータを取得"""
    url = "https://www.tcc.gr.jp/copira/?copy=&copywriter=&ad=&biz=&media=&start=1960&end=2025&target_prize=all"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    print("Fetching data from TCC Copira...")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        with open('tcc_page1.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Saved HTML to tcc_page1.html")
        
        # HTMLを解析
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # ページ内のテキストを確認
        print("\n=== Page Structure Analysis ===")
        
        # タイトルを確認
        title = soup.find('title')
        if title:
            print(f"Page title: {title.get_text()}")
        
        # 件数を確認
        count_text = soup.find(text=lambda x: x and '件が検索されました' in x)
        if count_text:
            print(f"Search result count: {count_text}")
        
        # テーブルを探す
        tables = soup.find_all('table')
        print(f"Found {len(tables)} table(s)")
        
        # リンクを探す
        links = soup.find_all('a', href=True)
        detail_links = [link for link in links if 'detail' in link.get('href', '').lower() or 'id=' in link.get('href', '')]
        print(f"Found {len(detail_links)} detail links")
        
        # サンプルとして最初の10個のリンクを表示
        if detail_links:
            print("\nSample detail links:")
            for i, link in enumerate(detail_links[:10], 1):
                print(f"  {i}. {link.get_text(strip=True)[:50]} - {link.get('href', '')[:50]}")
        
        return response.text
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    html_content = get_sample_data()
    
    if html_content:
        print("\n✅ Successfully fetched page content")
        print(f"HTML size: {len(html_content)} characters")
    else:
        print("\n❌ Failed to fetch page content")