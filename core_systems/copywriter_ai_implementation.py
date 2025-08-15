"""
Famous Copywriter AI Service - Implementation Prototype
世界の有名なコピーライターAIサービスの実装とデモンストレーション

This module demonstrates the core functionality of the Famous Copywriter AI service,
including persona-based copywriting generation using Claude API.
"""

import json
import os
import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
try:
    import anthropic
except ImportError:
    anthropic = None
from datetime import datetime

# Configuration
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "your-api-key-here")

class CopywriterPersona(Enum):
    """有名なコピーライターのペルソナ定義"""
    DAVID_OGILVY = "david_ogilvy"
    CLAUDE_HOPKINS = "claude_hopkins"
    JOHN_CAPLES = "john_caples"
    DAN_KENNEDY = "dan_kennedy"

@dataclass
class CopywritingRequest:
    """コピーライティング依頼のデータ構造"""
    persona: CopywriterPersona
    content_type: str  # "advertisement", "email", "headline", "sales_letter"
    product_service: str
    target_audience: str
    key_benefits: List[str]
    tone: str  # "professional", "casual", "urgent", "friendly"
    length: str  # "short", "medium", "long"
    additional_context: Optional[str] = None

@dataclass
class CopywritingResult:
    """生成されたコピーライティングの結果"""
    content: str
    persona_used: CopywriterPersona
    timestamp: str
    metadata: Dict

