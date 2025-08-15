"""
Advanced Copywriter Style Analysis System
高度なコピーライター スタイル分析システム

実際の作品データを基にコピーライターのスタイルを
定量的・定性的に分析し、AIペルソナ生成に活用
"""

import json
import re
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import Counter, defaultdict
import unicodedata
from datetime import datetime

# 日本語形態素解析用（MeCabが利用できない場合のダミー実装も含む）
try:
    import MeCab
    MECAB_AVAILABLE = True
except ImportError:
    MECAB_AVAILABLE = False
    print("MeCab not available, using simplified analysis")

# MeCabクラス定義（importエラー回避）
if not MECAB_AVAILABLE:
    class MeCab:
        @staticmethod
        def Tagger(option):
            return None

@dataclass
class StyleMetrics:
    """コピーライター スタイル指標"""
    copywriter_name: str
    
    # 基本統計
    total_works: int
    avg_copy_length: float
    median_copy_length: float
    
    # 言語特徴
    vocabulary_richness: float  # 語彙の豊富さ
    readability_score: float    # 読みやすさスコア
    emotional_tone_score: float # 感情的トーン
    
    # 構造特徴
    avg_sentences_per_copy: float
    punctuation_frequency: Dict[str, float]
    
    # 内容特徴
    top_keywords: List[Tuple[str, int]]
    common_themes: List[str]
    industry_specialization: Dict[str, int]
    media_preference: Dict[str, int]
    
    # 時系列特徴
    career_evolution: List[Dict]
    active_period: Tuple[int, int]
    
    # 独自性指標
    uniqueness_score: float
    signature_phrases: List[str]

@dataclass
class CopyAnalysis:
    """個別コピー作品の分析結果"""
    entry_id: str
    copy_text: str
    copywriter: str
    
    # 基本指標
    length: int
    sentence_count: int
    word_count: int
    
    # 言語分析
    pos_distribution: Dict[str, int]  # 品詞分布
    keywords: List[str]
    emotional_words: List[str]
    
    # スタイル特徴
    tone: str  # 'formal', 'casual', 'emotional', 'rational'
    target_appeal: str  # 'logical', 'emotional', 'lifestyle'
    complexity: str  # 'simple', 'moderate', 'complex'

