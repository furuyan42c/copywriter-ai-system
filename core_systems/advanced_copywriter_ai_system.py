"""
Advanced Copywriter AI System - Production Ready
本格的コピーライターAIシステム（完成版）

実際のTCCデータとスタイル分析を統合した
高精度コピーライター生成システム
"""

import json
import sqlite3
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import re
from collections import Counter
import logging
import asyncio

# Claude API用（実際のAPIキーが必要）
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

@dataclass
class AdvancedCopywritingRequest:
    """高度なコピーライティング依頼構造"""
    # 基本情報
    copywriter_persona: str
    content_type: str
    product_service: str
    target_audience: str
    
    # 詳細設定
    style_intensity: float  # 0.0-1.0 (ペルソナ特徴の強度)
    creativity_level: float  # 0.0-1.0 (創造性レベル)
    length_preference: str  # 'short', 'medium', 'long'
    tone_preference: str   # 'formal', 'casual', 'emotional', 'rational'
    
    # 制約・要件
    key_messages: List[str]
    avoid_words: List[str]
    target_metrics: Optional[Dict[str, float]]  # 想定指標（読みやすさ等）
    
    # コンテキスト
    brand_guidelines: Optional[str]
    competitive_context: Optional[str]
    cultural_considerations: Optional[str]

@dataclass
class AdvancedCopywritingResult:
    """高度なコピーライティング結果"""
    # 生成コンテンツ
    primary_copy: str
    alternative_versions: List[str]
    
    # 品質指標
    style_accuracy_score: float
    predicted_effectiveness: float
    readability_score: float
    emotional_impact_score: float
    
    # 分析情報
    style_elements_detected: List[str]
    keyword_optimization: Dict[str, float]
    target_alignment: Dict[str, float]
    
    # メタデータ
    generation_metadata: Dict
    confidence_score: float
    recommended_usage: List[str]

class PersonaDatabase:
    """強化されたペルソナデータベース"""
    
    def __init__(self, db_path: str, analysis_data_path: str):
        self.db_path = db_path
        self.analysis_data_path = analysis_data_path
        self.load_enhanced_personas()
    
    def load_enhanced_personas(self):
        """強化されたペルソナデータの読み込み"""
        # スタイル分析結果の読み込み
        try:
            with open(self.analysis_data_path, 'r', encoding='utf-8') as f:
                self.style_analysis = json.load(f)
        except FileNotFoundError:
            self.style_analysis = {}
            logging.warning("Style analysis data not found, using fallback")
        
        # TCCデータベースからの実作品読み込み
        self.load_actual_works()
        
        # 統合ペルソナプロファイルの構築
        self.build_integrated_personas()
    
    def load_actual_works(self):
        """実際の作品データ読み込み"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT copywriter, copy_text, client, industry, media_type, year, award
                FROM copy_works
                WHERE copy_text IS NOT NULL AND copy_text != ""
            ''')
            
            self.actual_works = {}
            for row in cursor.fetchall():
                copywriter = row[0]
                if copywriter not in self.actual_works:
                    self.actual_works[copywriter] = []
                
                self.actual_works[copywriter].append({
                    'copy_text': row[1],
                    'client': row[2],
                    'industry': row[3],
                    'media_type': row[4],
                    'year': row[5],
                    'award': row[6]
                })
            
            conn.close()
            logging.info(f"Loaded actual works for {len(self.actual_works)} copywriters")
            
        except Exception as e:
            logging.error(f"Error loading actual works: {e}")
            self.actual_works = {}
    
    def build_integrated_personas(self):
        """統合ペルソナプロファイル構築"""
        self.integrated_personas = {}
        
        # スタイル分析データとの統合
        if 'copywriter_analyses' in self.style_analysis:
            for name, analysis in self.style_analysis['copywriter_analyses'].items():
                
                # 実作品サンプル
                work_samples = self.actual_works.get(name, [])[:5]  # 最大5作品
                
                # 統合ペルソナプロファイル作成
                integrated_persona = {
                    'name': name,
                    'style_metrics': analysis,
                    'work_samples': work_samples,
                    'writing_patterns': self.extract_writing_patterns(name, work_samples),
                    'signature_elements': self.identify_signature_elements(analysis),
                    'generation_prompts': self.create_generation_prompts(name, analysis, work_samples)
                }
                
                self.integrated_personas[name] = integrated_persona
        
        logging.info(f"Built integrated personas for {len(self.integrated_personas)} copywriters")
    
    def extract_writing_patterns(self, name: str, works: List[Dict]) -> Dict:
        """ライティングパターン抽出"""
        if not works:
            return {}
        
        patterns = {
            'common_structures': [],
            'typical_openings': [],
            'characteristic_endings': [],
            'preferred_expressions': [],
            'sentence_patterns': []
        }
        
        for work in works:
            text = work['copy_text']
            
            # 文の構造分析
            sentences = [s.strip() for s in re.split(r'[。！？]', text) if s.strip()]
            
            if sentences:
                patterns['typical_openings'].append(sentences[0][:10])
                if len(sentences) > 1:
                    patterns['characteristic_endings'].append(sentences[-1][-10:])
            
            # 特徴的表現の抽出
            expressions = re.findall(r'[ぁ-んァ-ヶー一-龠]{2,6}', text)
            patterns['preferred_expressions'].extend(expressions)
        
        # 頻度分析
        for key in ['typical_openings', 'characteristic_endings', 'preferred_expressions']:
            counter = Counter(patterns[key])
            patterns[key] = [item for item, count in counter.most_common(3)]
        
        return patterns
    
    def identify_signature_elements(self, analysis: Dict) -> List[str]:
        """シグネチャー要素特定"""
        elements = []
        
        # 統計的特徴からの抽出
        if analysis.get('vocabulary_richness', 0) > 0.7:
            elements.append('高い語彙多様性')
        
        if analysis.get('emotional_tone_score', 0) > 50:
            elements.append('感情的表現重視')
        
        if analysis.get('readability_score', 0) > 70:
            elements.append('高い読みやすさ')
        
        # トップキーワードから特徴抽出
        top_keywords = analysis.get('top_keywords', [])
        if top_keywords:
            elements.append(f"頻出キーワード: {', '.join([kw[0] for kw in top_keywords[:3]])}")
        
        return elements
    
    def create_generation_prompts(self, name: str, analysis: Dict, works: List[Dict]) -> Dict:
        """生成用プロンプト作成"""
        
        # スタイル特徴の言語化
        style_description = f"""
{name}のコピーライティングスタイル:

