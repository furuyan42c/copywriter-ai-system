"""
Coca-Cola Campaign Generator using David Ogilvy's Style
David Ogilvyスタイルを活用したコカ・コーラキャンペーン企画ジェネレーター
"""

import asyncio
import json
from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime

@dataclass 
class PosterCampaign:
    """ポスター広告キャンペーンのデータ構造"""
    headline: str
    subheadline: str
    body_copy: str
    visual_concept: str
    call_to_action: str
    target_audience: str
    placement_strategy: List[str]
    design_elements: Dict[str, str]

@dataclass
class VideoCampaign:
    """動画広告キャンペーンのデータ構造"""
    title: str
    concept: str
    script: str
    duration: str
    target_audience: str
    youtube_strategy: Dict[str, str]
    visual_direction: List[str]
    music_direction: str

class OgilvyCocaColaGenerator:
    """David Ogilvyスタイルのコカ・コーラキャンペーン生成器"""
    
    def __init__(self):
        self.ogilvy_principles = [
            "The consumer is not a moron; she is your wife",
            "Headlines are 80% of the advertisement", 
            "Use facts, not puffery",
            "Long copy sells more than short copy",
            "Make your advertising distinctive"
        ]
        
        self.coca_cola_brand_attributes = {
            "heritage": "130+ years of refreshment tradition",
            "global_reach": "Available in 200+ countries",
            "secret_formula": "The world's most famous secret recipe",
            "moments": "Sharing happiness and special moments",
            "refreshment": "The pause that refreshes",
            "universal_appeal": "Bringing people together worldwide"
        }
    
    def generate_poster_campaign(self) -> PosterCampaign:
        """David OgilvyスタイルのCoca-Colaポスター企画を生成"""
        
        return PosterCampaign(
            headline="The Pause That Refreshes Has Delighted 7 Billion People",
            subheadline="For 137 years, Coca-Cola's secret formula has created moments of pure refreshment across every continent",
            body_copy="""
Every day, 1.9 billion servings of Coca-Cola products refresh the world. 

What makes this remarkable? Not marketing gimmicks or celebrity endorsements, but a simple truth: quality endures.

Our secret formula, locked in an Atlanta vault since 1886, creates the distinctive taste that has remained unchanged through world wars, technological revolutions, and changing consumer preferences.

When John Stith Pemberton first mixed that fateful blend in his backyard, he created more than a beverage. He created a moment—the pause between the urgent and the important, between stress and satisfaction.

Today, from a Tokyo businessman catching his breath to a Brazilian mother sharing joy with her children, Coca-Cola continues to provide that essential pause. Not because we tell you it's refreshing, but because 137 years of human experience proves it.

In an age of artificial everything, we remain committed to the real thing. The same carefully sourced ingredients. The same exacting standards. The same moment of authentic refreshment your great-grandmother enjoyed.

Some things never need to change. They simply need to endure.
            """.strip(),
            visual_concept="Classic Coca-Cola bottle silhouette with a world map pattern inside, showing tiny moments of people pausing to drink Coca-Cola across different countries and time zones",
            call_to_action="Taste the real thing. Experience the pause that has refreshed the world since 1886.",
            target_audience="Adults 25-54 who value authenticity, tradition, and quality",
            placement_strategy=[
                "Premium magazines (Time, National Geographic, The Economist)",
                "Transit stations in major metropolitan areas",
                "Airport terminals international gates",
                "Movie theater lobbies",
                "University campuses during exam periods"
            ],
            design_elements={
                "color_scheme": "Classic Coca-Cola red with elegant white typography",
                "typography": "Clean, serif font reminiscent of newspaper headlines",
                "layout": "70% visual, 30% text with generous white space",
                "logo_placement": "Bottom right corner, subtle but recognizable",
                "background": "Warm gradient from cream to soft red"
            }
        )
    
    def generate_youtube_campaign(self) -> VideoCampaign:
        """David OgilvyスタイルのCoca-Cola YouTube動画企画を生成"""
        
        script = """
[FADE IN: Black screen]

NARRATOR (V.O.): In 1886, a curious pharmacist in Atlanta mixed a secret formula that would change the world.

[Cut to: Vintage footage of early Coca-Cola production]

NARRATOR (V.O.): Not through grand promises or marketing spectacle, but through something far more powerful: authentic moments of refreshment.

[Montage: Real people across different decades enjoying Coca-Cola]
- 1920s: Friends sharing Coke at a soda fountain
- 1940s: Soldiers receiving Coca-Cola during WWII  
- 1960s: Family gathering around dinner table with Coke
- 1980s: Students celebrating graduation with Coke
- 2000s: Co-workers taking a break with Coke
- 2020s: Video call friends toasting with Coke

NARRATOR (V.O.): 137 years later, that same secret formula creates the same genuine pause. The same real refreshment.

[Close-up: The distinctive bubble formation in a glass of Coca-Cola]

NARRATOR (V.O.): While trends come and go, while technologies evolve, while the world changes rapidly around us...

[Cut to: Modern busy street, then slow motion of person opening a Coca-Cola]

NARRATOR (V.O.): Some things remain constant. Some things are worth preserving.

[Final shot: Classic Coca-Cola bottle against white background]

NARRATOR (V.O.): Coca-Cola. The real thing never goes out of style.

[End card: Coca-Cola logo with tagline "The Pause That Refreshes Since 1886"]
        """.strip()
        
        return VideoCampaign(
            title="The Real Thing Never Goes Out of Style - Coca-Cola Heritage Campaign",
            concept="A 60-second brand heritage piece that emphasizes Coca-Cola's authentic, enduring quality through historical moments and real consumer experiences",
            script=script,
            duration="60 seconds",
            target_audience="Adults 25-54 seeking authenticity and quality brands",
            youtube_strategy={
                "primary_placement": "Pre-roll on premium content channels (documentaries, news, educational)",
                "targeting": "Interest-based targeting on food & beverage, lifestyle, nostalgia content",
                "optimization": "Brand awareness and consideration campaigns",
                "companion_content": "Behind-the-scenes documentary about Coca-Cola's history and secret formula vault"
            },
            visual_direction=[
                "Cinematic quality with warm, nostalgic color grading",
                "Mix of authentic archival footage and contemporary cinematography",
                "Slow-motion emphasis on product interaction and refreshment moments",
                "Clean, sophisticated editing with smooth transitions",
                "Hero shots of the classic Coca-Cola bottle and logo"
            ],
            music_direction="Orchestral score building from simple piano to full orchestration, evoking nostalgia and warmth without being overly sentimental"
        )
    
    def create_campaign_analysis(self, poster: PosterCampaign, video: VideoCampaign) -> Dict:
        """キャンペーン分析レポートを作成"""
        
        return {
            "ogilvy_principles_applied": {
                "consumer_intelligence": "Treats audience as intelligent, informed consumers who value authenticity",
                "headline_power": f"Poster headline '{poster.headline}' leads with specific, factual claim",
                "factual_approach": "Uses specific data (1.9 billion servings, 137 years, 200+ countries)",
                "long_copy_strategy": "Detailed copy tells complete brand story with historical context",
                "distinctive_positioning": "Focuses on heritage and authenticity vs. competitors' trend-chasing"
            },
            "brand_integration": {
                "heritage_emphasis": "Both campaigns highlight 137-year legacy",
                "secret_formula_mystique": "Leverages the intrigue of the protected recipe",
                "global_reach": "Emphasizes worldwide acceptance and timeless appeal",
                "authentic_moments": "Shows real refreshment occasions across demographics"
            },
            "strategic_recommendations": {
                "poster_campaign": {
                    "budget_allocation": "$2M for premium placements over 6 months",
                    "success_metrics": "Brand awareness lift, purchase intent, heritage association",
                    "testing_approach": "A/B test headline variations in select markets"
                },
                "video_campaign": {
                    "budget_allocation": "$5M YouTube ad spend + $1M production",
                    "success_metrics": "View completion rate, brand recall, emotional connection scores",
                    "optimization": "Create 30-second and 15-second versions for different placements"
                }
            },
            "expected_results": {
                "brand_perception": "Increased association with quality, heritage, and authenticity",
                "competitive_advantage": "Differentiation from competitors focused on trends and celebrities",
                "long_term_value": "Campaigns that age well and reinforce consistent brand narrative"
            }
        }

