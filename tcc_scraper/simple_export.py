import json
import csv
from datetime import datetime
import os

def export_to_csv(json_file, output_file):
    """JSONデータをCSVファイルに変換"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['id', 'title', 'client', 'media', 'year', 'detail_url', 'copywriter_names', 'copywriter_count']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for item in data:
            row = {
                'id': item.get('id', ''),
                'title': item.get('title', ''),
                'client': item.get('client', ''),
                'media': item.get('media', ''),
                'year': item.get('year', ''),
                'detail_url': item.get('detail_url', ''),
                'copywriter_names': ', '.join([cw.get('name', '') for cw in item.get('copywriters', [])]),
                'copywriter_count': len(item.get('copywriters', []))
            }
            writer.writerow(row)
    
    print(f"✅ CSVファイルを保存: {output_file}")
    return data

def create_detailed_text_export(json_file, output_file):
    """詳細なテキスト形式でエクスポート"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    lines = []
    lines.append("=" * 80)
    lines.append("TCC コピラ データ 詳細エクスポート")
    lines.append("=" * 80)
    lines.append(f"エクスポート日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
    lines.append(f"総データ件数: {len(data)}件")
    lines.append("")
    
    # データの詳細リスト
    lines.append("📋 データ詳細リスト")
    lines.append("-" * 80)
    
    for i, item in enumerate(data, 1):
        lines.append(f"\n[{i:3d}] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"ID: {item.get('id', 'N/A')}")
        lines.append(f"タイトル: {item.get('title', 'N/A')}")
        lines.append(f"クライアント: {item.get('client', 'N/A')}")
        lines.append(f"媒体: {item.get('media', 'N/A')}")
        lines.append(f"年度: {item.get('year', 'N/A')}")
        
        copywriters = item.get('copywriters', [])
        if copywriters:
            lines.append("コピーライター:")
            for j, cw in enumerate(copywriters, 1):
                cw_id = f" (ID: {cw.get('id')})" if cw.get('id') else ""
                lines.append(f"  {j}. {cw.get('name', 'N/A')}{cw_id}")
        else:
            lines.append("コピーライター: N/A")
        
        if item.get('detail_url'):
            lines.append(f"詳細URL: {item.get('detail_url')}")
    
    # 統計情報
    lines.append("\n\n" + "=" * 80)
    lines.append("📊 統計情報")
    lines.append("=" * 80)
    
    # 媒体別集計
    media_count = {}
    for item in data:
        media = item.get('media', 'Unknown')
        media_count[media] = media_count.get(media, 0) + 1
    
    lines.append("\n📺 媒体別集計:")
    lines.append("-" * 40)
    for media, count in sorted(media_count.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(data)) * 100
        lines.append(f"{media:15s}: {count:3d}件 ({percentage:5.1f}%)")
    
    # 年度別集計
    year_count = {}
    for item in data:
        year = str(item.get('year', 'Unknown'))
        year_count[year] = year_count.get(year, 0) + 1
    
    lines.append("\n📅 年度別集計:")
    lines.append("-" * 40)
    for year, count in sorted(year_count.items(), key=lambda x: x[0] if x[0] != 'Unknown' else '0', reverse=True):
        percentage = (count / len(data)) * 100
        lines.append(f"{year}年: {count:3d}件 ({percentage:5.1f}%)")
    
    # クライアント別集計
    client_count = {}
    for item in data:
        client = item.get('client', 'Unknown')
        client_count[client] = client_count.get(client, 0) + 1
    
    lines.append("\n🏢 クライアント別集計:")
    lines.append("-" * 40)
    for client, count in sorted(client_count.items(), key=lambda x: x[1], reverse=True):
        if client != 'Unknown':
            percentage = (count / len(data)) * 100
            lines.append(f"{client[:50]:50s}: {count:2d}件 ({percentage:4.1f}%)")
    
    # コピーライター別集計
    copywriter_count = {}
    for item in data:
        for cw in item.get('copywriters', []):
            name = cw.get('name', 'Unknown')
            copywriter_count[name] = copywriter_count.get(name, 0) + 1
    
    lines.append("\n✍️ コピーライター別集計:")
    lines.append("-" * 40)
    for copywriter, count in sorted(copywriter_count.items(), key=lambda x: x[1], reverse=True):
        if copywriter != 'Unknown':
            percentage = (count / len(data)) * 100
            lines.append(f"{copywriter[:30]:30s}: {count:2d}件 ({percentage:4.1f}%)")
    
    # データ品質チェック
    lines.append("\n✅ データ品質チェック:")
    lines.append("-" * 40)
    has_title = sum(1 for item in data if item.get('title'))
    has_client = sum(1 for item in data if item.get('client'))
    has_copywriter = sum(1 for item in data if item.get('copywriters'))
    has_media = sum(1 for item in data if item.get('media'))
    has_year = sum(1 for item in data if item.get('year'))
    
    lines.append(f"タイトルあり    : {has_title:3d}/{len(data)} ({has_title/len(data)*100:5.1f}%)")
    lines.append(f"クライアントあり : {has_client:3d}/{len(data)} ({has_client/len(data)*100:5.1f}%)")
    lines.append(f"コピーライターあり: {has_copywriter:3d}/{len(data)} ({has_copywriter/len(data)*100:5.1f}%)")
    lines.append(f"媒体あり       : {has_media:3d}/{len(data)} ({has_media/len(data)*100:5.1f}%)")
    lines.append(f"年度あり       : {has_year:3d}/{len(data)} ({has_year/len(data)*100:5.1f}%)")
    
    lines.append("\n" + "=" * 80)
    lines.append("エクスポート完了")
    lines.append("=" * 80)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ 詳細テキストファイルを保存: {output_file}")

def create_json_pretty_export(json_file, output_file):
    """整形されたJSONファイルを作成"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # より読みやすい形式で保存
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, sort_keys=True)
    
    print(f"✅ 整形JSONファイルを保存: {output_file}")

def create_copywriter_list(json_file, output_file):
    """コピーライターリストを作成"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    copywriter_info = {}
    
    for item in data:
        for cw in item.get('copywriters', []):
            name = cw.get('name', '')
            if name and name != 'Unknown':
                if name not in copywriter_info:
                    copywriter_info[name] = {
                        'name': name,
                        'id': cw.get('id'),
                        'works': [],
                        'clients': set(),
                        'media_types': set(),
                        'years': set()
                    }
                
                copywriter_info[name]['works'].append({
                    'title': item.get('title', ''),
                    'client': item.get('client', ''),
                    'media': item.get('media', ''),
                    'year': item.get('year', ''),
                    'id': item.get('id', '')
                })
                
                if item.get('client'):
                    copywriter_info[name]['clients'].add(item.get('client'))
                if item.get('media'):
                    copywriter_info[name]['media_types'].add(item.get('media'))
                if item.get('year'):
                    copywriter_info[name]['years'].add(str(item.get('year')))
    
    # コピーライターリストをCSVで保存
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['name', 'copywriter_id', 'works_count', 'clients', 'media_types', 'years', 'year_range']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for name, info in sorted(copywriter_info.items(), key=lambda x: len(x[1]['works']), reverse=True):
            years = sorted([y for y in info['years'] if y.isdigit()])
            year_range = f"{years[0]}-{years[-1]}" if len(years) > 1 else years[0] if years else ""
            
            row = {
                'name': name,
                'copywriter_id': info['id'] or '',
                'works_count': len(info['works']),
                'clients': ', '.join(sorted(info['clients'])),
                'media_types': ', '.join(sorted(info['media_types'])),
                'years': ', '.join(sorted(info['years'])),
                'year_range': year_range
            }
            writer.writerow(row)
    
    print(f"✅ コピーライターリストを保存: {output_file}")

def main():
    """メインエクスポート処理"""
    print("TCC データ エクスポートツール")
    print("=" * 50)
    
    # 最新のJSONファイルを探す
    json_files = [f for f in os.listdir('.') if f.startswith('tcc_data_') and f.endswith('.json')]
    if not json_files:
        print("❌ JSONファイルが見つかりません")
        return
    
    latest_json = max(json_files, key=os.path.getctime)
    print(f"📁 対象ファイル: {latest_json}")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_name = f"tcc_export_{timestamp}"
    
    print(f"\n🔄 エクスポート開始...")
    
    # 1. CSV形式
    csv_file = f"{base_name}.csv"
    export_to_csv(latest_json, csv_file)
    
    # 2. 詳細テキスト形式
    txt_file = f"{base_name}_detailed.txt"
    create_detailed_text_export(latest_json, txt_file)
    
    # 3. 整形JSON形式
    pretty_json_file = f"{base_name}_pretty.json"
    create_json_pretty_export(latest_json, pretty_json_file)
    
    # 4. コピーライターリスト
    copywriter_file = f"{base_name}_copywriters.csv"
    create_copywriter_list(latest_json, copywriter_file)
    
    print(f"\n🎉 エクスポート完了!")
    print(f"━" * 50)
    print(f"📄 CSVファイル         : {csv_file}")
    print(f"📝 詳細テキストファイル   : {txt_file}")
    print(f"📋 整形JSONファイル      : {pretty_json_file}")
    print(f"✍️ コピーライターリスト   : {copywriter_file}")
    print(f"━" * 50)
    
    # ファイルサイズ情報も表示
    for filename in [csv_file, txt_file, pretty_json_file, copywriter_file]:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"📊 {filename}: {size:,} bytes")

if __name__ == "__main__":
    main()