統計的特徴:
- 平均コピー長: {analysis.get('avg_copy_length', 0):.0f}文字
- 読みやすさスコア: {analysis.get('readability_score', 0):.1f}
- 感情的トーン: {analysis.get('emotional_tone_score', 0):.1f}%
- 語彙多様性: {analysis.get('vocabulary_richness', 0):.3f}

主要テーマ: {', '.join(analysis.get('common_themes', []))}
トップキーワード: {', '.join([kw[0] for kw in analysis.get('top_keywords', [])[:5]])}
活動期間: {analysis.get('active_period', ['', ''])[0]}-{analysis.get('active_period', ['', ''])[1]}
        """.strip()
        
        # 実作品例
        work_examples = ""
        if works:
            work_examples = "実際の作品例:\n"
            for i, work in enumerate(works[:3], 1):
                work_examples += f"{i}. 「{work['copy_text']}」（{work.get('client', '不明')}・{work.get('year', '不明')}年）\n"
        
        # 生成指示プロンプト
        generation_prompt = f"""
あなたは{name}のスタイルでコピーライティングを行うAIです。

{style_description}

{work_examples}

以下の特徴を必ず反映してコピーを作成してください:
- {name}特有の言葉選びと表現方法
- 統計的特徴に合致した文字数・文体
- 実作品に見られるトーン・訴求方法
- {name}らしい独自性と創造性