def generate_presentation_materials():
    """プレゼンテーション資料を生成"""
    
    generator = OgilvyCocaColaGenerator()
    
    # キャンペーン生成
    poster_campaign = generator.generate_poster_campaign()
    video_campaign = generator.generate_youtube_campaign()
    analysis = generator.create_campaign_analysis(poster_campaign, video_campaign)
    
    # 結果を辞書にまとめる
    presentation_data = {
        "campaign_overview": {
            "title": "Coca-Cola Brand Heritage Campaign",
            "subtitle": "Applying David Ogilvy's Timeless Principles to a Timeless Brand",
            "created_date": datetime.now().isoformat(),
            "campaign_philosophy": "In an era of digital noise and fleeting trends, we return to Ogilvy's fundamental truth: respect your consumer's intelligence and tell them something worth knowing."
        },
        "poster_campaign": {
            "headline": poster_campaign.headline,
            "subheadline": poster_campaign.subheadline,
            "body_copy": poster_campaign.body_copy,
            "visual_concept": poster_campaign.visual_concept,
            "call_to_action": poster_campaign.call_to_action,
            "target_audience": poster_campaign.target_audience,
            "placement_strategy": poster_campaign.placement_strategy,
            "design_elements": poster_campaign.design_elements
        },
        "video_campaign": {
            "title": video_campaign.title,
            "concept": video_campaign.concept,
            "script": video_campaign.script,
            "duration": video_campaign.duration,
            "target_audience": video_campaign.target_audience,
            "youtube_strategy": video_campaign.youtube_strategy,
            "visual_direction": video_campaign.visual_direction,
            "music_direction": video_campaign.music_direction
        },
        "strategic_analysis": analysis
    }
    
    return presentation_data

# 実行とファイル出力
if __name__ == "__main__":
    print("=== David Ogilvy Style Coca-Cola Campaign Generator ===\n")
    
    # プレゼンテーション資料生成
    presentation = generate_presentation_materials()
    
    # JSONファイルとして保存
    with open('/Users/naoki/coca_cola_ogilvy_campaign_data.json', 'w', encoding='utf-8') as f:
        json.dump(presentation, f, indent=2, ensure_ascii=False)
    
    print("Campaign materials generated successfully!")
    print("Files created:")
    print("- coca_cola_ogilvy_campaign_data.json (Complete campaign data)")
    print("\nCampaign Overview:")
    print(f"Title: {presentation['campaign_overview']['title']}")
    print(f"Philosophy: {presentation['campaign_overview']['campaign_philosophy']}")
    print(f"\nPoster Headline: {presentation['poster_campaign']['headline']}")
    print(f"Video Title: {presentation['video_campaign']['title']}")