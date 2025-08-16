import json
import csv
import pandas as pd
from datetime import datetime
import os

def export_to_csv(json_file, output_file):
    """JSONデータをCSVファイルに変換"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # データを平坦化
    flattened_data = []
    for item in data:
        row = {
            'id': item.get('id', ''),
            'title': item.get('title', ''),
            'client': item.get('client', ''),
            'media': item.get('media', ''),
            'year': item.get('year', ''),
            'detail_url': item.get('detail_url', ''),
            'copywriter_names': ', '.join([cw.get('name', '') for cw in item.get('copywriters', [])]),
            'copywriter_count': len(item.get('copywriters', [])),
            'has_copywriter_id': any(cw.get('id') for cw in item.get('copywriters', []))
        }
        flattened_data.append(row)
    
    # CSVに保存
    df = pd.DataFrame(flattened_data)
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"✅ CSVファイルを保存: {output_file}")
    return df

def export_to_excel(json_file, output_file):
    """JSONデータをExcelファイルに変換（複数シート）"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # メインデータシート
    main_data = []
    copywriter_data = []
    
    for item in data:
        # メインデータ
        main_row = {
            'ID': item.get('id', ''),
            'タイトル': item.get('title', ''),
            'クライアント': item.get('client', ''),
            '媒体': item.get('media', ''),
            '年度': item.get('year', ''),
            '詳細URL': item.get('detail_url', ''),
            'コピーライター数': len(item.get('copywriters', []))
        }
        main_data.append(main_row)
        
        # コピーライターデータ
        for cw in item.get('copywriters', []):
            cw_row = {
                '広告ID': item.get('id', ''),
                'タイトル': item.get('title', ''),
                'コピーライター名': cw.get('name', ''),
                'コピーライターID': cw.get('id', ''),
                'クライアント': item.get('client', ''),
                '媒体': item.get('media', ''),
                '年度': item.get('year', '')
            }
            copywriter_data.append(cw_row)
    
    # Excelファイルに保存
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        pd.DataFrame(main_data).to_excel(writer, sheet_name='広告データ', index=False)
        pd.DataFrame(copywriter_data).to_excel(writer, sheet_name='コピーライター', index=False)
        
        # 分析シートも追加
        media_analysis = pd.DataFrame(list(analyze_media(data).items()), columns=['媒体', '件数'])
        year_analysis = pd.DataFrame(list(analyze_years(data).items()), columns=['年度', '件数'])
        client_analysis = pd.DataFrame(list(analyze_clients(data).items()), columns=['クライアント', '件数'])
        
        media_analysis.to_excel(writer, sheet_name='媒体別分析', index=False)
        year_analysis.to_excel(writer, sheet_name='年度別分析', index=False)
        client_analysis.to_excel(writer, sheet_name='クライアント別分析', index=False)
    
    print(f"✅ Excelファイルを保存: {output_file}")

def analyze_media(data):
    """媒体別分析"""
    media_count = {}
    for item in data:
        media = item.get('media', 'Unknown')
        media_count[media] = media_count.get(media, 0) + 1
    return dict(sorted(media_count.items(), key=lambda x: x[1], reverse=True))

def analyze_years(data):
    """年度別分析"""
    year_count = {}
    for item in data:
        year = str(item.get('year', 'Unknown'))
        year_count[year] = year_count.get(year, 0) + 1
    return dict(sorted(year_count.items(), key=lambda x: x[0] if x[0] != 'Unknown' else '0', reverse=True))

def analyze_clients(data):
    """クライアント別分析"""
    client_count = {}
    for item in data:
        client = item.get('client', 'Unknown')
        client_count[client] = client_count.get(client, 0) + 1
    return dict(sorted(client_count.items(), key=lambda x: x[1], reverse=True))