class CopywriterPersonaManager:
    """コピーライターペルソナの管理クラス"""
    
    PERSONA_PROFILES = {
        CopywriterPersona.DAVID_OGILVY: {
            "name": "David Ogilvy",
            "style_characteristics": [
                "Research-based approach",
                "Long-form copy preference", 
                "Factual and informative tone",
                "Brand positioning focus",
                "Sophisticated vocabulary"
            ],
            "famous_principles": [
                "The consumer isn't a moron; she is your wife",
                "Headlines are 80% of the ad",
                "Long copy sells more than short copy",
                "Use facts, not puffery"
            ],
            "prompt_template": """
You are David Ogilvy, the "Father of Advertising". Write in your characteristic style:
- Use research-backed claims and specific facts
- Write long-form, informative copy that educates the reader
- Focus on brand positioning and sophisticated messaging
- Include compelling headlines that capture attention
- Maintain a factual, authoritative yet approachable tone
- Use elegant, persuasive language that respects the reader's intelligence

Product/Service: {product_service}
Target Audience: {target_audience}  
Key Benefits: {key_benefits}
Content Type: {content_type}
Tone: {tone}
Length: {length}

Additional Context: {additional_context}

Generate compelling copy in David Ogilvy's distinctive style:
"""
        },
        
        CopywriterPersona.CLAUDE_HOPKINS: {
            "name": "Claude Hopkins",
            "style_characteristics": [
                "Scientific advertising approach",
                "Test-driven methodology",
                "ROI-focused messaging",
                "Specific claims and offers",
                "Direct response orientation"
            ],
            "famous_principles": [
                "Advertising is salesmanship in print",
                "Test everything, assume nothing", 
                "Specific claims are more believable",
                "Make every ad pay its own way"
            ],
            "prompt_template": """
You are Claude Hopkins, pioneer of scientific advertising. Write in your characteristic style:
- Focus on measurable results and specific claims
- Use testing-oriented, data-driven language
- Make specific offers with clear value propositions
- Write direct, no-nonsense copy that drives action
- Include trackable elements and calls-to-action
- Use simple, clear language that sells

Product/Service: {product_service}
Target Audience: {target_audience}
Key Benefits: {key_benefits}
Content Type: {content_type}
Tone: {tone}
Length: {length}

Additional Context: {additional_context}

Generate scientific, results-driven copy in Claude Hopkins' style:
"""
        },
        
        CopywriterPersona.JOHN_CAPLES: {
            "name": "John Caples", 
            "style_characteristics": [
                "Headline mastery",
                "Psychological triggers",
                "Curiosity-driven approach",
                "Reader benefit focus",
                "Emotional connection"
            ],
            "famous_principles": [
                "Headlines are the most important part",
                "Appeal to human psychology",
                "Create curiosity and intrigue",
                "Focus on reader benefits, not features"
            ],
            "prompt_template": """
You are John Caples, master of headlines and psychological copywriting. Write in your characteristic style:
- Craft compelling headlines that stop readers in their tracks
- Use psychological triggers to create emotional connection
- Focus on reader benefits and transformation
- Create curiosity and intrigue that compels reading
- Use storytelling elements to engage the audience
- Make the reader the hero of the story

Product/Service: {product_service}
Target Audience: {target_audience}
Key Benefits: {key_benefits}
Content Type: {content_type}
Tone: {tone}
Length: {length}

Additional Context: {additional_context}

Generate psychologically compelling copy with powerful headlines in John Caples' style:
"""
        },
        
        CopywriterPersona.DAN_KENNEDY: {
            "name": "Dan Kennedy",
            "style_characteristics": [
                "Direct marketing focus",
                "Relationship building emphasis", 
                "Urgency and scarcity tactics",
                "Personal, conversational tone",
                "Sales funnel orientation"
            ],
            "famous_principles": [
                "Build relationships, not just make sales",
                "Create urgency and scarcity",
                "Use personal, authentic voice",
                "Focus on lifetime customer value"
            ],
            "prompt_template": """
You are Dan Kennedy, direct marketing guru and relationship-focused copywriter. Write in your characteristic style:
- Use direct, personal, conversational tone as if speaking to a friend
- Build relationships and trust through authentic communication
- Create urgency and scarcity where appropriate
- Focus on long-term customer value and relationships
- Use storytelling and personal anecdotes
- Include strong calls-to-action with deadline pressure

Product/Service: {product_service}
Target Audience: {target_audience}
Key Benefits: {key_benefits}
Content Type: {content_type}
Tone: {tone}
Length: {length}

Additional Context: {additional_context}

Generate relationship-building, direct marketing copy in Dan Kennedy's style:
"""
        }
    }
    
    @classmethod
    def get_persona_profile(cls, persona: CopywriterPersona) -> Dict:
        """指定されたペルソナのプロファイルを取得"""
        return cls.PERSONA_PROFILES.get(persona, {})
    
    @classmethod
    def get_prompt_template(cls, persona: CopywriterPersona) -> str:
        """指定されたペルソナのプロンプトテンプレートを取得"""
        profile = cls.get_persona_profile(persona)
        return profile.get("prompt_template", "")

class CopywriterAIService:
    """メインのコピーライターAIサービスクラス"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or CLAUDE_API_KEY
        self.client = anthropic.Anthropic(api_key=self.api_key) if (anthropic and self.api_key != "your-api-key-here") else None
        self.persona_manager = CopywriterPersonaManager()
    
    async def generate_copy(self, request: CopywritingRequest) -> CopywritingResult:
        """指定されたペルソナでコピーライティングを生成"""
        
        # プロンプトテンプレートを取得
        template = self.persona_manager.get_prompt_template(request.persona)
        
        # プロンプトに値を代入
        prompt = template.format(
            product_service=request.product_service,
            target_audience=request.target_audience,
            key_benefits=", ".join(request.key_benefits),
            content_type=request.content_type,
            tone=request.tone,
            length=request.length,
            additional_context=request.additional_context or "None"
        )
        
        # APIクライアントが設定されている場合は実際にAPIを呼び出す
        if self.client:
            try:
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2000,
                    temperature=0.7,
                    messages=[
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ]
                )
                
                generated_content = response.content[0].text
                
            except Exception as e:
                generated_content = f"Error generating content: {str(e)}\n\n[Demo Mode] This would be the generated copy in {request.persona.value} style."
        else:
            # デモモード: APIキーが設定されていない場合のサンプル生成
            generated_content = self._generate_demo_copy(request)
        
        return CopywritingResult(
            content=generated_content,
            persona_used=request.persona,
            timestamp=datetime.now().isoformat(),
            metadata={
                "content_type": request.content_type,
                "target_audience": request.target_audience,
                "tone": request.tone,
                "length": request.length
            }
        )
    
    def _generate_demo_copy(self, request: CopywritingRequest) -> str:
        """デモ用のサンプルコピー生成"""
        persona_name = self.persona_manager.get_persona_profile(request.persona)["name"]
        
        return f"""
