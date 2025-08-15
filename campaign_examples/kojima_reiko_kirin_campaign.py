"""
児島令子スタイル キリンビール広告制作システム
Kojima Reiko Style Kirin Beer Advertisement Creation System

児島令子のコピーライティングスタイルを再現し、
キリンビールの広告を制作するシステム
"""

from dataclasses import dataclass
from typing import List, Dict
import json
from datetime import datetime

@dataclass
class KirinaAdvertisementCampaign:
    """キリンビール広告キャンペーンデータ"""
    headline: str
    subheadline: str
    body_copy: str
    visual_concept: str
    target_audience: str
    media_placement: List[str]
    brand_message: str
    style_analysis: Dict[str, str]

class KojimaReikoStyleGenerator:
    """児島令子スタイル コピー生成システム"""
    
    def __init__(self):
        self.kojima_profile = {
            "name": "児島令子",
            "birth_year": 1956,
            "background": "大阪府出身。京都女子大学卒業。女性ならではの視点で多くの名作を生み出す。",
            "famous_works": [
                "earth music&ecology「明日、何を着て生きていく？」",
                "トヨタヴィッツ「Vitz loves people」", 
                "資生堂「美しさは、仕事だ。」",
                "ユニクロ「着る人を選ばない服」"
            ],
            "style_characteristics": [
                "女性の心に響く繊細で洗練された表現",
                "ライフスタイルを提案する視点",
                "等身大の女性の気持ちを代弁",
                "上品で知性的な印象",
                "共感を重視したコピー"
            ],
            "philosophy": "女性の気持ちを理解することが良いコピーの基本",
            "target_specialty": "女性向けマーケティング、ファッション・美容広告、ライフスタイル提案"
        }
        
        self.kirin_brand_attributes = {
            "heritage": "創業150年の伝統と信頼",
            "quality": "一番搾り製法による高品質",
            "taste": "麦のうまみ、雑味のないクリアな味わい",
            "positioning": "上質な大人のビール",
            "target": "品質を重視する大人の消費者"
        }
    
    def create_kojima_style_campaign(self) -> KirinaAdvertisementCampaign:
        """児島令子スタイルのキリンビール広告キャンペーンを作成"""
        
        # 児島令子スタイルの特徴を反映したコピー作成
        headline = "今日という日に、ひとつの贅沢を。"
        
        subheadline = "一番搾りの澄んだ味わいが、あなたの時間を特別なものに変える。"
        
        body_copy = """
仕事を終えて帰る道すがら、ふと空を見上げる。
今日もいろんなことがあった。
頑張った自分に、小さなご褒美を。

キリン一番搾りは、麦芽100%の一番搾り麦汁だけを使用。
雑味のないクリアな味わいが、あなたの一日の疲れを優しく包み込みます。

創業150年、私たちが守り続けてきた品質へのこだわり。
それは、毎日を大切に生きる大人の女性のためのビールです。

今夜は、自分だけの時間を。
一番搾りと共に。
        """.strip()
        
        visual_concept = """
【メインビジュアル】
・30代後半の知的で上品な女性が、夕暮れのテラスで一人静かにビールを味わっている
・グラスに注がれた黄金色のビール、美しい泡立ち
・背景は都市の夕景、温かみのあるライティング
・女性の表情は満足感と充実感に満ちている

【カラートーン】
・ゴールデンアワーの温かい光
・キリンビールの黄金色を基調とした上品な配色
・落ち着いたトーンで上質感を演出

【レイアウト】
・ビジュアル60%、コピー40%の配分
・余白を活かした洗練されたデザイン
・キリンロゴは控えめに、品格を保持
        """
        
        style_analysis = {
            "headline_analysis": "『今日という日に、ひとつの贅沢を。』- 日常への感謝と自分へのご褒美を表現。児島令子らしい女性の心理に寄り添う言葉選び。",
            "emotional_appeal": "働く女性の日常の疲れと充実感を丁寧に描写。『頑張った自分に』という表現で自己肯定感を後押し。",
            "lifestyle_proposal": "単なる商品訴求ではなく、『自分だけの時間』という価値あるライフスタイルを提案。",
            "feminine_perspective": "『ふと空を見上げる』『優しく包み込む』など、女性らしい繊細な感性を表現。",
            "quality_positioning": "一番搾り製法と150年の歴史を、押し付けがましくなく自然に織り込み、品質への信頼感を醸成。"
        }
        
        return KirinaAdvertisementCampaign(
            headline=headline,
            subheadline=subheadline,
            body_copy=body_copy,
            visual_concept=visual_concept,
            target_audience="30-45歳の働く女性（会社員、専門職、主婦層を含む上質志向の女性）",
            media_placement=[
                "女性誌見開き（MORE、VERY、Oggi、Domani）",
                "駅構内プレミアムポスター（丸の内、表参道、自由が丘）", 
                "百貨店内デジタルサイネージ",
                "高級住宅街の駅周辺屋外広告",
                "女性向けWebメディア（ELLE、VOGUE、Harper's BAZAAR）"
            ],
            brand_message="キリン一番搾りは、品質を大切にする大人の女性の日常に寄り添う、上質なビールです。",
            style_analysis=style_analysis
        )
    
    def create_additional_variations(self) -> List[str]:
        """児島令子スタイルの追加ヘッドラインバリエーション"""
        
        return [
            "働く私の、小さな贅沢時間。",
            "今日を頑張った自分に、澄んだ一杯を。", 
            "いつもの夕暮れが、特別になる瞬間。",
            "私らしい時間の過ごし方。",
            "品質という名の、やさしさ。",
            "明日への力を、一番搾りと共に。",
            "日常に隠れた、上質なひととき。",
            "自分を大切にする時間、始まります。"
        ]
    
    def analyze_kojima_style_elements(self) -> Dict[str, List[str]]:
        """児島令子スタイルの要素分析"""
        
        return {
            "言葉選びの特徴": [
                "『ひとつの贅沢』- 控えめで上品な表現",
                "『優しく包み込む』- 母性的で温かい言葉",
                "『自分だけの時間』- 女性の心理に寄り添う表現",
                "『今日という日に』- 日常への感謝と肯定"
            ],
            "感情への訴求": [
                "自己肯定感の向上（頑張った自分への評価）",
                "罪悪感の解消（小さな贅沢への許可）", 
                "充実感の提供（特別な時間の創出）",
                "安心感の醸成（品質への信頼）"
            ],
            "ライフスタイル提案": [
                "忙しい日常の中での息抜き時間",
                "自分を大切にするセルフケア",
                "品質にこだわる上質な選択",
                "一人の時間を楽しむ大人の女性像"
            ],
            "ブランド統合": [
                "商品特徴を押し付けがましくなく表現",
                "歴史と品質を自然に織り込み",
                "女性の日常体験とブランド価値を統合",
                "感情的価値と機能的価値のバランス"
            ]
        }