コピー作成時は、商品・サービス情報、ターゲット層、媒体を考慮し、
{name}が手がけたであろうクオリティの作品を生成してください。
        """.strip()
        
        return {
            'style_description': style_description,
            'work_examples': work_examples,
            'generation_prompt': generation_prompt
        }
    
    def get_persona(self, name: str) -> Optional[Dict]:
        """ペルソナ取得"""
        return self.integrated_personas.get(name)
    
    def list_available_personas(self) -> List[str]:
        """利用可能ペルソナ一覧"""
        return list(self.integrated_personas.keys())

class AdvancedCopywriterAIGenerator:
    """高精度コピーライター AI生成器"""
    
    def __init__(self, persona_db: PersonaDatabase, api_key: str = None):
        self.persona_db = persona_db
        self.api_key = api_key
        
        # Claude API初期化
        if ANTHROPIC_AVAILABLE and api_key and api_key != "your-api-key-here":
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            self.client = None
            logging.warning("Claude API not available, using fallback generation")
    
    async def generate_advanced_copy(self, request: AdvancedCopywritingRequest) -> AdvancedCopywritingResult:
        """高精度コピー生成"""
        
        # ペルソナ情報取得
        persona = self.persona_db.get_persona(request.copywriter_persona)
        if not persona:
            raise ValueError(f"Persona not found: {request.copywriter_persona}")
        
        # 生成プロンプト構築
        generation_prompt = self.build_advanced_prompt(request, persona)
        
        # AI生成実行
        if self.client:
            generated_content = await self.generate_with_claude(generation_prompt, request)
        else:
            generated_content = self.generate_fallback(request, persona)
        
        # 品質分析
        quality_scores = self.analyze_quality(generated_content, request, persona)
        
        # 結果構築
        return AdvancedCopywritingResult(
            primary_copy=generated_content['primary'],
            alternative_versions=generated_content.get('alternatives', []),
            style_accuracy_score=quality_scores['style_accuracy'],
            predicted_effectiveness=quality_scores['effectiveness'],
            readability_score=quality_scores['readability'],
            emotional_impact_score=quality_scores['emotional_impact'],
            style_elements_detected=quality_scores['detected_elements'],
            keyword_optimization=quality_scores['keyword_scores'],
            target_alignment=quality_scores['target_alignment'],
            generation_metadata=generated_content.get('metadata', {}),
            confidence_score=quality_scores['confidence'],
            recommended_usage=self.generate_usage_recommendations(quality_scores)
        )
    
    def build_advanced_prompt(self, request: AdvancedCopywritingRequest, persona: Dict) -> str:
        """高度なプロンプト構築"""
        
        base_prompt = persona['generation_prompts']['generation_prompt']
        
        # 追加コンテキスト
        context_additions = f"""

具体的な依頼内容:
- 商品・サービス: {request.product_service}
- ターゲット: {request.target_audience}
- コンテンツタイプ: {request.content_type}
- 希望する長さ: {request.length_preference}
- トーン: {request.tone_preference}
- スタイル強度: {request.style_intensity} (0.0-1.0)
- 創造性レベル: {request.creativity_level} (0.0-1.0)

キーメッセージ: {', '.join(request.key_messages)}
避けるべき言葉: {', '.join(request.avoid_words)}
        """
        
        if request.brand_guidelines:
            context_additions += f"\nブランドガイドライン: {request.brand_guidelines}"
        
        if request.competitive_context:
            context_additions += f"\n競合状況: {request.competitive_context}"
        
        # 品質要求
        quality_requirements = f"""

品質要求:
- {request.copywriter_persona}のスタイル特徴を{request.style_intensity*100:.0f}%の強度で反映
- 創造性レベル{request.creativity_level*100:.0f}%で、独創的だが適切な表現を使用
- ターゲット層に最適化された言葉選びと訴求
- {request.length_preference}の長さに適したコンテンツ