class CopywriterStyleAnalyzer:
    """コピーライター スタイル分析器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.mecab = None
        
        # MeCab初期化
        if MECAB_AVAILABLE:
            try:
                self.mecab = MeCab.Tagger('-Owakati')
                print("MeCab initialized successfully")
            except:
                print("MeCab initialization failed, using fallback")
        
        # 感情語辞書（簡易版）
        self.emotional_words = {
            'positive': ['美しい', '素晴らしい', '楽しい', '嬉しい', '愛', '幸せ', '喜び', '感動', '素敵', '最高'],
            'negative': ['悲しい', '辛い', '困難', '問題', '不安', '心配', '苦しい', '失望'],
            'neutral': ['普通', '一般', '標準', '通常', '平均']
        }
        
        # 業界キーワード辞書
        self.industry_keywords = {
            '食品・飲料': ['美味しい', '味', '食べる', '飲む', '料理', 'グルメ', '新鮮', '栄養'],
            'ファッション': ['着る', 'スタイル', 'おしゃれ', 'トレンド', 'コーディネート', 'ブランド'],
            '自動車': ['走る', 'ドライブ', '車', 'エンジン', '燃費', '安全', '性能'],
            '化粧品': ['美しさ', '美容', 'スキンケア', '肌', 'メイク', '若々しい'],
            'テクノロジー': ['革新', '技術', 'デジタル', 'AI', '未来', '効率', '便利']
        }
        
        print("CopywriterStyleAnalyzer initialized")
    
    def load_copyworks_data(self) -> List[Dict]:
        """データベースからコピー作品データを読み込み"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT entry_id, copy_text, copywriter, client, industry, 
                       media_type, year, award
                FROM copy_works 
                WHERE copy_text IS NOT NULL AND copy_text != ""
                ORDER BY copywriter, year
            ''')
            
            works = []
            for row in cursor.fetchall():
                works.append({
                    'entry_id': row[0],
                    'copy_text': row[1],
                    'copywriter': row[2],
                    'client': row[3],
                    'industry': row[4],
                    'media_type': row[5],
                    'year': row[6],
                    'award': row[7]
                })
            
            conn.close()
            print(f"Loaded {len(works)} copy works")
            return works
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return []
    
    def analyze_single_copy(self, copy_data: Dict) -> CopyAnalysis:
        """個別コピー作品の詳細分析"""
        text = copy_data['copy_text']
        
        # 基本統計
        length = len(text)
        sentence_count = len([s for s in re.split(r'[。！？]', text) if s.strip()])
        
        # 形態素解析
        if self.mecab and MECAB_AVAILABLE:
            words = self.mecab.parse(text).strip().split()
            word_count = len(words)
            # より詳細な品詞分析も可能
            pos_distribution = self._analyze_pos_distribution(text)
        else:
            # フォールバック: 簡易単語分割
            words = re.findall(r'[ぁ-んァ-ヶー一-龠]+', text)
            word_count = len(words)
            pos_distribution = {}
        
        # キーワード抽出
        keywords = self._extract_keywords(text, words)
        
        # 感情語抽出
        emotional_words = self._extract_emotional_words(text)
        
        # トーン判定
        tone = self._classify_tone(text, emotional_words)
        
        # ターゲット訴求判定
        target_appeal = self._classify_target_appeal(text)
        
        # 複雑さ判定
        complexity = self._classify_complexity(length, sentence_count, word_count)
        
        return CopyAnalysis(
            entry_id=copy_data['entry_id'],
            copy_text=text,
            copywriter=copy_data['copywriter'],
            length=length,
            sentence_count=sentence_count,
            word_count=word_count,
            pos_distribution=pos_distribution,
            keywords=keywords,
            emotional_words=emotional_words,
            tone=tone,
            target_appeal=target_appeal,
            complexity=complexity
        )
    
    def _analyze_pos_distribution(self, text: str) -> Dict[str, int]:
        """品詞分布分析（MeCab使用）"""
        if not self.mecab:
            return {}
        
        try:
            # 詳細な品詞分析の実装
            # 実際にはMeCabの形態素解析結果から品詞を抽出
            return {'noun': 0, 'verb': 0, 'adjective': 0, 'particle': 0}
        except:
            return {}
    
    def _extract_keywords(self, text: str, words: List[str]) -> List[str]:
        """キーワード抽出"""
        # TF-IDF的な手法で重要語を抽出（簡易実装）
        word_freq = Counter(words)
        # 頻度上位かつ意味のある語を選択
        keywords = [word for word, freq in word_freq.most_common(5) 
                   if len(word) > 1 and not re.match(r'^[ぁ-ん]*$', word)]
        return keywords[:3]
    
    def _extract_emotional_words(self, text: str) -> List[str]:
        """感情語抽出"""
        emotional = []
        for category, words in self.emotional_words.items():
            for word in words:
                if word in text:
                    emotional.append(f"{word}({category})")
        return emotional
    
    def _classify_tone(self, text: str, emotional_words: List[str]) -> str:
        """トーン分類"""
        if len(emotional_words) > 2:
            return 'emotional'
        elif '。' in text and '！' not in text and '？' not in text:
            return 'formal'
        elif '！' in text or 'だ' in text or 'である' in text:
            return 'assertive'
        else:
            return 'casual'
    
    def _classify_target_appeal(self, text: str) -> str:
        """訴求タイプ分類"""
        logical_indicators = ['効果', '結果', '実証', '科学', '研究', 'データ']
        emotional_indicators = ['感じ', '体験', '気持ち', '心', '愛', '幸せ']
        lifestyle_indicators = ['生活', '日常', 'ライフ', 'スタイル', '暮らし']
        
        logical_score = sum(1 for word in logical_indicators if word in text)
        emotional_score = sum(1 for word in emotional_indicators if word in text)
        lifestyle_score = sum(1 for word in lifestyle_indicators if word in text)
        
        if logical_score >= emotional_score and logical_score >= lifestyle_score:
            return 'logical'
        elif emotional_score >= lifestyle_score:
            return 'emotional'
        else:
            return 'lifestyle'
    
    def _classify_complexity(self, length: int, sentence_count: int, word_count: int) -> str:
        """複雑さ分類"""
        if length < 20 and sentence_count <= 1:
            return 'simple'
        elif length < 100 and sentence_count <= 3:
            return 'moderate'
        else:
            return 'complex'
    
    def analyze_copywriter_style(self, copywriter_name: str, works: List[Dict]) -> StyleMetrics:
        """特定コピーライターの総合スタイル分析"""
        copywriter_works = [w for w in works if w['copywriter'] == copywriter_name]
        
        if not copywriter_works:
            return None
        
        # 個別コピー分析
        copy_analyses = [self.analyze_single_copy(work) for work in copywriter_works]
        
        # 基本統計計算
        lengths = [analysis.length for analysis in copy_analyses]
        total_works = len(copywriter_works)
        avg_length = np.mean(lengths) if lengths else 0
        median_length = np.median(lengths) if lengths else 0
        
        # 語彙の豊富さ計算
        all_keywords = []
        for analysis in copy_analyses:
            all_keywords.extend(analysis.keywords)
        vocabulary_richness = len(set(all_keywords)) / len(all_keywords) if all_keywords else 0
        
        # 読みやすさスコア（簡易版）
        avg_sentences = np.mean([a.sentence_count for a in copy_analyses]) if copy_analyses else 0
        readability_score = max(0, 100 - avg_length/10 - avg_sentences*5)
        
        # 感情的トーン
        emotional_copies = sum(1 for a in copy_analyses if len(a.emotional_words) > 0)
        emotional_tone_score = (emotional_copies / total_works) * 100 if total_works > 0 else 0
        
        # 句読点頻度
        punctuation_freq = self._calculate_punctuation_frequency(copywriter_works)
        
        # トップキーワード
        keyword_counter = Counter()
        for analysis in copy_analyses:
            keyword_counter.update(analysis.keywords)
        top_keywords = keyword_counter.most_common(10)
        
        # テーマ分析
        common_themes = self._extract_common_themes(copy_analyses)
        
        # 業界特化度
        industry_dist = Counter(work['industry'] for work in copywriter_works if work['industry'])
        
        # メディア選好
        media_dist = Counter(work['media_type'] for work in copywriter_works if work['media_type'])
        
        # キャリア進化
        career_evolution = self._analyze_career_evolution(copywriter_works)
        
        # 活動期間
        years = [work['year'] for work in copywriter_works if work['year']]
        active_period = (min(years), max(years)) if years else (0, 0)
        
        # 独自性スコア
        uniqueness_score = self._calculate_uniqueness_score(copywriter_name, copy_analyses, works)
        
        # シグネチャーフレーズ
        signature_phrases = self._extract_signature_phrases(copy_analyses)
        
        return StyleMetrics(
            copywriter_name=copywriter_name,
            total_works=total_works,
            avg_copy_length=avg_length,
            median_copy_length=median_length,
            vocabulary_richness=vocabulary_richness,
            readability_score=readability_score,
            emotional_tone_score=emotional_tone_score,
            avg_sentences_per_copy=avg_sentences,
            punctuation_frequency=punctuation_freq,
            top_keywords=top_keywords,
            common_themes=common_themes,
            industry_specialization=dict(industry_dist),
            media_preference=dict(media_dist),
            career_evolution=career_evolution,
            active_period=active_period,
            uniqueness_score=uniqueness_score,
            signature_phrases=signature_phrases
        )
    
    def _calculate_punctuation_frequency(self, works: List[Dict]) -> Dict[str, float]:
        """句読点使用頻度計算"""
        punctuation_marks = {'。': 0, '、': 0, '！': 0, '？': 0, '〜': 0}
        total_chars = 0
        
        for work in works:
            text = work['copy_text']
            total_chars += len(text)
            for mark in punctuation_marks:
                punctuation_marks[mark] += text.count(mark)
        
        # 100文字あたりの出現頻度
        return {mark: (count / total_chars * 100) if total_chars > 0 else 0 
                for mark, count in punctuation_marks.items()}
    
    def _extract_common_themes(self, analyses: List[CopyAnalysis]) -> List[str]:
        """共通テーマ抽出"""
        # 訴求タイプの分布から主要テーマを判定
        appeal_counter = Counter(analysis.target_appeal for analysis in analyses)
        tone_counter = Counter(analysis.tone for analysis in analyses)
        
        themes = []
        if appeal_counter.most_common(1):
            themes.append(f"主要訴求: {appeal_counter.most_common(1)[0][0]}")
        if tone_counter.most_common(1):
            themes.append(f"基調トーン: {tone_counter.most_common(1)[0][0]}")
        
        return themes
    
    def _analyze_career_evolution(self, works: List[Dict]) -> List[Dict]:
        """キャリア進化分析"""
        # 年代別の作品傾向変化を分析
        year_groups = defaultdict(list)
        for work in works:
            if work['year']:
                decade = (work['year'] // 10) * 10
                year_groups[decade].append(work)
        
        evolution = []
        for decade, decade_works in sorted(year_groups.items()):
            avg_length = np.mean([len(work['copy_text']) for work in decade_works])
            evolution.append({
                'period': f"{decade}年代",
                'works_count': len(decade_works),
                'avg_length': avg_length,
                'themes': list(set(work['industry'] for work in decade_works if work['industry']))[:3]
            })
        
        return evolution
    
    def _calculate_uniqueness_score(self, copywriter_name: str, analyses: List[CopyAnalysis], all_works: List[Dict]) -> float:
        """独自性スコア計算"""
        # 他のコピーライターとの差異化度を測定
        copywriter_keywords = set()
        for analysis in analyses:
            copywriter_keywords.update(analysis.keywords)
        
        # 他のコピーライターのキーワードを収集
        other_keywords = set()
        for work in all_works:
            if work['copywriter'] != copywriter_name:
                # 簡易キーワード抽出
                words = re.findall(r'[ぁ-んァ-ヶー一-龠]+', work['copy_text'])
                word_freq = Counter(words)
                keywords = [word for word, freq in word_freq.most_common(3) if len(word) > 1]
                other_keywords.update(keywords)
        
        # Jaccard係数の逆数（独自性の指標）
        if not copywriter_keywords or not other_keywords:
            return 50.0
        
        intersection = len(copywriter_keywords & other_keywords)
        union = len(copywriter_keywords | other_keywords)
        jaccard = intersection / union if union > 0 else 0
        uniqueness = (1 - jaccard) * 100
        
        return uniqueness
    
    def _extract_signature_phrases(self, analyses: List[CopyAnalysis]) -> List[str]:
        """シグネチャーフレーズ抽出"""
        # 頻出する特徴的なフレーズを抽出
        all_text = ' '.join(analysis.copy_text for analysis in analyses)
        
        # 2-3文字の頻出パターンを探索
        phrases = []
        for length in [2, 3, 4]:
            for i in range(len(all_text) - length + 1):
                phrase = all_text[i:i+length]
                if re.match(r'^[ぁ-んァ-ヶー一-龠]+$', phrase) and all_text.count(phrase) >= 2:
                    phrases.append(phrase)
        
        # 頻度でソートして上位を返す
        phrase_counter = Counter(phrases)
        return [phrase for phrase, count in phrase_counter.most_common(5)]
    
    def generate_comprehensive_report(self) -> Dict:
        """包括的分析レポート生成"""
        works = self.load_copyworks_data()
        if not works:
            return {"error": "No data available"}
        
        # 全コピーライターの分析
        copywriters = list(set(work['copywriter'] for work in works))
        style_metrics = {}
        
        print(f"Analyzing {len(copywriters)} copywriters...")
        
        for copywriter in copywriters:
            print(f"Analyzing: {copywriter}")
            metrics = self.analyze_copywriter_style(copywriter, works)
            if metrics:
                style_metrics[copywriter] = asdict(metrics)
        
        # 全体統計
        overall_stats = {
            'total_copywriters': len(copywriters),
            'total_works': len(works),
            'analysis_date': datetime.now().isoformat(),
            'avg_works_per_copywriter': len(works) / len(copywriters) if copywriters else 0
        }
        
        # ランキング生成
        rankings = self._generate_rankings(style_metrics)
        
        return {
            'overall_statistics': overall_stats,
            'copywriter_analyses': style_metrics,
            'rankings': rankings,
            'methodology': self._get_methodology_description()
        }
    
    def _generate_rankings(self, style_metrics: Dict) -> Dict:
        """各種ランキング生成"""
        rankings = {}
        
        # 語彙豊富度ランキング
        vocab_ranking = sorted(
            [(name, data['vocabulary_richness']) for name, data in style_metrics.items()],
            key=lambda x: x[1], reverse=True
        )
        rankings['vocabulary_richness'] = vocab_ranking[:10]
        
        # 感情表現度ランキング
        emotion_ranking = sorted(
            [(name, data['emotional_tone_score']) for name, data in style_metrics.items()],
            key=lambda x: x[1], reverse=True
        )
        rankings['emotional_tone'] = emotion_ranking[:10]
        
        # 独自性ランキング
        unique_ranking = sorted(
            [(name, data['uniqueness_score']) for name, data in style_metrics.items()],
            key=lambda x: x[1], reverse=True
        )
        rankings['uniqueness'] = unique_ranking[:10]
        
        # 作品数ランキング
        works_ranking = sorted(
            [(name, data['total_works']) for name, data in style_metrics.items()],
            key=lambda x: x[1], reverse=True
        )
        rankings['productivity'] = works_ranking[:10]
        
        return rankings
    
    def _get_methodology_description(self) -> Dict:
        """分析手法説明"""
        return {
            'vocabulary_richness': 'ユニークキーワード数 / 総キーワード数',
            'readability_score': '100 - 平均文字数/10 - 平均文数*5',
            'emotional_tone_score': '感情語を含む作品の割合 * 100',
            'uniqueness_score': '(1 - 他作者との共通キーワード率) * 100',
            'limitations': [
                'サンプル数による精度の制約',
                '形態素解析の精度依存',
                '業界・時代背景の考慮不足'
            ]
        }
    
    def export_analysis_results(self, report: Dict, filename: str = None):
        """分析結果エクスポート"""
        if filename is None:
            filename = f"/Users/naoki/copywriter_style_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"Analysis results exported to: {filename}")
        return filename

# デモ実行
def run_style_analysis_demo():
    """スタイル分析デモ実行"""
    print("=== Copywriter Style Analysis Demo ===\n")
    
    analyzer = CopywriterStyleAnalyzer('/Users/naoki/tcc_copyworks.db')
    
    # 包括的分析実行
    report = analyzer.generate_comprehensive_report()
    
    if 'error' in report:
        print(f"Error: {report['error']}")
        return
    
    # 結果表示
    print("📊 Analysis Results Summary:")
    print(f"  Total Copywriters Analyzed: {report['overall_statistics']['total_copywriters']}")
    print(f"  Total Works Analyzed: {report['overall_statistics']['total_works']}")
    print(f"  Avg Works per Copywriter: {report['overall_statistics']['avg_works_per_copywriter']:.1f}")
    
    print("\n🏆 Top Rankings:")
    
    if 'vocabulary_richness' in report['rankings']:
        print("\n  語彙豊富度 TOP3:")
        for i, (name, score) in enumerate(report['rankings']['vocabulary_richness'][:3], 1):
            print(f"    {i}. {name}: {score:.3f}")
    
    if 'emotional_tone' in report['rankings']:
        print("\n  感情表現度 TOP3:")
        for i, (name, score) in enumerate(report['rankings']['emotional_tone'][:3], 1):
            print(f"    {i}. {name}: {score:.1f}%")
    
    if 'uniqueness' in report['rankings']:
        print("\n  独自性スコア TOP3:")
        for i, (name, score) in enumerate(report['rankings']['uniqueness'][:3], 1):
            print(f"    {i}. {name}: {score:.1f}")
    
    # 詳細分析例
    if report['copywriter_analyses']:
        sample_writer = list(report['copywriter_analyses'].keys())[0]
        sample_analysis = report['copywriter_analyses'][sample_writer]
        
        print(f"\n📝 Sample Analysis - {sample_writer}:")
        print(f"  Total Works: {sample_analysis['total_works']}")
        print(f"  Avg Copy Length: {sample_analysis['avg_copy_length']:.1f} characters")
        print(f"  Readability Score: {sample_analysis['readability_score']:.1f}")
        print(f"  Top Keywords: {[kw[0] for kw in sample_analysis['top_keywords'][:3]]}")
        print(f"  Common Themes: {sample_analysis['common_themes']}")
        print(f"  Active Period: {sample_analysis['active_period'][0]}-{sample_analysis['active_period'][1]}")
    
    # 結果エクスポート
    filename = analyzer.export_analysis_results(report)
    
    print(f"\n✅ Style analysis completed!")
    print(f"📁 Detailed report saved to: {filename}")
    
    return report

if __name__ == "__main__":
    demo_report = run_style_analysis_demo()