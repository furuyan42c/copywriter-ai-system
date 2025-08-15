"""
Final System Validation and Testing
最終システム検証とテスト

完成したコピーライターAIシステムの
包括的なテストと性能検証
"""

import json
import asyncio
import time
from typing import Dict, List, Tuple
from dataclasses import asdict
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import logging

# 完成システムのインポート
from advanced_copywriter_ai_system import ProductionCopywriterAI, AdvancedCopywritingRequest

class SystemValidator:
    """システム検証クラス"""
    
    def __init__(self, system: ProductionCopywriterAI):
        self.system = system
        self.test_results = []
        self.performance_metrics = {}
        
        # テストケース定義
        self.test_cases = [
            {
                'name': 'Premium Food Product',
                'copywriter': '糸井重里',
                'product': '有機野菜ジュース',
                'target': '健康志向の30代女性',
                'content_type': 'Web広告',
                'key_messages': ['自然の恵み', '健康美容', '毎日の習慣'],
                'expected_elements': ['親しみやすい表現', '生活提案', '温かみ']
            },
            {
                'name': 'Technology Product', 
                'copywriter': '仲畑貴志',
                'product': 'スマートフォンアプリ',
                'target': '20代のデジタルネイティブ',
                'content_type': 'SNS広告',
                'key_messages': ['簡単操作', '革新的', 'つながり'],
                'expected_elements': ['シンプル表現', '印象的', '普遍的']
            },
            {
                'name': 'Luxury Brand',
                'copywriter': '糸井重里',
                'product': 'プレミアム時計',
                'target': '40-50代男性経営層',
                'content_type': '雑誌広告',
                'key_messages': ['職人技', '伝統', 'ステータス'],
                'expected_elements': ['上質な表現', 'ブランド価値', '信頼感']
            }
        ]
        
        logging.info("System validator initialized with test cases")
    
    async def run_comprehensive_validation(self) -> Dict:
        """包括的システム検証実行"""
        
        print("🔍 Starting Comprehensive System Validation")
        print("=" * 60)
        
        validation_results = {
            'start_time': datetime.now().isoformat(),
            'system_info': await self.validate_system_setup(),
            'functionality_tests': await self.run_functionality_tests(),
            'performance_tests': await self.run_performance_tests(),
            'quality_tests': await self.run_quality_tests(),
            'stress_tests': await self.run_stress_tests(),
            'final_assessment': None
        }
        
        # 最終評価
        validation_results['final_assessment'] = self.generate_final_assessment(validation_results)
        validation_results['end_time'] = datetime.now().isoformat()
        
        return validation_results
    
    async def validate_system_setup(self) -> Dict:
        """システム設定検証"""
        print("\n📋 System Setup Validation")
        
        setup_validation = {
            'available_copywriters': len(self.system.get_available_copywriters()),
            'copywriters_list': self.system.get_available_copywriters(),
            'database_connectivity': False,
            'style_analysis_loaded': False,
            'api_availability': hasattr(self.system.generator, 'client') and self.system.generator.client is not None
        }
        
        # データベース接続テスト
        try:
            profiles = [self.system.get_copywriter_profile(name) 
                       for name in setup_validation['copywriters_list']]
            setup_validation['database_connectivity'] = any(p is not None for p in profiles)
        except Exception as e:
            logging.error(f"Database connectivity test failed: {e}")
        
        # スタイル分析データ確認
        try:
            if setup_validation['copywriters_list']:
                first_profile = self.system.get_copywriter_profile(setup_validation['copywriters_list'][0])
                setup_validation['style_analysis_loaded'] = (
                    first_profile is not None and 
                    'style_metrics' in first_profile
                )
        except Exception as e:
            logging.error(f"Style analysis validation failed: {e}")
        
        print(f"  ✓ Available Copywriters: {setup_validation['available_copywriters']}")
        print(f"  ✓ Database Connectivity: {setup_validation['database_connectivity']}")
        print(f"  ✓ Style Analysis Loaded: {setup_validation['style_analysis_loaded']}")
        print(f"  ✓ API Availability: {setup_validation['api_availability']}")
        
        return setup_validation
    
    async def run_functionality_tests(self) -> Dict:
        """機能テスト実行"""
        print("\n⚙️  Functionality Tests")
        
        functionality_results = {
            'basic_generation': False,
            'persona_switching': False,
            'style_consistency': False,
            'error_handling': False,
            'test_details': []
        }
        
        # 基本生成テスト
        try:
            if self.system.get_available_copywriters():
                test_copywriter = self.system.get_available_copywriters()[0]
                result = await self.system.create_professional_copy(
                    copywriter_name=test_copywriter,
                    product_service="テスト商品",
                    target_audience="テスト層",
                    content_type="テスト広告"
                )
                functionality_results['basic_generation'] = bool(result.primary_copy)
                print(f"  ✓ Basic Generation: {'PASS' if functionality_results['basic_generation'] else 'FAIL'}")
            
        except Exception as e:
            logging.error(f"Basic generation test failed: {e}")
            print(f"  ✗ Basic Generation: FAIL - {e}")
        
        # ペルソナ切り替えテスト
        try:
            available = self.system.get_available_copywriters()
            if len(available) >= 2:
                results = []
                for copywriter in available[:2]:
                    result = await self.system.create_professional_copy(
                        copywriter_name=copywriter,
                        product_service="同一商品",
                        target_audience="同一ターゲット", 
                        content_type="同一媒体"
                    )
                    results.append(result.primary_copy)
                
                # 異なる出力が生成されているかチェック
                functionality_results['persona_switching'] = len(set(results)) > 1
                print(f"  ✓ Persona Switching: {'PASS' if functionality_results['persona_switching'] else 'FAIL'}")
            
        except Exception as e:
            logging.error(f"Persona switching test failed: {e}")
            print(f"  ✗ Persona Switching: FAIL - {e}")
        
        # エラーハンドリングテスト
        try:
            # 存在しないコピーライターでのテスト
            try:
                await self.system.create_professional_copy(
                    copywriter_name="存在しないコピーライター",
                    product_service="テスト",
                    target_audience="テスト",
                    content_type="テスト"
                )
                functionality_results['error_handling'] = False
            except (ValueError, KeyError):
                functionality_results['error_handling'] = True
            
            print(f"  ✓ Error Handling: {'PASS' if functionality_results['error_handling'] else 'FAIL'}")
            
        except Exception as e:
            logging.error(f"Error handling test failed: {e}")
            print(f"  ✗ Error Handling: FAIL - {e}")
        
        return functionality_results
    
    async def run_performance_tests(self) -> Dict:
        """パフォーマンステスト実行"""
        print("\n🚀 Performance Tests")
        
        performance_results = {
            'generation_speed': [],
            'memory_usage': 'Not measured',
            'concurrent_handling': False,
            'average_response_time': 0.0
        }
        
        # 生成速度テスト
        if self.system.get_available_copywriters():
            test_copywriter = self.system.get_available_copywriters()[0]
            
            for i in range(3):
                start_time = time.time()
                try:
                    result = await self.system.create_professional_copy(
                        copywriter_name=test_copywriter,
                        product_service=f"パフォーマンステスト商品{i}",
                        target_audience="テスト層",
                        content_type="テスト広告"
                    )
                    end_time = time.time()
                    response_time = end_time - start_time
                    performance_results['generation_speed'].append(response_time)
                    print(f"  ✓ Generation {i+1}: {response_time:.2f}s")
                    
                except Exception as e:
                    logging.error(f"Performance test {i} failed: {e}")
                    performance_results['generation_speed'].append(None)
        
        # 平均応答時間計算
        valid_times = [t for t in performance_results['generation_speed'] if t is not None]
        if valid_times:
            performance_results['average_response_time'] = sum(valid_times) / len(valid_times)
            print(f"  📊 Average Response Time: {performance_results['average_response_time']:.2f}s")
        
        return performance_results
    
    async def run_quality_tests(self) -> Dict:
        """品質テスト実行"""
        print("\n🎯 Quality Tests")
        
        quality_results = {
            'test_cases': [],
            'overall_quality_score': 0.0,
            'style_accuracy_average': 0.0,
            'effectiveness_average': 0.0
        }
        
        total_style_accuracy = 0
        total_effectiveness = 0
        valid_tests = 0
        
        for i, test_case in enumerate(self.test_cases):
            print(f"  🧪 Test Case {i+1}: {test_case['name']}")
            
            case_result = {
                'name': test_case['name'],
                'copywriter': test_case['copywriter'],
                'success': False,
                'generated_copy': '',
                'quality_scores': {},
                'style_analysis': {}
            }
            
            try:
                # コピーライターが利用可能かチェック
                if test_case['copywriter'] not in self.system.get_available_copywriters():
                    print(f"    ⚠️  Copywriter {test_case['copywriter']} not available, using fallback")
                    test_case['copywriter'] = self.system.get_available_copywriters()[0]
                
                result = await self.system.create_professional_copy(
                    copywriter_name=test_case['copywriter'],
                    product_service=test_case['product'],
                    target_audience=test_case['target'],
                    content_type=test_case['content_type'],
                    key_messages=test_case['key_messages'],
                    style_intensity=0.8,
                    creativity_level=0.7
                )
                
                case_result['success'] = True
                case_result['generated_copy'] = result.primary_copy
                case_result['quality_scores'] = {
                    'style_accuracy': result.style_accuracy_score,
                    'effectiveness': result.predicted_effectiveness,
                    'readability': result.readability_score,
                    'emotional_impact': result.emotional_impact_score,
                    'confidence': result.confidence_score
                }
                
                # 期待要素の確認
                expected_found = sum(1 for element in test_case['expected_elements'] 
                                   if any(keyword in result.primary_copy.lower() 
                                         for keyword in element.lower().split()))
                
                case_result['style_analysis'] = {
                    'expected_elements_found': expected_found,
                    'total_expected_elements': len(test_case['expected_elements']),
                    'key_messages_included': sum(1 for msg in test_case['key_messages']
                                               if msg in result.primary_copy)
                }
                
                # 統計に追加
                total_style_accuracy += result.style_accuracy_score
                total_effectiveness += result.predicted_effectiveness
                valid_tests += 1
                
                print(f"    ✓ Generated: {result.primary_copy[:50]}...")
                print(f"    📊 Quality: Style={result.style_accuracy_score:.1f}%, Effectiveness={result.predicted_effectiveness:.1f}%")
                
            except Exception as e:
                logging.error(f"Quality test case {i+1} failed: {e}")
                print(f"    ✗ Failed: {e}")
            
            quality_results['test_cases'].append(case_result)
        
        # 平均品質スコア計算
        if valid_tests > 0:
            quality_results['style_accuracy_average'] = total_style_accuracy / valid_tests
            quality_results['effectiveness_average'] = total_effectiveness / valid_tests
            quality_results['overall_quality_score'] = (
                quality_results['style_accuracy_average'] + 
                quality_results['effectiveness_average']
            ) / 2
        
        print(f"\n  📈 Overall Quality Summary:")
        print(f"    Average Style Accuracy: {quality_results['style_accuracy_average']:.1f}%")
        print(f"    Average Effectiveness: {quality_results['effectiveness_average']:.1f}%")
        print(f"    Overall Quality Score: {quality_results['overall_quality_score']:.1f}%")
        
        return quality_results
    
    async def run_stress_tests(self) -> Dict:
        """ストレステスト実行"""
        print("\n💪 Stress Tests")
        
        stress_results = {
            'concurrent_requests': False,
            'large_input_handling': False,
            'rapid_successive_calls': False,
            'edge_cases': []
        }
        
        # 大量入力テスト
        try:
            if self.system.get_available_copywriters():
                long_product_desc = "非常に長い商品説明" * 100
                result = await self.system.create_professional_copy(
                    copywriter_name=self.system.get_available_copywriters()[0],
                    product_service=long_product_desc,
                    target_audience="テスト層",
                    content_type="テスト広告"
                )
                stress_results['large_input_handling'] = bool(result.primary_copy)
                print(f"  ✓ Large Input Handling: {'PASS' if stress_results['large_input_handling'] else 'FAIL'}")
            
        except Exception as e:
            logging.error(f"Large input test failed: {e}")
            print(f"  ✗ Large Input Handling: FAIL - {e}")
        
        # 連続呼び出しテスト
        try:
            if self.system.get_available_copywriters():
                rapid_results = []
                for i in range(5):
                    result = await self.system.create_professional_copy(
                        copywriter_name=self.system.get_available_copywriters()[0],
                        product_service=f"連続テスト商品{i}",
                        target_audience="テスト層",
                        content_type="テスト広告"
                    )
                    rapid_results.append(bool(result.primary_copy))
                
                stress_results['rapid_successive_calls'] = all(rapid_results)
                print(f"  ✓ Rapid Successive Calls: {'PASS' if stress_results['rapid_successive_calls'] else 'FAIL'}")
            
        except Exception as e:
            logging.error(f"Rapid successive calls test failed: {e}")
            print(f"  ✗ Rapid Successive Calls: FAIL - {e}")
        
        return stress_results
    
    def generate_final_assessment(self, validation_results: Dict) -> Dict:
        """最終評価生成"""
        
        assessment = {
            'overall_status': 'UNKNOWN',
            'system_readiness': 'NOT_READY',
            'strengths': [],
            'weaknesses': [],
            'recommendations': [],
            'production_readiness_score': 0.0
        }
        
        # 各テスト結果の評価
        system_info = validation_results.get('system_info', {})
        functionality = validation_results.get('functionality_tests', {})
        performance = validation_results.get('performance_tests', {})
        quality = validation_results.get('quality_tests', {})
        stress = validation_results.get('stress_tests', {})
        
        # 強み
        if system_info.get('database_connectivity'):
            assessment['strengths'].append("データベース統合機能")
        
        if system_info.get('style_analysis_loaded'):
            assessment['strengths'].append("スタイル分析データ活用")
        
        if functionality.get('basic_generation'):
            assessment['strengths'].append("基本的なコピー生成機能")
        
        if functionality.get('persona_switching'):
            assessment['strengths'].append("ペルソナ切り替え機能")
        
        if quality.get('overall_quality_score', 0) > 50:
            assessment['strengths'].append("品質スコアが基準値を超過")
        
        # 弱み・推奨事項
        if not system_info.get('api_availability'):
            assessment['weaknesses'].append("AI API接続不可（フォールバック動作）")
            assessment['recommendations'].append("Claude API接続の設定")
        
        if system_info.get('available_copywriters', 0) < 5:
            assessment['weaknesses'].append("利用可能コピーライター数が少ない")
            assessment['recommendations'].append("TCCデータベースからの実データ収集")
        
        if quality.get('style_accuracy_average', 0) < 70:
            assessment['weaknesses'].append("スタイル再現精度が不足")
            assessment['recommendations'].append("ペルソナプロファイルの詳細化")
        
        if not functionality.get('error_handling'):
            assessment['weaknesses'].append("エラーハンドリングが不十分")
            assessment['recommendations'].append("例外処理の強化")
        
        # 本格運用準備度スコア算出
        scores = []
        
        if system_info.get('database_connectivity'): scores.append(20)
        if system_info.get('style_analysis_loaded'): scores.append(15)
        if functionality.get('basic_generation'): scores.append(25)
        if functionality.get('persona_switching'): scores.append(15)
        if quality.get('overall_quality_score', 0) > 50: scores.append(25)
        
        assessment['production_readiness_score'] = sum(scores)
        
        # 総合評価判定
        if assessment['production_readiness_score'] >= 80:
            assessment['overall_status'] = 'EXCELLENT'
            assessment['system_readiness'] = 'PRODUCTION_READY'
        elif assessment['production_readiness_score'] >= 60:
            assessment['overall_status'] = 'GOOD'
            assessment['system_readiness'] = 'STAGING_READY'
        elif assessment['production_readiness_score'] >= 40:
            assessment['overall_status'] = 'FAIR'
            assessment['system_readiness'] = 'DEVELOPMENT_READY'
        else:
            assessment['overall_status'] = 'POOR'
            assessment['system_readiness'] = 'NOT_READY'
        
        return assessment
    
    def generate_validation_report(self, results: Dict) -> str:
        """検証レポート生成"""
        
        timestamp = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        
        report = f"""
# コピーライターAIシステム - 最終検証レポート
## 検証日時: {timestamp}

## 🎯 総合評価
**システム状態**: {results['final_assessment']['overall_status']}
**運用準備度**: {results['final_assessment']['system_readiness']}
**準備度スコア**: {results['final_assessment']['production_readiness_score']}/100

## ✅ システム強み
{chr(10).join(f'• {strength}' for strength in results['final_assessment']['strengths'])}

## ⚠️  改善点
{chr(10).join(f'• {weakness}' for weakness in results['final_assessment']['weaknesses'])}

## 💡 推奨事項
{chr(10).join(f'• {rec}' for rec in results['final_assessment']['recommendations'])}

## 📊 詳細テスト結果

### システム設定
- 利用可能コピーライター: {results['system_info']['available_copywriters']}人
- データベース接続: {'✓' if results['system_info']['database_connectivity'] else '✗'}
- スタイル分析データ: {'✓' if results['system_info']['style_analysis_loaded'] else '✗'}
- API接続: {'✓' if results['system_info']['api_availability'] else '✗'}

### 機能テスト
- 基本生成: {'PASS' if results['functionality_tests']['basic_generation'] else 'FAIL'}
- ペルソナ切替: {'PASS' if results['functionality_tests']['persona_switching'] else 'FAIL'}
- エラー処理: {'PASS' if results['functionality_tests']['error_handling'] else 'FAIL'}

### 品質テスト
- 平均スタイル精度: {results['quality_tests']['style_accuracy_average']:.1f}%
- 平均効果予測: {results['quality_tests']['effectiveness_average']:.1f}%
- 総合品質スコア: {results['quality_tests']['overall_quality_score']:.1f}%

### パフォーマンス
- 平均応答時間: {results['performance_tests']['average_response_time']:.2f}秒
- 生成成功率: {len([t for t in results['performance_tests']['generation_speed'] if t is not None])}/{len(results['performance_tests']['generation_speed'])}

## 🏁 結論
{'本システムは現時点で基本的な機能を実現しており、さらなるデータ収集とAPI統合により本格運用レベルに到達可能です。' if results['final_assessment']['production_readiness_score'] >= 40 else '基本機能は動作するものの、本格運用にはさらなる開発が必要です。'}

---
*このレポートは自動生成されました*
        """.strip()
        
        return report