出力形式:
1. メインコピー（最も推奨される案）
2. 代替案1（トーンが異なるバリエーション）
3. 代替案2（アプローチが異なるバリエーション）
        """
        
        return base_prompt + context_additions + quality_requirements
    
    async def generate_with_claude(self, prompt: str, request: AdvancedCopywritingRequest) -> Dict:
        """Claude APIでの生成"""
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2000,
                    temperature=min(0.9, 0.3 + request.creativity_level * 0.6),
                    messages=[{"role": "user", "content": prompt}]
                )
            )
            
            content = response.content[0].text
            
            # 生成内容の解析・分割
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            
            primary = ""
            alternatives = []
            
            # メインコピーと代替案の分離
            current_section = "main"
            for line in lines:
                if "代替案" in line or "バリエーション" in line:
                    current_section = "alt"
                elif line.startswith("1.") or line.startswith("メイン"):
                    current_section = "main"
                elif line.startswith("2.") or line.startswith("3."):
                    current_section = "alt"
                elif current_section == "main" and not line.startswith("メイン"):
                    primary += line + "\n"
                elif current_section == "alt" and not line.startswith(("2.", "3.", "代替案")):
                    if alternatives and line:
                        alternatives[-1] += line + "\n"
                    elif line:
                        alternatives.append(line + "\n")
            
            return {
                'primary': primary.strip(),
                'alternatives': [alt.strip() for alt in alternatives[:2]],
                'metadata': {
                    'model_used': 'claude-3-5-sonnet',
                    'temperature': min(0.9, 0.3 + request.creativity_level * 0.6),
                    'generated_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logging.error(f"Claude API generation failed: {e}")
            return self.generate_fallback(request, self.persona_db.get_persona(request.copywriter_persona))
    
    def generate_fallback(self, request: AdvancedCopywritingRequest, persona: Dict) -> Dict:
        """フォールバック生成（APIなし）"""
        
        # スタイル特徴から基本パターン生成
        style_metrics = persona.get('style_metrics', {})
        work_samples = persona.get('work_samples', [])
        
        # 基本的なコピー構造
        if request.length_preference == 'short':
            template = "{hook}。{product}で{benefit}。"
        elif request.length_preference == 'long':
            template = "{hook}。{problem}を解決する{product}。{benefit_detail}。{call_to_action}。"
        else:
            template = "{hook}。{product}が{benefit}をお届け。"
        
        # テンプレート要素の生成
        elements = {
            'hook': f"新しい{request.target_audience}の体験",
            'product': request.product_service,
            'benefit': "価値ある時間",
            'problem': f"{request.target_audience}の課題",
            'benefit_detail': "これまでにない満足感",
            'call_to_action': "今すぐ体験してください"
        }
        
        # スタイル調整
        if style_metrics.get('emotional_tone_score', 0) > 50:
            elements['hook'] = f"心を動かす{request.target_audience}への提案"
        
        primary = template.format(**elements)
        
        # 代替案生成
        alternatives = [
            f"{request.product_service}が、{request.target_audience}の毎日を変える。",
            f"選ばれる理由がある。{request.product_service}という選択。"
        ]
        
        return {
            'primary': primary,
            'alternatives': alternatives,
            'metadata': {
                'generation_method': 'fallback',
                'generated_at': datetime.now().isoformat()
            }
        }
    
    def analyze_quality(self, content: Dict, request: AdvancedCopywritingRequest, persona: Dict) -> Dict:
        """品質分析"""
        primary_copy = content['primary']
        
        # スタイル一致度
        style_accuracy = self.calculate_style_accuracy(primary_copy, persona)
        
        # 効果予測
        effectiveness = self.predict_effectiveness(primary_copy, request)
        
        # 読みやすさ
        readability = self.calculate_readability(primary_copy)
        
        # 感情的インパクト
        emotional_impact = self.calculate_emotional_impact(primary_copy)
        
        # 検出された要素
        detected_elements = self.detect_style_elements(primary_copy, persona)
        
        # キーワード最適化
        keyword_scores = self.analyze_keyword_optimization(primary_copy, request)
        
        # ターゲット適合度
        target_alignment = self.analyze_target_alignment(primary_copy, request)
        
        # 総合信頼度
        confidence = (style_accuracy + effectiveness + readability) / 3
        
        return {
            'style_accuracy': style_accuracy,
            'effectiveness': effectiveness,
            'readability': readability,
            'emotional_impact': emotional_impact,
            'detected_elements': detected_elements,
            'keyword_scores': keyword_scores,
            'target_alignment': target_alignment,
            'confidence': confidence
        }
    
    def calculate_style_accuracy(self, copy_text: str, persona: Dict) -> float:
        """スタイル一致度計算"""
        style_metrics = persona.get('style_metrics', {})
        
        # 長さの一致度
        expected_length = style_metrics.get('avg_copy_length', 50)
        actual_length = len(copy_text)
        length_score = max(0, 100 - abs(expected_length - actual_length) / expected_length * 100)
        
        # キーワード一致度
        top_keywords = [kw[0] for kw in style_metrics.get('top_keywords', [])]
        keyword_matches = sum(1 for keyword in top_keywords if keyword in copy_text)
        keyword_score = (keyword_matches / len(top_keywords)) * 100 if top_keywords else 50
        
        # 総合スコア
        return (length_score * 0.3 + keyword_score * 0.7)
    
    def predict_effectiveness(self, copy_text: str, request: AdvancedCopywritingRequest) -> float:
        """効果予測"""
        score = 50.0  # ベースライン
        
        # キーメッセージ包含度
        if request.key_messages:
            message_coverage = sum(1 for msg in request.key_messages if any(word in copy_text for word in msg.split()))
            score += (message_coverage / len(request.key_messages)) * 30
        
        # ターゲット適合度
        if request.target_audience in copy_text or any(word in copy_text for word in request.target_audience.split()):
            score += 10
        
        # コール・トゥ・アクション
        cta_words = ['今すぐ', 'お試し', '体験', '発見', 'はじめ', '選ぶ']
        if any(word in copy_text for word in cta_words):
            score += 10
        
        return min(100, score)
    
    def calculate_readability(self, copy_text: str) -> float:
        """読みやすさ計算"""
        # 簡易読みやすさ指標
        char_count = len(copy_text)
        sentence_count = len([s for s in re.split(r'[。！？]', copy_text) if s.strip()])
        
        if sentence_count == 0:
            return 50.0
        
        avg_sentence_length = char_count / sentence_count
        
        # 理想的な文長（20-40文字）からの乖離度で評価
        readability = max(0, 100 - abs(30 - avg_sentence_length) * 2)
        
        return readability
    
    def calculate_emotional_impact(self, copy_text: str) -> float:
        """感情的インパクト計算"""
        emotional_words = [
            '感動', '驚き', '喜び', '愛', '幸せ', '素晴らしい', '美しい', '特別',
            '感謝', '心', '思い', '願い', '夢', '希望', '感じる', '体験'
        ]
        
        impact_count = sum(1 for word in emotional_words if word in copy_text)
        return min(100, impact_count * 20)
    
    def detect_style_elements(self, copy_text: str, persona: Dict) -> List[str]:
        """スタイル要素検出"""
        elements = []
        
        # シグネチャー要素チェック
        signature_elements = persona.get('signature_elements', [])
        for element in signature_elements:
            if '語彙' in element and len(set(copy_text.split())) > 5:
                elements.append('語彙多様性')
            elif '感情' in element and any(word in copy_text for word in ['感じ', '心', '思い']):
                elements.append('感情的表現')
            elif '読みやすさ' in element and len(copy_text) < 100:
                elements.append('簡潔な表現')
        
        return elements
    
    def analyze_keyword_optimization(self, copy_text: str, request: AdvancedCopywritingRequest) -> Dict[str, float]:
        """キーワード最適化分析"""
        scores = {}
        
        # 商品・サービス名の含有
        if request.product_service.lower() in copy_text.lower():
            scores['product_inclusion'] = 100.0
        else:
            scores['product_inclusion'] = 0.0
        
        # ターゲット適合キーワード
        target_words = request.target_audience.split()
        target_matches = sum(1 for word in target_words if word in copy_text)
        scores['target_relevance'] = (target_matches / len(target_words)) * 100 if target_words else 0
        
        return scores
    
    def analyze_target_alignment(self, copy_text: str, request: AdvancedCopywritingRequest) -> Dict[str, float]:
        """ターゲット適合度分析"""
        alignment = {}
        
        # 年代適合度（簡易判定）
        if '若い' in request.target_audience or '20代' in request.target_audience:
            youth_words = ['新しい', 'トレンド', 'スタイリッシュ', '今', '最新']
            alignment['age_appropriateness'] = sum(10 for word in youth_words if word in copy_text)
        else:
            mature_words = ['信頼', '品質', '安心', '実績', '経験']
            alignment['age_appropriateness'] = sum(10 for word in mature_words if word in copy_text)
        
        # 性別適合度
        if '女性' in request.target_audience:
            female_words = ['美しい', '優しい', 'エレガント', 'かわいい', 'おしゃれ']
            alignment['gender_appropriateness'] = sum(10 for word in female_words if word in copy_text)
        elif '男性' in request.target_audience:
            male_words = ['力強い', 'クール', 'スマート', 'プロ', '本格']
            alignment['gender_appropriateness'] = sum(10 for word in male_words if word in copy_text)
        else:
            alignment['gender_appropriateness'] = 50.0
        
        return alignment
    
    def generate_usage_recommendations(self, quality_scores: Dict) -> List[str]:
        """使用推奨事項生成"""
        recommendations = []
        
        if quality_scores['style_accuracy'] > 80:
            recommendations.append("スタイル再現度が高く、メインコピーとして使用推奨")
        
        if quality_scores['effectiveness'] > 75:
            recommendations.append("高い効果が期待でき、実際のキャンペーンで使用可能")
        
        if quality_scores['readability'] > 70:
            recommendations.append("読みやすく、幅広い層に訴求可能")
        
        if quality_scores['emotional_impact'] > 60:
            recommendations.append("感情的訴求力があり、ブランディング用途に適している")
        
        if not recommendations:
            recommendations.append("品質向上のため再生成を推奨")
        
        return recommendations

# 統合システムクラス
class ProductionCopywriterAI:
    """本格運用コピーライターAIシステム"""
    
    def __init__(self, db_path: str, analysis_path: str, api_key: str = None):
        self.persona_db = PersonaDatabase(db_path, analysis_path)
        self.generator = AdvancedCopywriterAIGenerator(self.persona_db, api_key)
        
        logging.info("Production Copywriter AI System initialized")
    
    async def create_professional_copy(self, 
                                     copywriter_name: str,
                                     product_service: str,
                                     target_audience: str,
                                     content_type: str = "advertisement",
                                     **kwargs) -> AdvancedCopywritingResult:
        """プロフェッショナルコピー作成"""
        
        request = AdvancedCopywritingRequest(
            copywriter_persona=copywriter_name,
            content_type=content_type,
            product_service=product_service,
            target_audience=target_audience,
            style_intensity=kwargs.get('style_intensity', 0.8),
            creativity_level=kwargs.get('creativity_level', 0.7),
            length_preference=kwargs.get('length_preference', 'medium'),
            tone_preference=kwargs.get('tone_preference', 'professional'),
            key_messages=kwargs.get('key_messages', []),
            avoid_words=kwargs.get('avoid_words', []),
            target_metrics=kwargs.get('target_metrics'),
            brand_guidelines=kwargs.get('brand_guidelines'),
            competitive_context=kwargs.get('competitive_context'),
            cultural_considerations=kwargs.get('cultural_considerations')
        )
        
        return await self.generator.generate_advanced_copy(request)
    
    def get_available_copywriters(self) -> List[str]:
        """利用可能コピーライター取得"""
        return self.persona_db.list_available_personas()
    
    def get_copywriter_profile(self, name: str) -> Optional[Dict]:
        """コピーライタープロファイル取得"""
        return self.persona_db.get_persona(name)

# デモ・テスト実行
async def run_production_demo():
    """本格システムデモ実行"""
    print("=== Production Copywriter AI System Demo ===\n")
    
    # システム初期化
    system = ProductionCopywriterAI(
        db_path='/Users/naoki/tcc_copyworks.db',
        analysis_path='/Users/naoki/copywriter_style_analysis_20250810_000147.json'
    )
    
    print("📋 Available Copywriters:")
    available = system.get_available_copywriters()
    for i, name in enumerate(available, 1):
        print(f"  {i}. {name}")
    
    if not available:
        print("  No copywriters available in database")
        return
    
    # テストケース実行
    test_copywriter = available[0]
    print(f"\n🎯 Testing with: {test_copywriter}")
    
    # プロフィール表示
    profile = system.get_copywriter_profile(test_copywriter)
    if profile:
        print(f"  Profile loaded: {len(profile.get('work_samples', []))} work samples available")
        print(f"  Style metrics: {list(profile.get('style_metrics', {}).keys())[:5]}")
    
    # コピー生成テスト
    print("\n🚀 Generating professional copy...")
    
    result = await system.create_professional_copy(
        copywriter_name=test_copywriter,
        product_service="プレミアム日本茶",
        target_audience="30-50代の品質重視層",
        content_type="雑誌広告",
        style_intensity=0.9,
        creativity_level=0.8,
        key_messages=["伝統の技術", "最高品質", "日本の心"],
        length_preference="medium"
    )
    
    # 結果表示
    print(f"\n✨ Generated Copy:")
    print(f"Primary: {result.primary_copy}")
    
    if result.alternative_versions:
        print(f"\nAlternatives:")
        for i, alt in enumerate(result.alternative_versions, 1):
            print(f"  {i}. {alt}")
    
    print(f"\n📊 Quality Scores:")
    print(f"  Style Accuracy: {result.style_accuracy_score:.1f}%")
    print(f"  Predicted Effectiveness: {result.predicted_effectiveness:.1f}%")
    print(f"  Readability: {result.readability_score:.1f}")
    print(f"  Emotional Impact: {result.emotional_impact_score:.1f}")
    print(f"  Confidence: {result.confidence_score:.1f}%")
    
    print(f"\n💡 Recommendations:")
    for rec in result.recommended_usage:
        print(f"  • {rec}")
    
    print(f"\n✅ Production demo completed!")
    return result

if __name__ == "__main__":
    # 本格システムデモ実行
    demo_result = asyncio.run(run_production_demo())