def create_summary_files():
    """サマリーファイルを作成"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 最新のJSONファイルを探す
    json_files = [f for f in os.listdir('.') if f.startswith('tcc_data_') and f.endswith('.json')]
    if not json_files:
        print("❌ JSONファイルが見つかりません")
        return
    
    latest_json = max(json_files, key=os.path.getctime)
    print(f"📁 対象ファイル: {latest_json}")
    
    # 各形式でエクスポート
    base_name = f"tcc_export_{timestamp}"
    
    # CSV形式
    csv_file = f"{base_name}.csv"
    df = export_to_csv(latest_json, csv_file)
    
    # Excel形式
    excel_file = f"{base_name}.xlsx"
    export_to_excel(latest_json, excel_file)
    
    # テキスト形式のサマリー
    txt_file = f"{base_name}_summary.txt"
    create_text_summary(latest_json, txt_file, df)
    
    print(f"\n🎉 エクスポート完了!")
    print(f"📄 CSVファイル: {csv_file}")
    print(f"📊 Excelファイル: {excel_file}")
    print(f"📝 サマリーファイル: {txt_file}")

def create_text_summary(json_file, output_file, df):
    """テキスト形式のサマリーを作成"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    summary_lines = []
    summary_lines.append("=" * 60)
    summary_lines.append("TCC コピラ データ エクスポート サマリー")
    summary_lines.append("=" * 60)
    summary_lines.append(f"エクスポート日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
    summary_lines.append(f"データ件数: {len(data)}件")
    summary_lines.append("")
    
    # 基本統計
    summary_lines.append("📊 基本統計")
    summary_lines.append("-" * 30)
    summary_lines.append(f"ユニークなタイトル数: {df['title'].nunique()}")
    summary_lines.append(f"ユニークなクライアント数: {df['client'].nunique()}")
    summary_lines.append(f"総コピーライター数: {df['copywriter_count'].sum()}")
    summary_lines.append(f"ユニークなコピーライター数: {len(set(name.strip() for names in df['copywriter_names'] for name in names.split(',') if name.strip()))}")
    summary_lines.append("")
    
    # 媒体別統計
    summary_lines.append("📺 媒体別統計")
    summary_lines.append("-" * 30)
    media_counts = analyze_media(data)
    for media, count in media_counts.items():
        percentage = (count / len(data)) * 100
        summary_lines.append(f"{media:10s}: {count:3d}件 ({percentage:5.1f}%)")
    summary_lines.append("")
    
    # 年度別統計
    summary_lines.append("📅 年度別統計")
    summary_lines.append("-" * 30)
    year_counts = analyze_years(data)
    for year, count in year_counts.items():
        if year != 'Unknown':
            percentage = (count / len(data)) * 100
            summary_lines.append(f"{year}年: {count:3d}件 ({percentage:5.1f}%)")
    summary_lines.append("")
    
    # クライアント別統計（上位10）
    summary_lines.append("🏢 クライアント別統計（上位10）")
    summary_lines.append("-" * 30)
    client_counts = analyze_clients(data)
    for i, (client, count) in enumerate(list(client_counts.items())[:10], 1):
        if client != 'Unknown':
            summary_lines.append(f"{i:2d}. {client[:40]:40s}: {count:2d}件")
    summary_lines.append("")
    
    # データ品質チェック
    summary_lines.append("✅ データ品質チェック")
    summary_lines.append("-" * 30)
    summary_lines.append(f"タイトルあり: {(df['title'] != '').sum()}/{len(df)} ({(df['title'] != '').sum()/len(df)*100:.1f}%)")
    summary_lines.append(f"クライアントあり: {(df['client'] != '').sum()}/{len(df)} ({(df['client'] != '').sum()/len(df)*100:.1f}%)")
    summary_lines.append(f"コピーライターあり: {(df['copywriter_names'] != '').sum()}/{len(df)} ({(df['copywriter_names'] != '').sum()/len(df)*100:.1f}%)")
    summary_lines.append(f"媒体あり: {(df['media'] != '').sum()}/{len(df)} ({(df['media'] != '').sum()/len(df)*100:.1f}%)")
    summary_lines.append(f"年度あり: {(df['year'] != '').sum()}/{len(df)} ({(df['year'] != '').sum()/len(df)*100:.1f}%)")
    summary_lines.append("")
    
    summary_lines.append("=" * 60)
    summary_lines.append("エクスポート完了")
    summary_lines.append("=" * 60)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(summary_lines))
    
    print(f"✅ サマリーファイルを保存: {output_file}")

if __name__ == "__main__":
    print("TCC データ エクスポートツール")
    print("=" * 40)
    create_summary_files()