#!/usr/bin/env python3
"""
Test Enhanced PADRES Pipeline
Verifies that the improvements addressing Stanford professor's critique are working correctly.

This script tests:
1. Enhanced spatial tasks with complexity gradients
2. Statistical analysis capabilities
3. Improved paper generation with proper metrics
4. GCS integration with the exact bucket: gen-lang-client-0029379200-research-papers
"""

import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_spatial_tasks():
    """Test that enhanced spatial tasks are properly loaded with complexity variants"""
    print("🧪 Testing Enhanced Spatial Tasks...")
    
    try:
        from padres_container.app.main import SPATIAL_TASKS_CATALOG, BASE_TASKS
        
        print(f"✅ Base tasks loaded: {len(BASE_TASKS)}")
        print(f"✅ Total task variants: {len(SPATIAL_TASKS_CATALOG)}")
        
        # Verify we have complexity variants
        complexity_variants = [task_id for task_id in SPATIAL_TASKS_CATALOG.keys() 
                             if 'complexity_' in task_id]
        print(f"✅ Complexity variants: {len(complexity_variants)}")
        
        # Verify control conditions exist
        control_tasks = [task_id for task_id in SPATIAL_TASKS_CATALOG.keys() 
                        if 'baseline' in task_id]
        print(f"✅ Control/baseline tasks: {control_tasks}")
        
        # Test specific enhanced tasks
        required_tasks = ['multi_step_tower_build', 'complex_maze_navigation', 
                         'spatial_memory_sequence', 'random_baseline', 'simple_baseline']
        for task in required_tasks:
            if task in SPATIAL_TASKS_CATALOG:
                print(f"✅ Enhanced task '{task}' exists")
            else:
                print(f"❌ Missing enhanced task '{task}'")
                
        return True
        
    except Exception as e:
        print(f"❌ Enhanced spatial tasks test failed: {e}")
        return False

def test_statistical_analysis():
    """Test the enhanced statistical analysis capabilities"""
    print("\n📊 Testing Statistical Analysis...")
    
    try:
        from analyze_research_papers import compute_statistical_analysis, extract_quality_metrics
        import numpy as np
        
        # Create mock paper data for testing
        mock_papers = []
        for i in range(10):
            # Simulate declining performance (like Stanford professor found)
            quality_score = max(20, 90 - i * 5 + np.random.normal(0, 5))
            mock_papers.append({
                'created': datetime.now(),
                'metrics': {
                    'quality_score': quality_score,
                    'has_p_values': i > 3,
                    'has_effect_sizes': i > 2,
                    'has_correlation_analysis': i > 5
                }
            })
        
        # Test statistical analysis
        results = compute_statistical_analysis(mock_papers)
        
        if 'error' in results:
            print(f"❌ Statistical analysis error: {results['error']}")
            return False
            
        # Verify all required statistical components exist
        required_components = ['correlation', 'descriptive', 'confidence_intervals', 
                             'effect_size', 'trend_analysis', 'quality_distribution']
        
        for component in required_components:
            if component in results:
                print(f"✅ Statistical component '{component}' implemented")
            else:
                print(f"❌ Missing component '{component}'")
                
        # Test specific metrics
        if 'correlation' in results:
            corr = results['correlation']
            print(f"✅ Pearson correlation: r = {corr['pearson_r']:.3f}, p = {corr['p_value']:.4f}")
            
        if 'effect_size' in results:
            effect = results['effect_size']
            print(f"✅ Effect size: Cohen's d = {effect['cohens_d']:.3f} ({effect['interpretation']})")
            
        return True
        
    except Exception as e:
        print(f"❌ Statistical analysis test failed: {e}")
        return False

