import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime

def fetch_page(page_num=1, items_per_page=20):
    """指定ページのHTMLを取得"""
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
    
    if page_num > 1:
        params['page'] = page_num
    
    # items_per_pageを設定
    params['limit'] = items_per_page
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3'
    }
    
    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching page {page_num}: {e}")
        return None

def parse_table_data(html_content):
    """HTMLテーブルからデータを抽出"""
    soup = BeautifulSoup(html_content, 'html.parser')
    entries = []
    
    # テーブルを探す
    table = soup.find('table', class_='table2__table')
    
    if table:
        tbody = table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            
            for row in rows:
                entry = {}
                
                # 年度
                year_th = row.find('th')
                if year_th:
                    year_text = year_th.get_text(strip=True)
                    # 「2023年」から「2023」を抽出
                    year_match = re.search(r'(\d{4})', year_text)
                    if year_match:
                        entry['year'] = int(year_match.group(1))
                
                # メインデータのtd
                main_td = row.find('td')
                if main_td:
                    # タイトル（リンク付き）
                    title_link = main_td.find('a')
                    if title_link:
                        entry['title'] = title_link.get_text(strip=True)
                        entry['detail_url'] = title_link.get('href', '')
                        
                        # IDを抽出
                        id_match = re.search(r'/id/(\d+)', entry['detail_url'])
                        if id_match:
                            entry['id'] = id_match.group(1)
                    
                    # クライアント名
                    client_p = main_td.find('p', class_='copira__client')
                    if client_p:
                        entry['client'] = client_p.get_text(strip=True)
                    
                    # コピーライター
                    copywriter_p = main_td.find('p', class_='copira__copywriter')
                    if copywriter_p:
                        # コピーライター名とリンクを処理
                        copywriters = []
                        
                        # リンク付きのコピーライター
                        for link in copywriter_p.find_all('a'):
                            name = link.get_text(strip=True)
                            copywriter_id = None
                            href = link.get('href', '')
                            id_match = re.search(r'/id/(\d+)', href)
                            if id_match:
                                copywriter_id = id_match.group(1)
                            copywriters.append({
                                'name': name,
                                'id': copywriter_id
                            })
                        
                        # リンクなしのテキストも取得
                        full_text = copywriter_p.get_text(strip=True)
                        # リンク付きの名前を除去して残りを取得
                        for cw in copywriters:
                            full_text = full_text.replace(cw['name'], '')
                        
                        # 残りの名前を追加
                        remaining_names = full_text.strip().split()
                        for name in remaining_names:
                            if name and name not in [cw['name'] for cw in copywriters]:
                                copywriters.append({
                                    'name': name,
                                    'id': None
                                })
                        
                        entry['copywriters'] = copywriters
                
                # 媒体
                media_td = row.find_all('td')
                if len(media_td) >= 2:
                    entry['media'] = media_td[-1].get_text(strip=True)
                
                if entry:
                    entries.append(entry)
    
    return entries

def fetch_detail_info(detail_url):
    """詳細ページから追加情報を取得"""
    if not detail_url.startswith('http'):
        detail_url = f"https://www.tcc.gr.jp{detail_url}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(detail_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        details = {}
        
        # 詳細情報を探す
        info_table = soup.find('table', class_='table1__table')
        if info_table:
            rows = info_table.find_all('tr')
            for row in rows:
                th = row.find('th')
                td = row.find('td')
                if th and td:
                    key = th.get_text(strip=True)
                    value = td.get_text(strip=True)
                    
                    if '受賞' in key:
                        details['award'] = value
                    elif '業種' in key:
                        details['industry'] = value
                    elif '掲載ページ' in key:
                        details['page_number'] = value
                    elif '広告会社' in key:
                        details['agency'] = value
                    elif '制作会社' in key:
                        details['production'] = value
        
        return details
    except Exception as e:
        print(f"Error fetching detail page: {e}")
        return {}

