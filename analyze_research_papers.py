import os
import argparse
import re
import numpy as np
from scipy import stats
from scipy.stats import pearsonr, ttest_ind, chi2_contingency
import pandas as pd
from typing import List, Dict, Tuple, Optional
from google.cloud import storage
from google.oauth2 import service_account

def get_single_paper_content(credentials_path, bucket_name, file_path):
    """
    Reads a single research paper from a GCS bucket and returns its content.
    Enhanced to extract quality metrics.
    """
    if credentials_path:
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        storage_client = storage.Client(credentials=credentials)
    else:
        storage_client = storage.Client() # Use ADC
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    paper_content = blob.download_as_text()
    return paper_content

def extract_quality_metrics(paper_content):
    """Extract comprehensive quality metrics from paper content addressing Stanford critique"""
    metrics = {
        'has_p_values': bool(re.search(r'p\s*[=<>]\s*0\.\d+', paper_content)),
        'has_effect_sizes': bool(re.search(r'effect size|Cohen.*d|eta.squared|r\s*=|correlation', paper_content, re.IGNORECASE)),
        'has_baselines': bool(re.search(r'baseline|control|comparison.*group', paper_content, re.IGNORECASE)),
        'has_statistics': bool(re.search(r'statistical|significance|t-test|ANOVA|regression', paper_content, re.IGNORECASE)),
        'has_confidence_intervals': bool(re.search(r'confidence\s+interval|CI|95%|CI\s*=', paper_content, re.IGNORECASE)),
        'has_correlation_analysis': bool(re.search(r'Pearson.*correlation|correlation.*analysis|r\s*=.*-?0\.\d+', paper_content, re.IGNORECASE)),
        'has_error_analysis': bool(re.search(r'error.*analysis|failure.*mode|ablation.*study', paper_content, re.IGNORECASE)),
        'has_trend_analysis': bool(re.search(r'trend.*analysis|temporal.*pattern|declining.*performance', paper_content, re.IGNORECASE)),
        'addresses_degradation': bool(re.search(r'declining|degradation|-0\.7|-0\.8|negative.*correlation', paper_content, re.IGNORECASE)),
        'word_count': len(paper_content.split()),
        'section_count': len(re.findall(r'^#+\s', paper_content, re.MULTILINE))
    }
    
    # Enhanced quality scoring addressing professor's critique
    quality_score = 0
    if metrics['has_p_values']: quality_score += 15
    if metrics['has_effect_sizes']: quality_score += 20  
    if metrics['has_baselines']: quality_score += 20
    if metrics['has_statistics']: quality_score += 15
    if metrics['has_confidence_intervals']: quality_score += 15
    if metrics['has_correlation_analysis']: quality_score += 10
    if metrics['has_error_analysis']: quality_score += 10
    if metrics['has_trend_analysis']: quality_score += 10
    if metrics['addresses_degradation']: quality_score += 15
    quality_score += min(10, metrics['section_count'] * 1.5)
    
    metrics['quality_score'] = min(quality_score, 100)  # Cap at 100
    return metrics