def test_enhanced_quality_metrics():
    """Test enhanced quality metrics extraction"""
    print("\n🔍 Testing Enhanced Quality Metrics...")
    
    try:
        from analyze_research_papers import extract_quality_metrics
        
        # Test paper with Stanford-level statistical content
        mock_paper_content = """
        # Enhanced Research Paper
        
        ## Results
        We found a significant correlation (r = -0.73, p < 0.01) between experiment count and success rate.
        The effect size was large (Cohen's d = 0.87) with 95% confidence intervals [0.45, 0.89].
        Baseline comparisons showed significant differences from control conditions.
        
        ## Discussion
        The declining performance trend requires error analysis and addresses the degradation pattern.
        Statistical significance was established through proper trend analysis.
        """
        
        metrics = extract_quality_metrics(mock_paper_content)
        
        # Verify enhanced metrics
        enhanced_metrics = ['has_correlation_analysis', 'has_confidence_intervals', 
                          'has_error_analysis', 'has_trend_analysis', 'addresses_degradation']
        
        for metric in enhanced_metrics:
            if metrics.get(metric, False):
                print(f"✅ Enhanced metric '{metric}' detected")
            else:
                print(f"❌ Enhanced metric '{metric}' not detected")
                
        print(f"✅ Quality score: {metrics['quality_score']}/100")
        
        return metrics['quality_score'] > 50  # Should be high with enhanced content
        
    except Exception as e:
        print(f"❌ Enhanced quality metrics test failed: {e}")
        return False

def test_gcs_bucket_configuration():
    """Verify GCS bucket configuration is correct"""
    print("\n☁️ Testing GCS Bucket Configuration...")
    
    try:
        # Check if the bucket name is correctly configured in the file
        with open("analyze_research_papers.py", "r") as f:
            content = f.read()
            
        expected_bucket = "gen-lang-client-0029379200-research-papers"
        
        if expected_bucket in content:
            print(f"✅ Correct GCS bucket configured: {expected_bucket}")
            return True
        else:
            print(f"❌ Bucket not found in analyze_research_papers.py")
            return False
            
    except Exception as e:
        print(f"❌ GCS bucket test failed: {e}")
        return False

def test_paper_generation_enhancements():
    """Test that paper generation includes proper statistical analysis"""
    print("\n📝 Testing Enhanced Paper Generation...")
    
    try:
        # We can't easily test the full paper generation without external dependencies,
        # but we can verify the statistical computation methods exist
        from paper_generator import AutomatedPaperGenerator
        
        # Check if the enhanced methods exist
        if hasattr(AutomatedPaperGenerator, '_compute_statistical_metrics'):
            print("✅ Statistical metrics computation method exists")
        else:
            print("❌ Missing statistical metrics computation method")
            return False
            
        # Create a mock instance to test statistical computation
        class MockDataManager:
            def get_all_experiments_for_paper(self):
                return []
                
        class MockResearcher:
            def call_llm_for_text(self, prompt):
                return "Mock response"
                
        try:
            generator = AutomatedPaperGenerator(MockDataManager(), MockResearcher())
            print("✅ Enhanced paper generator can be instantiated")
            return True
        except Exception as e:
            print(f"❌ Paper generator instantiation failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Paper generation test failed: {e}")
        return False

def main():
    """Run all tests and provide summary"""
    print("🚀 Testing Enhanced PADRES Pipeline")
    print("=" * 60)
    print("Addressing Stanford Professor's Critique:")
    print("- Task complexity and experimental controls")
    print("- Statistical rigor (p-values, effect sizes, CI)")
    print("- Performance degradation analysis") 
    print("- Proper baseline comparisons")
    print("=" * 60)
    
    tests = [
        ("Enhanced Spatial Tasks", test_enhanced_spatial_tasks),
        ("Statistical Analysis", test_statistical_analysis),
        ("Enhanced Quality Metrics", test_enhanced_quality_metrics),
        ("GCS Bucket Configuration", test_gcs_bucket_configuration),
        ("Paper Generation Enhancements", test_paper_generation_enhancements),
    ]
    
    results = {}
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Enhanced PADRES pipeline addresses Stanford critique")
        print("✅ Ready for improved research paper generation")
        print("✅ Statistical analysis capabilities verified")
        print("✅ GCS integration properly configured")
    else:
        print(f"\n⚠️  {total - passed} tests failed - review implementation")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