async def run_final_validation():
    """最終検証実行"""
    print("🚀 Final System Validation and Testing")
    print("=" * 80)
    
    # システム初期化
    system = ProductionCopywriterAI(
        db_path='/Users/naoki/tcc_copyworks.db',
        analysis_path='/Users/naoki/copywriter_style_analysis_20250810_000147.json'
    )
    
    # 検証器初期化
    validator = SystemValidator(system)
    
    # 包括的検証実行
    results = await validator.run_comprehensive_validation()
    
    # レポート生成
    report = validator.generate_validation_report(results)
    
    # ファイル保存
    report_filename = f"/Users/naoki/final_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    results_filename = f"/Users/naoki/validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 最終サマリー表示
    print("\n" + "=" * 80)
    print("🏆 FINAL SYSTEM VALIDATION COMPLETE")
    print("=" * 80)
    
    assessment = results['final_assessment']
    print(f"📋 Overall Status: {assessment['overall_status']}")
    print(f"🎯 System Readiness: {assessment['system_readiness']}")
    print(f"📊 Readiness Score: {assessment['production_readiness_score']}/100")
    
    print(f"\n📄 Reports Generated:")
    print(f"  • Validation Report: {report_filename}")
    print(f"  • Detailed Results: {results_filename}")
    
    if assessment['production_readiness_score'] >= 60:
        print(f"\n🎉 SYSTEM READY FOR NEXT PHASE!")
    else:
        print(f"\n⚠️  SYSTEM REQUIRES FURTHER DEVELOPMENT")
    
    print("=" * 80)
    
    return results, report

if __name__ == "__main__":
    # 最終検証実行
    validation_results, validation_report = asyncio.run(run_final_validation())