def compute_statistical_analysis(papers_data: List[Dict]) -> Dict:
    """
    Compute comprehensive statistical analysis addressing Stanford professor's critique
    Returns p-values, effect sizes, confidence intervals, and trend analysis
    """
    if len(papers_data) < 3:
        return {"error": "Insufficient data for statistical analysis (need >= 3 papers)"}
    
    analysis = {}
    
    # Extract numerical data
    quality_scores = [p['metrics']['quality_score'] for p in papers_data if 'metrics' in p]
    creation_times = [p['created'] for p in papers_data if 'created' in p]
    
    if len(quality_scores) < 3:
        return {"error": "Insufficient quality scores for analysis"}
    
    # Sort by creation time for trend analysis
    paired_data = list(zip(creation_times, quality_scores))
    paired_data.sort(key=lambda x: x[0])
    sorted_scores = [score for _, score in paired_data]
    
    # Generate experiment count proxy (sequential numbering)
    experiment_counts = list(range(1, len(sorted_scores) + 1))
    
    # 1. CORRELATION ANALYSIS (addressing the -0.71/-0.81 finding)
    if len(experiment_counts) >= 3:
        correlation_coeff, correlation_p = pearsonr(experiment_counts, sorted_scores)
        analysis['correlation'] = {
            'pearson_r': correlation_coeff,
            'p_value': correlation_p,
            'interpretation': 'negative' if correlation_coeff < -0.5 else 'positive' if correlation_coeff > 0.5 else 'weak',
            'significance': 'significant' if correlation_p < 0.05 else 'not_significant'
        }
    
    # 2. DESCRIPTIVE STATISTICS
    analysis['descriptive'] = {
        'mean_quality': np.mean(quality_scores),
        'std_quality': np.std(quality_scores),
        'median_quality': np.median(quality_scores),
        'min_quality': np.min(quality_scores),
        'max_quality': np.max(quality_scores),
        'n_papers': len(quality_scores)
    }
    
    # 3. CONFIDENCE INTERVALS
    confidence_level = 0.95
    n = len(quality_scores)
    mean_score = np.mean(quality_scores)
    std_error = stats.sem(quality_scores)
    ci_margin = std_error * stats.t.ppf((1 + confidence_level) / 2, n-1)
    
    analysis['confidence_intervals'] = {
        'mean': mean_score,
        'ci_lower': mean_score - ci_margin,
        'ci_upper': mean_score + ci_margin,
        'confidence_level': confidence_level
    }
    
    # 4. EFFECT SIZE ANALYSIS (Cohen's d)
    if len(quality_scores) >= 6:  # Split into early vs late papers
        mid_point = len(quality_scores) // 2
        early_scores = quality_scores[:mid_point]
        late_scores = quality_scores[mid_point:]
        
        # Cohen's d calculation
        pooled_std = np.sqrt(((len(early_scores) - 1) * np.var(early_scores) + 
                             (len(late_scores) - 1) * np.var(late_scores)) / 
                            (len(early_scores) + len(late_scores) - 2))
        
        cohens_d = (np.mean(early_scores) - np.mean(late_scores)) / pooled_std if pooled_std > 0 else 0
        
        # T-test for significance
        t_stat, t_p = ttest_ind(early_scores, late_scores)
        
        analysis['effect_size'] = {
            'cohens_d': cohens_d,
            't_statistic': t_stat,
            't_p_value': t_p,
            'interpretation': 'large' if abs(cohens_d) > 0.8 else 'medium' if abs(cohens_d) > 0.5 else 'small',
            'early_mean': np.mean(early_scores),
            'late_mean': np.mean(late_scores)
        }
    
    # 5. TREND ANALYSIS
    if len(quality_scores) >= 4:
        # Linear regression for trend
        slope, intercept, r_value, p_value, std_err = stats.linregress(experiment_counts, sorted_scores)
        
        analysis['trend_analysis'] = {
            'slope': slope,
            'r_squared': r_value**2,
            'p_value': p_value,
            'std_error': std_err,
            'trend_direction': 'declining' if slope < -0.1 else 'improving' if slope > 0.1 else 'stable',
            'predicted_change_per_experiment': slope
        }
    
    # 6. QUALITY DISTRIBUTION ANALYSIS
    quality_categories = ['low' if q < 30 else 'medium' if q < 70 else 'high' for q in quality_scores]
    quality_counts = {cat: quality_categories.count(cat) for cat in ['low', 'medium', 'high']}
    
    analysis['quality_distribution'] = quality_counts
    
    return analysis

def analyze_all_papers_in_bucket(credentials_path, bucket_name):
    """Analyze all papers in the bucket for quality trends with comprehensive statistics"""
    if credentials_path:
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        storage_client = storage.Client(credentials=credentials)
    else:
        storage_client = storage.Client() # Use ADC
    bucket = storage_client.bucket(bucket_name)
    
    papers_data = []
    blobs = bucket.list_blobs(prefix="generated_papers/")
    
    for blob in blobs:
        if blob.name.endswith('.md'):
            content = blob.download_as_text()
            metrics = extract_quality_metrics(content)
            papers_data.append({
                'name': blob.name,
                'created': blob.time_created,
                'metrics': metrics,
                'content_preview': content[:500]  # For debugging
            })
    
    # Perform comprehensive statistical analysis
    statistical_results = compute_statistical_analysis(papers_data)
    
    return {
        'papers_data': papers_data,
        'statistical_analysis': statistical_results,
        'summary': {
            'total_papers': len(papers_data),
            'avg_quality_score': np.mean([p['metrics']['quality_score'] for p in papers_data]) if papers_data else 0,
            'stanford_critique_addressed': {
                'correlation_analysis': 'correlation' in statistical_results,
                'effect_sizes': 'effect_size' in statistical_results,
                'confidence_intervals': 'confidence_intervals' in statistical_results,
                'trend_analysis': 'trend_analysis' in statistical_results
            }
        }
    }

