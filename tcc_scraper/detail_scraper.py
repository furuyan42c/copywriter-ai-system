import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime
import os

def fetch_detail_page(detail_url):
    """詳細ページの完全なデータを取得"""
    if not detail_url.startswith('http'):
        detail_url = f"https://www.tcc.gr.jp{detail_url}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3'
    }
    
    try:
        response = requests.get(detail_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        detail_data = {}
        
        # ページタイトル
        title_elem = soup.find('h1')
        if title_elem:
            detail_data['page_title'] = title_elem.get_text(strip=True)
        
        # メタ情報のテーブルを探す
        info_table = soup.find('table', class_='table1__table')
        if info_table:
            rows = info_table.find_all('tr')
            for row in rows:
                th = row.find('th')
                td = row.find('td')
                if th and td:
                    key = th.get_text(strip=True).replace('：', '').replace(':', '')
                    value = td.get_text(strip=True)
                    
                    # キーを正規化
                    if '広告主' in key or 'クライアント' in key:
                        detail_data['advertiser'] = value
                    elif '受賞' in key:
                        detail_data['award'] = value
                    elif '業種' in key:
                        detail_data['industry'] = value
                    elif '媒体' in key:
                        detail_data['media_type'] = value
                    elif '掲載年度' in key:
                        detail_data['publication_year'] = value
                    elif '掲載ページ' in key:
                        detail_data['page_number'] = value
                    elif 'コピーライター' in key:
                        detail_data['copywriter'] = value
                    elif '広告会社' in key:
                        detail_data['agency'] = value
                    elif '制作会社' in key:
                        detail_data['production_company'] = value
                    elif 'ディレクター' in key:
                        detail_data['director'] = value
                    elif 'プロデューサー' in key:
                        detail_data['producer'] = value
                    else:
                        detail_data[key] = value
        
        # ページ全体のテキストからコピー内容を抽出
        page_text = soup.get_text(separator='\n', strip=True)
        detail_data['full_text'] = page_text
        
        # 特定のセクションを探す
        content_divs = soup.find_all(['div', 'section', 'article'])
        for div in content_divs:
            div_text = div.get_text(strip=True)
            if len(div_text) > 50 and 'コピー' in div_text:
                detail_data['copy_content'] = div_text
                break
        
        # コピーライターへのリンクを探す
        copywriter_links = soup.find_all('a', href=lambda x: x and '/copitan/' in x)
        if copywriter_links:
            detail_data['copywriter_links'] = []
            for link in copywriter_links:
                detail_data['copywriter_links'].append({
                    'name': link.get_text(strip=True),
                    'url': link.get('href', '')
                })
        
        # 画像があれば取得
        images = soup.find_all('img')
        if images:
            detail_data['images'] = []
            for img in images:
                src = img.get('src', '')
                alt = img.get('alt', '')
                if src and not src.startswith('data:') and 'icon' not in src.lower():
                    detail_data['images'].append({
                        'src': src,
                        'alt': alt
                    })
        
        detail_data['scraped_at'] = datetime.now().isoformat()
        detail_data['source_url'] = detail_url
        
        return detail_data
        
    except Exception as e:
        print(f"Error fetching detail page {detail_url}: {e}")
        return {'error': str(e), 'source_url': detail_url}

def enhance_basic_data_with_details(json_file, max_details=50):
    """基本データに詳細情報を追加"""
    with open(json_file, 'r', encoding='utf-8') as f:
        basic_data = json.load(f)
    
    enhanced_data = []
    
    print(f"詳細ページから情報を取得中... (最大{max_details}件)")
    print("=" * 60)
    
    count = 0
    for i, item in enumerate(basic_data, 1):
        if count >= max_details:
            break
        
        detail_url = item.get('detail_url', '')
        if detail_url:
            print(f"[{count+1:2d}/{max_details:2d}] {item.get('title', 'No title')[:50]:50s}")
            
            # 詳細情報を取得
            detail_info = fetch_detail_page(detail_url)
            
            # 基本データと詳細データを結合
            enhanced_item = item.copy()
            enhanced_item['detail_info'] = detail_info
            
            enhanced_data.append(enhanced_item)
            count += 1
            
            # サーバーに優しく
            time.sleep(1)
        else:
            # 詳細URLがない場合もデータに含める
            enhanced_data.append(item)
    
    return enhanced_data

def save_enhanced_data(enhanced_data, output_file):
    """拡張データを保存"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(enhanced_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 拡張データを保存: {output_file}")

def create_detailed_csv_export(enhanced_data, output_file):
    """詳細情報を含むCSVを作成"""
    import csv
    
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = [
            'id', 'title', 'client', 'media', 'year', 'copywriter_names',
            'advertiser', 'award', 'industry', 'media_type', 'publication_year',
            'page_number', 'agency', 'production_company', 'director', 'producer',
            'copy_content', 'detail_url', 'has_detail_info'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for item in enhanced_data:
            detail_info = item.get('detail_info', {})
            
            row = {
                'id': item.get('id', ''),
                'title': item.get('title', ''),
                'client': item.get('client', ''),
                'media': item.get('media', ''),
                'year': item.get('year', ''),
                'copywriter_names': ', '.join([cw.get('name', '') for cw in item.get('copywriters', [])]),
                'advertiser': detail_info.get('advertiser', ''),
                'award': detail_info.get('award', ''),
                'industry': detail_info.get('industry', ''),
                'media_type': detail_info.get('media_type', ''),
                'publication_year': detail_info.get('publication_year', ''),
                'page_number': detail_info.get('page_number', ''),
                'agency': detail_info.get('agency', ''),
                'production_company': detail_info.get('production_company', ''),
                'director': detail_info.get('director', ''),
                'producer': detail_info.get('producer', ''),
                'copy_content': detail_info.get('copy_content', '')[:500] if detail_info.get('copy_content') else '',  # 500文字まで
                'detail_url': item.get('detail_url', ''),
                'has_detail_info': 'Yes' if detail_info and 'error' not in detail_info else 'No'
            }
            writer.writerow(row)
    
    print(f"✅ 詳細CSVファイルを保存: {output_file}")

def create_analysis_report(enhanced_data, output_file):
    """拡張データの分析レポートを作成"""
    lines = []
    lines.append("=" * 80)
    lines.append("TCC コピラ 詳細データ分析レポート")
    lines.append("=" * 80)
    lines.append(f"作成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
    lines.append(f"総データ件数: {len(enhanced_data)}件")
    
    # 詳細情報の取得状況
    with_details = sum(1 for item in enhanced_data if item.get('detail_info') and 'error' not in item.get('detail_info', {}))
    lines.append(f"詳細情報取得成功: {with_details}件 ({with_details/len(enhanced_data)*100:.1f}%)")
    lines.append("")
    
    # 受賞情報の分析
    award_count = {}
    industry_count = {}
    agency_count = {}
    
    for item in enhanced_data:
        detail_info = item.get('detail_info', {})
        if detail_info and 'error' not in detail_info:
            # 受賞
            award = detail_info.get('award', '')
            if award:
                award_count[award] = award_count.get(award, 0) + 1
            
            # 業種
            industry = detail_info.get('industry', '')
            if industry:
                industry_count[industry] = industry_count.get(industry, 0) + 1
            
            # 広告会社
            agency = detail_info.get('agency', '')
            if agency:
                agency_count[agency] = agency_count.get(agency, 0) + 1
    
    # 受賞情報
    if award_count:
        lines.append("🏆 受賞情報:")
        lines.append("-" * 40)
        for award, count in sorted(award_count.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"{award:30s}: {count:2d}件")
        lines.append("")
    
    # 業種情報
    if industry_count:
        lines.append("🏢 業種別分析:")
        lines.append("-" * 40)
        for industry, count in sorted(industry_count.items(), key=lambda x: x[1], reverse=True)[:10]:
            lines.append(f"{industry:40s}: {count:2d}件")
        lines.append("")
    
    # 広告会社
    if agency_count:
        lines.append("🎬 広告会社別分析:")
        lines.append("-" * 40)
        for agency, count in sorted(agency_count.items(), key=lambda x: x[1], reverse=True)[:10]:
            lines.append(f"{agency:40s}: {count:2d}件")
        lines.append("")
    
    lines.append("=" * 80)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ 分析レポートを保存: {output_file}")

def main():
    """メイン処理"""
    print("TCC 詳細データ スクレイピング & エクスポートツール")
    print("=" * 60)
    
    # 最新のJSONファイルを探す
    json_files = [f for f in os.listdir('.') if f.startswith('tcc_data_') and f.endswith('.json')]
    if not json_files:
        print("❌ 基本データのJSONファイルが見つかりません")
        return
    
    latest_json = max(json_files, key=os.path.getctime)
    print(f"📁 基本データファイル: {latest_json}")
    
    # 詳細データを取得
    enhanced_data = enhance_basic_data_with_details(latest_json, max_details=20)  # 20件のサンプル
    
    if not enhanced_data:
        print("❌ 詳細データの取得に失敗しました")
        return
    
    # ファイル名のタイムスタンプ
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 拡張データを保存
    enhanced_json_file = f"tcc_enhanced_{timestamp}.json"
    save_enhanced_data(enhanced_data, enhanced_json_file)
    
    # 詳細CSVを作成
    detailed_csv_file = f"tcc_detailed_{timestamp}.csv"
    create_detailed_csv_export(enhanced_data, detailed_csv_file)
    
    # 分析レポートを作成
    analysis_file = f"tcc_detailed_analysis_{timestamp}.txt"
    create_analysis_report(enhanced_data, analysis_file)
    
    print(f"\n🎉 詳細データスクレイピング完了!")
    print(f"━" * 60)
    print(f"📋 拡張JSONファイル: {enhanced_json_file}")
    print(f"📊 詳細CSVファイル : {detailed_csv_file}")
    print(f"📈 分析レポート   : {analysis_file}")
    print(f"━" * 60)
    
    # ファイルサイズ情報
    for filename in [enhanced_json_file, detailed_csv_file, analysis_file]:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"📊 {filename}: {size:,} bytes")

if __name__ == "__main__":
    main()