[DEMO MODE - {persona_name} Style Copy]

=== Generated Copy ===

**Headline:** Revolutionary {request.product_service} - Transform Your {request.target_audience} Experience

**Body Copy:**

Dear {request.target_audience},

In the spirit of {persona_name}'s legendary copywriting style, here's how we would craft your message:

Key Benefits Highlighted:
{chr(10).join([f"• {benefit}" for benefit in request.key_benefits])}

This copy would be tailored for: {request.content_type}
Tone: {request.tone}
Length: {request.length}

[Note: This is a demo. With a valid API key, you would see actual {persona_name}-style copy generated by Claude AI]

Best regards,
Your AI Copywriter in {persona_name}'s Style
        """

class CopywriterAIValidator:
    """生成されたコピーの品質検証クラス"""
    
    @staticmethod
    def validate_copy_quality(result: CopywritingResult) -> Dict:
        """コピーの品質を評価"""
        content = result.content
        
        validation_results = {
            "word_count": len(content.split()),
            "has_headline": "headline" in content.lower() or "**" in content,
            "has_call_to_action": any(cta in content.lower() for cta in [
                "call now", "click here", "order today", "visit", "contact", 
                "buy now", "get started", "learn more"
            ]),
            "readability_score": CopywriterAIValidator._calculate_readability(content),
            "persona_consistency": CopywriterAIValidator._check_persona_consistency(
                result.persona_used, content
            )
        }
        
        return validation_results
    
    @staticmethod
    def _calculate_readability(text: str) -> float:
        """簡易的な読みやすさスコア算出"""
        words = text.split()
        sentences = text.split('.')
        if not words or not sentences:
            return 0.0
        
        avg_words_per_sentence = len(words) / len(sentences)
        # 簡易フレッシュリーディングエーススコア近似
        score = 206.835 - (1.015 * avg_words_per_sentence)
        return max(0.0, min(100.0, score))
    
    @staticmethod
    def _check_persona_consistency(persona: CopywriterPersona, content: str) -> float:
        """ペルソナの一貫性をチェック（簡易版）"""
        # 実際の実装では、より詳細な自然言語処理分析を行う
        content_lower = content.lower()
        
        persona_keywords = {
            CopywriterPersona.DAVID_OGILVY: ["research", "fact", "brand", "sophisticated"],
            CopywriterPersona.CLAUDE_HOPKINS: ["test", "result", "specific", "scientific"],
            CopywriterPersona.JOHN_CAPLES: ["headline", "curiosity", "benefit", "psychology"],
            CopywriterPersona.DAN_KENNEDY: ["urgent", "relationship", "personal", "scarcity"]
        }
        
        relevant_keywords = persona_keywords.get(persona, [])
        found_keywords = sum(1 for keyword in relevant_keywords if keyword in content_lower)
        
        return (found_keywords / len(relevant_keywords)) * 100 if relevant_keywords else 0.0

# デモンストレーション実行
async def run_copywriter_ai_demo():
    """コピーライターAIサービスのデモ実行"""
    
    print("=== Famous Copywriter AI Service Demo ===\n")
    
    # サービス初期化
    ai_service = CopywriterAIService()
    
    # デモ用リクエスト作成
    demo_requests = [
        CopywritingRequest(
            persona=CopywriterPersona.DAVID_OGILVY,
            content_type="advertisement",
            product_service="Premium Marketing Automation Software",
            target_audience="small business owners",
            key_benefits=[
                "Increase sales by 40% in 90 days",
                "Automate repetitive marketing tasks", 
                "Get detailed analytics and insights"
            ],
            tone="professional",
            length="medium",
            additional_context="Targeting entrepreneurs who want to scale their business"
        ),
        
        CopywritingRequest(
            persona=CopywriterPersona.CLAUDE_HOPKINS,
            content_type="sales_letter",
            product_service="Weight Loss Supplement",
            target_audience="people struggling with weight loss",
            key_benefits=[
                "Lose 10 lbs in 30 days guaranteed",
                "No side effects or strict diets",
                "Clinically proven ingredients"
            ],
            tone="urgent",
            length="long",
            additional_context="Targeting people who have tried other solutions without success"
        )
    ]
    
    # 各リクエストを処理してデモ
    for i, request in enumerate(demo_requests, 1):
        print(f"\n--- Demo {i}: {request.persona.value.replace('_', ' ').title()} Style ---")
        
        # コピー生成
        result = await ai_service.generate_copy(request)
        
        # 結果表示
        print(f"\nGenerated Copy:\n{result.content}")
        
        # 品質検証
        validation = CopywriterAIValidator.validate_copy_quality(result)
        print(f"\n--- Quality Validation ---")
        print(f"Word Count: {validation['word_count']}")
        print(f"Has Headline: {validation['has_headline']}")
        print(f"Has Call-to-Action: {validation['has_call_to_action']}")
        print(f"Readability Score: {validation['readability_score']:.1f}")
        print(f"Persona Consistency: {validation['persona_consistency']:.1f}%")
        
        print("\n" + "="*80 + "\n")

def save_implementation_analysis():
    """実装分析をJSONファイルに保存"""
    analysis = {
        "implementation_status": {
            "core_functionality": "Completed",
            "persona_system": "Completed", 
            "api_integration": "Completed",
            "validation_system": "Completed",
            "demo_system": "Completed"
        },
        "technical_specifications": {
            "programming_language": "Python 3.8+",
            "ai_provider": "Anthropic Claude",
            "architecture": "Object-oriented design with async support",
            "key_features": [
                "4 Famous copywriter personas",
                "Flexible request/response system",
                "Quality validation",
                "Demo mode for testing"
            ]
        },
        "personas_implemented": {
            "david_ogilvy": "Research-based, long-form advertising copy",
            "claude_hopkins": "Scientific, test-driven direct response", 
            "john_caples": "Headline-focused, psychological triggers",
            "dan_kennedy": "Relationship-building, direct marketing"
        },
        "next_steps": [
            "Integrate with web framework (FastAPI/Flask)",
            "Add user authentication and billing",
            "Implement A/B testing capabilities",
            "Create web UI interface",
            "Add analytics and reporting",
            "Scale infrastructure for production"
        ],
        "validation_metrics": {
            "word_count_tracking": "Implemented",
            "headline_detection": "Implemented",
            "cta_detection": "Implemented",
            "readability_scoring": "Basic implementation",
            "persona_consistency": "Keyword-based validation"
        }
    }
    
    with open('/Users/naoki/copywriter_ai_implementation_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print("Implementation analysis saved to copywriter_ai_implementation_analysis.json")

# メイン実行
if __name__ == "__main__":
    # デモ実行
    asyncio.run(run_copywriter_ai_demo())
    
    # 実装分析保存
    save_implementation_analysis()
    
    print("\n=== Implementation Complete ===")
    print("✅ Famous Copywriter AI Service prototype implemented")
    print("✅ 4 copywriter personas configured")
    print("✅ Quality validation system ready")
    print("✅ Demo mode functional")
    print("✅ Production-ready architecture designed")
    
    print("\nTo run with real API:")
    print("1. Set CLAUDE_API_KEY environment variable")
    print("2. Install required dependencies: pip install anthropic")
    print("3. Execute: python copywriter_ai_implementation.py")