def scrape_tcc_data(max_items=100, fetch_details=False):
    """TCCコピラからデータをスクレイピング"""
    all_entries = []
    page = 1
    items_per_page = 20
    
    print(f"Starting to scrape {max_items} items from TCC Copira...")
    print("="*50)
    
    while len(all_entries) < max_items:
        print(f"\n📄 Fetching page {page}...")
        html = fetch_page(page, items_per_page)
        
        if not html:
            print(f"  ❌ Failed to fetch page {page}")
            break
        
        entries = parse_table_data(html)
        
        if not entries:
            print(f"  ⚠️ No entries found on page {page}")
            break
        
        print(f"  ✅ Found {len(entries)} entries")
        
        for i, entry in enumerate(entries, 1):
            if len(all_entries) >= max_items:
                break
            
            # 詳細情報を取得（オプション）
            if fetch_details and entry.get('detail_url'):
                print(f"    Fetching details for entry {i}...")
                details = fetch_detail_info(entry['detail_url'])
                entry.update(details)
                time.sleep(0.5)
            
            all_entries.append(entry)
            
            # 進捗表示
            copywriter_names = ', '.join([cw['name'] for cw in entry.get('copywriters', [])])
            print(f"  [{len(all_entries):3d}] {entry.get('year', '----')} | {entry.get('media', '---'):5s} | {entry.get('title', 'No title')[:40]:40s} | {copywriter_names[:30]}")
        
        page += 1
        time.sleep(1)  # サーバーに優しく
    
    return all_entries