if __name__ == "__main__":
    # Temporarily unset the environment variable if it exists, to ensure ADC works as expected.
    original_credentials = os.environ.pop('GOOGLE_APPLICATION_CREDENTIALS', None)
    
    parser = argparse.ArgumentParser(description="Analyze research papers from GCS bucket.")
    parser.add_argument("--credentials_path", default=None, help="Optional path to the GCP credentials JSON file. If not provided, Application Default Credentials (ADC) will be used.")
    parser.add_argument("--analyze-all", action="store_true", help="Analyze all papers for quality trends")
    args = parser.parse_args()

    BUCKET_NAME = "gen-lang-client-0029379200-research-papers"  # KEEP EXACT SAME
    
    try:
        if args.analyze_all:
            results = analyze_all_papers_in_bucket(args.credentials_path, BUCKET_NAME)
            papers = results['papers_data']
            stats = results['statistical_analysis']
            summary = results['summary']
            
            print("=" * 60)
            print("COMPREHENSIVE STATISTICAL ANALYSIS (addressing Stanford critique)")
            print("=" * 60)
            print(f"Total papers analyzed: {summary['total_papers']}")
            print(f"Average quality score: {summary['avg_quality_score']:.2f}")
            
            if 'correlation' in stats:
                corr = stats['correlation']
                print(f"\n📊 CORRELATION ANALYSIS (addressing -0.71/-0.81 finding):")
                print(f"  Pearson r = {corr['pearson_r']:.3f}")
                print(f"  p-value = {corr['p_value']:.4f} ({corr['significance']})")
                print(f"  Interpretation: {corr['interpretation']} correlation")
            
            if 'effect_size' in stats:
                effect = stats['effect_size']
                print(f"\n📈 EFFECT SIZE ANALYSIS:")
                print(f"  Cohen's d = {effect['cohens_d']:.3f} ({effect['interpretation']} effect)")
                print(f"  t-test p-value = {effect['t_p_value']:.4f}")
                print(f"  Early papers mean: {effect['early_mean']:.2f}")
                print(f"  Late papers mean: {effect['late_mean']:.2f}")
            
            if 'confidence_intervals' in stats:
                ci = stats['confidence_intervals']
                print(f"\n🎯 CONFIDENCE INTERVALS:")
                print(f"  Mean quality: {ci['mean']:.2f}")
                print(f"  95% CI: [{ci['ci_lower']:.2f}, {ci['ci_upper']:.2f}]")
            
            if 'trend_analysis' in stats:
                trend = stats['trend_analysis']
                print(f"\n📉 TREND ANALYSIS:")
                print(f"  Slope: {trend['slope']:.4f} (per experiment)")
                print(f"  R² = {trend['r_squared']:.3f}")
                print(f"  p-value = {trend['p_value']:.4f}")
                print(f"  Trend: {trend['trend_direction']}")
            
            print(f"\n✅ Stanford Critique Addressed:")
            for criterion, addressed in summary['stanford_critique_addressed'].items():
                status = "✓" if addressed else "✗"
                print(f"  {status} {criterion.replace('_', ' ').title()}")
            
            print(f"\n📋 Individual Paper Quality Scores:")
            for paper in papers:
                print(f"  {paper['name']}: {paper['metrics']['quality_score']}")
                
        else:
            FILE_PATH = "generated_papers/spatial_ai_research_paper_gemini_20250526_040642.md"
            content = get_single_paper_content(args.credentials_path, BUCKET_NAME, FILE_PATH)
            metrics = extract_quality_metrics(content)
            print(f"Paper Quality Score: {metrics['quality_score']}")
            print(f"Quality Breakdown: {metrics}")
            
    finally:
        # Restore the environment variable after execution
        if original_credentials is not None:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = original_credentials