def create_campaign_presentation():
    """キャンペーンプレゼンテーション資料作成"""
    
    generator = KojimaReikoStyleGenerator()
    campaign = generator.create_kojima_style_campaign()
    variations = generator.create_additional_variations()
    style_elements = generator.analyze_kojima_style_elements()
    
    presentation_data = {
        "campaign_overview": {
            "title": "キリン一番搾り 女性向けプレミアムキャンペーン",
            "subtitle": "児島令子スタイルによる上質なライフスタイル提案",
            "copywriter_style": "児島令子",
            "client": "キリンビール株式会社",
            "product": "キリン一番搾り生ビール",
            "created_date": datetime.now().isoformat()
        },
        "main_campaign": {
            "headline": campaign.headline,
            "subheadline": campaign.subheadline,
            "body_copy": campaign.body_copy,
            "visual_concept": campaign.visual_concept,
            "target_audience": campaign.target_audience,
            "media_placement": campaign.media_placement,
            "brand_message": campaign.brand_message
        },
        "style_analysis": campaign.style_analysis,
        "additional_variations": variations,
        "kojima_style_elements": style_elements,
        "expected_results": {
            "brand_perception": "上品で品質にこだわる大人のビールブランドとして認知向上",
            "target_engagement": "働く女性層との感情的結びつき強化",
            "differentiation": "男性中心の従来ビール広告から差別化",
            "sales_impact": "女性消費者の購買意欲向上、プレミアム価格の受容性向上"
        },
        "media_strategy": {
            "primary_media": "女性誌（MORE、VERY、Oggi）見開き広告",
            "secondary_media": "プレミアム立地でのポスター展開",
            "digital_extension": "女性向けWebメディアでの展開",
            "timeline": "6ヶ月間の継続キャンペーン"
        }
    }
    
    return presentation_data

# メイン実行
if __name__ == "__main__":
    print("=== 児島令子スタイル キリンビール広告制作システム ===\n")
    
    # キャンペーン生成
    presentation = create_campaign_presentation()
    
    # 結果表示
    print("【最終成果物】")
    print("=" * 60)
    
    print(f"\n🎯 キャンペーンタイトル")
    print(f"{presentation['campaign_overview']['title']}")
    print(f"{presentation['campaign_overview']['subtitle']}")
    
    print(f"\n✨ メインコピー")
    print(f"ヘッドライン: {presentation['main_campaign']['headline']}")
    print(f"サブヘッドライン: {presentation['main_campaign']['subheadline']}")
    
    print(f"\n📝 ボディコピー:")
    print(presentation['main_campaign']['body_copy'])
    
    print(f"\n🎨 ビジュアルコンセプト:")
    print(presentation['main_campaign']['visual_concept'])
    
    print(f"\n📊 ターゲット:")
    print(presentation['main_campaign']['target_audience'])
    
    print(f"\n📺 メディア展開:")
    for media in presentation['main_campaign']['media_placement']:
        print(f"  - {media}")
    
    print(f"\n🔍 児島令子スタイル分析:")
    for aspect, analysis in presentation['style_analysis'].items():
        print(f"  {aspect}: {analysis}")
    
    print(f"\n💡 追加ヘッドラインバリエーション:")
    for i, variation in enumerate(presentation['additional_variations'], 1):
        print(f"  {i}. {variation}")
    
    # JSONファイル出力
    with open('/Users/naoki/kojima_reiko_kirin_campaign.json', 'w', encoding='utf-8') as f:
        json.dump(presentation, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ キャンペーン制作完了")
    print("📁 kojima_reiko_kirin_campaign.json に詳細データ保存")
    print("\n" + "=" * 60)
    print("🏆 児島令子スタイルによるキリンビール広告キャンペーン完成！")