def analyze_and_save_data(entries):
    """データを分析して保存"""
    # データを保存
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'tcc_data_{len(entries)}items_{timestamp}.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Saved {len(entries)} entries to {filename}")
    
    # 分析
    analysis = {
        'total_count': len(entries),
        'by_media': {},
        'by_year': {},
        'by_client': {},
        'top_copywriters': {},
        'data_completeness': {
            'has_title': 0,
            'has_client': 0,
            'has_copywriter': 0,
            'has_media': 0,
            'has_year': 0
        }
    }
    
    for entry in entries:
        # 媒体別
        media = entry.get('media', 'Unknown')
        analysis['by_media'][media] = analysis['by_media'].get(media, 0) + 1
        
        # 年度別
        year = str(entry.get('year', 'Unknown'))
        analysis['by_year'][year] = analysis['by_year'].get(year, 0) + 1
        
        # クライアント別
        client = entry.get('client', 'Unknown')
        analysis['by_client'][client] = analysis['by_client'].get(client, 0) + 1
        
        # コピーライター別
        for cw in entry.get('copywriters', []):
            name = cw.get('name', 'Unknown')
            analysis['top_copywriters'][name] = analysis['top_copywriters'].get(name, 0) + 1
        
        # データ完全性
        if entry.get('title'): analysis['data_completeness']['has_title'] += 1
        if entry.get('client'): analysis['data_completeness']['has_client'] += 1
        if entry.get('copywriters'): analysis['data_completeness']['has_copywriter'] += 1
        if entry.get('media'): analysis['data_completeness']['has_media'] += 1
        if entry.get('year'): analysis['data_completeness']['has_year'] += 1
    
    # 分析結果を表示
    print("\n" + "="*60)
    print("📊 データ分析結果")
    print("="*60)
    
    print(f"\n📈 基本統計:")
    print(f"  総件数: {analysis['total_count']}")
    
    print(f"\n✅ データ完全性:")
    for key, count in analysis['data_completeness'].items():
        percentage = (count / analysis['total_count'] * 100) if analysis['total_count'] > 0 else 0
        print(f"  {key}: {count}/{analysis['total_count']} ({percentage:.1f}%)")
    
    print(f"\n📺 媒体別集計:")
    for media, count in sorted(analysis['by_media'].items(), key=lambda x: x[1], reverse=True)[:10]:
        percentage = (count / analysis['total_count'] * 100)
        print(f"  {media:10s}: {count:3d}件 ({percentage:5.1f}%)")
    
    print(f"\n📅 年度別集計 (最新10年):")
    for year, count in sorted(analysis['by_year'].items(), key=lambda x: x[0], reverse=True)[:10]:
        if year != 'Unknown':
            percentage = (count / analysis['total_count'] * 100)
            print(f"  {year}年: {count:3d}件 ({percentage:5.1f}%)")
    
    print(f"\n🏢 クライアント別集計 (上位10社):")
    for client, count in sorted(analysis['by_client'].items(), key=lambda x: x[1], reverse=True)[:10]:
        if client != 'Unknown':
            print(f"  {client[:30]:30s}: {count:2d}件")
    
    print(f"\n✍️ コピーライター別集計 (上位10名):")
    for copywriter, count in sorted(analysis['top_copywriters'].items(), key=lambda x: x[1], reverse=True)[:10]:
        if copywriter != 'Unknown':
            print(f"  {copywriter:20s}: {count:2d}件")
    
    # 分析結果も保存
    analysis_filename = f'tcc_analysis_{timestamp}.json'
    with open(analysis_filename, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 分析結果を {analysis_filename} に保存しました")
    
    return analysis

def create_summary_report(entries, analysis):
    """まとめレポートを作成"""
    report = []
    report.append("# TCC コピラ データ分析レポート")
    report.append(f"\n生成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
    report.append(f"データ件数: {len(entries)}件\n")
    
    report.append("## 📊 データの概要\n")
    report.append("### 媒体別の分布")
    report.append("| 媒体 | 件数 | 割合 |")
    report.append("|------|------|------|")
    for media, count in sorted(analysis['by_media'].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / analysis['total_count'] * 100)
        report.append(f"| {media} | {count} | {percentage:.1f}% |")
    
    report.append("\n### 年度別トレンド（最新5年）")
    report.append("| 年度 | 件数 |")
    report.append("|------|------|")
    for year, count in sorted(analysis['by_year'].items(), key=lambda x: x[0], reverse=True)[:5]:
        if year != 'Unknown':
            report.append(f"| {year} | {count} |")
    
    report.append("\n## 💡 データまとめ方の提案\n")
    report.append("### 1. 媒体別アーカイブ")
    report.append("- **TVCM**: 映像表現とコピーの関係性を分析")
    report.append("- **WEB**: デジタル時代の新しいコピーライティング手法")
    report.append("- **ポスター**: ビジュアルとコピーの相乗効果")
    report.append("- **ラジオCM**: 音声のみで伝える技術")
    
    report.append("\n### 2. 時代別トレンド分析")
    report.append("- 年代ごとのコピーの特徴変化")
    report.append("- 社会情勢とコピーの関連性")
    report.append("- テクノロジーの進化による表現の変化")
    
    report.append("\n### 3. クライアント別ケーススタディ")
    report.append("- 長期的なブランディング戦略の分析")
    report.append("- 業種別のコピーライティング特性")
    
    report.append("\n### 4. コピーライター別作品集")
    report.append("- 個人のスタイルと進化の追跡")
    report.append("- 師弟関係やスクールの系譜")
    
    report.append("\n### 5. 受賞作品の特別コレクション")
    report.append("- TCC賞受賞作品の共通点分析")
    report.append("- 審査基準の変遷")
    
    # レポートを保存
    report_filename = f'tcc_summary_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"\n📝 サマリーレポートを {report_filename} に保存しました")
    
    return '\n'.join(report)

def main():
    """メイン処理"""
    # 100件のデータを取得（詳細情報なし、高速）
    entries = scrape_tcc_data(max_items=100, fetch_details=False)
    
    if entries:
        # データ分析と保存
        analysis = analyze_and_save_data(entries)
        
        # サマリーレポート作成
        report = create_summary_report(entries, analysis)
        
        print("\n" + "="*60)
        print("🎉 処理完了！")
        print("="*60)
        print(f"取得データ数: {len(entries)}件")
        print("保存ファイル:")
        print("  - JSONデータファイル")
        print("  - 分析結果ファイル")
        print("  - サマリーレポート（Markdown）")
        
    else:
        print("\n❌ データの取得に失敗しました")

if __name__ == "__main__":
    main()