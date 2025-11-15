#!/usr/bin/env python3
"""
Analysis script for spatial shape vs metadata experiment results
"""

import json
import numpy as np
from typing import Dict, List, Any
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime


class SpatialExperimentAnalyzer:
    """Analyzer for spatial shape vs metadata experiment results"""
    
    def __init__(self, results_file: str):
        self.results_file = results_file
        self.data = None
        self.load_results()
    
    def load_results(self):
        """Load experiment results from JSON file"""
        with open(self.results_file, 'r') as f:
            self.data = json.load(f)
        
        print(f"Loaded results from: {self.results_file}")
        print(f"Total trials: {len(self.data['trials'])}")
    
    def calculate_statistics(self) -> Dict[str, Any]:
        """Calculate comprehensive statistics from the results"""
        
        trials = self.data['trials']
        
        # Separate trials by type
        shape_priority_trials = [t for t in trials if t['analysis']['task_type'] == 'shape_priority']
        metadata_priority_trials = [t for t in trials if t['analysis']['task_type'] == 'metadata_priority']
        
        # Calculate accuracy metrics
        shape_accuracy = sum(1 for t in shape_priority_trials if t['analysis']['correct_prioritization']) / len(shape_priority_trials) if shape_priority_trials else 0
        metadata_accuracy = sum(1 for t in metadata_priority_trials if t['analysis']['correct_prioritization']) / len(metadata_priority_trials) if metadata_priority_trials else 0
        
        # Calculate match counts
        shape_matches_shape_tasks = [t['analysis']['shape_matches'] for t in shape_priority_trials]
        metadata_matches_shape_tasks = [t['analysis']['metadata_matches'] for t in shape_priority_trials]
        
        shape_matches_metadata_tasks = [t['analysis']['shape_matches'] for t in metadata_priority_trials]
        metadata_matches_metadata_tasks = [t['analysis']['metadata_matches'] for t in metadata_priority_trials]
        
        # Statistical tests
        # Test if LLM prioritizes metadata over shape in shape priority tasks
        shape_priority_bias = np.mean([m - s for s, m in zip(shape_matches_shape_tasks, metadata_matches_shape_tasks)])
        
        # Test if LLM prioritizes metadata over shape in metadata priority tasks
        metadata_priority_bias = np.mean([m - s for s, m in zip(shape_matches_metadata_tasks, metadata_matches_metadata_tasks)])
        
        # Overall bias towards metadata
        overall_metadata_bias = np.mean([
            t['analysis']['metadata_matches'] - t['analysis']['shape_matches'] 
            for t in trials
        ])
        
        # Statistical significance tests
        # Paired t-test for shape vs metadata matches across all trials
        shape_matches_all = [t['analysis']['shape_matches'] for t in trials]
        metadata_matches_all = [t['analysis']['metadata_matches'] for t in trials]
        
        t_stat, p_value = stats.ttest_rel(metadata_matches_all, shape_matches_all)
        
        # Effect size (Cohen's d)
        pooled_std = np.sqrt((np.var(metadata_matches_all, ddof=1) + np.var(shape_matches_all, ddof=1)) / 2)
        cohens_d = (np.mean(metadata_matches_all) - np.mean(shape_matches_all)) / pooled_std if pooled_std > 0 else 0
        
        statistics = {
            'basic_stats': {
                'total_trials': len(trials),
                'shape_priority_trials': len(shape_priority_trials),
                'metadata_priority_trials': len(metadata_priority_trials),
                'shape_accuracy': shape_accuracy,
                'metadata_accuracy': metadata_accuracy,
                'overall_accuracy': self.data['statistics']['overall_accuracy']
            },
            'bias_analysis': {
                'shape_priority_bias': shape_priority_bias,
                'metadata_priority_bias': metadata_priority_bias,
                'overall_metadata_bias': overall_metadata_bias,
                'llm_prioritization': self.data['experiment_info']['llm_prioritization'],
                'prioritization_strength': self.data['experiment_info']['prioritization_strength']
            },
            'statistical_tests': {
                't_statistic': t_stat,
                'p_value': p_value,
                'cohens_d': cohens_d,
                'significant': p_value < 0.05,
                'effect_size_interpretation': self._interpret_effect_size(cohens_d)
            },
            'match_analysis': {
                'avg_shape_matches_shape_tasks': np.mean(shape_matches_shape_tasks) if shape_matches_shape_tasks else 0,
                'avg_metadata_matches_shape_tasks': np.mean(metadata_matches_shape_tasks) if metadata_matches_shape_tasks else 0,
                'avg_shape_matches_metadata_tasks': np.mean(shape_matches_metadata_tasks) if shape_matches_metadata_tasks else 0,
                'avg_metadata_matches_metadata_tasks': np.mean(metadata_matches_metadata_tasks) if metadata_matches_metadata_tasks else 0,
                'avg_shape_matches_overall': np.mean(shape_matches_all),
                'avg_metadata_matches_overall': np.mean(metadata_matches_all)
            }
        }
        
        return statistics
    
    def _interpret_effect_size(self, cohens_d: float) -> str:
        """Interpret Cohen's d effect size"""
        abs_d = abs(cohens_d)
        if abs_d < 0.2:
            return "negligible"
        elif abs_d < 0.5:
            return "small"
        elif abs_d < 0.8:
            return "medium"
        else:
            return "large"
    
    def generate_visualizations(self, output_dir: str = "analysis_output"):
        """Generate visualizations of the results"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        trials = self.data['trials']
        
        # Extract data for plotting
        shape_matches = [t['analysis']['shape_matches'] for t in trials]
        metadata_matches = [t['analysis']['metadata_matches'] for t in trials]
        task_types = [t['analysis']['task_type'] for t in trials]
        correct_prioritization = [t['analysis']['correct_prioritization'] for t in trials]
        
        # Set up the plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Spatial Shape vs Metadata Prioritization Analysis', fontsize=16, fontweight='bold')
        
        # Plot 1: Shape vs Metadata matches distribution
        axes[0, 0].scatter(shape_matches, metadata_matches, alpha=0.6, c=['red' if t == 'shape_priority' else 'blue' for t in task_types])
        axes[0, 0].plot([0, 3], [0, 3], 'k--', alpha=0.5, label='Equal preference line')
        axes[0, 0].set_xlabel('Shape Matches')
        axes[0, 0].set_ylabel('Metadata Matches')
        axes[0, 0].set_title('Shape vs Metadata Matches by Task Type')
        axes[0, 0].legend(['Equal preference', 'Shape priority tasks', 'Metadata priority tasks'])
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Accuracy by task type
        shape_trials = [t for t in trials if t['analysis']['task_type'] == 'shape_priority']
        metadata_trials = [t for t in trials if t['analysis']['task_type'] == 'metadata_priority']
        
        shape_acc = sum(1 for t in shape_trials if t['analysis']['correct_prioritization']) / len(shape_trials) if shape_trials else 0
        metadata_acc = sum(1 for t in metadata_trials if t['analysis']['correct_prioritization']) / len(metadata_trials) if metadata_trials else 0
        
        axes[0, 1].bar(['Shape Priority Tasks', 'Metadata Priority Tasks'], [shape_acc, metadata_acc], 
                      color=['red', 'blue'], alpha=0.7)
        axes[0, 1].set_ylabel('Accuracy')
        axes[0, 1].set_title('Accuracy by Task Type')
        axes[0, 1].set_ylim(0, 1)
        for i, v in enumerate([shape_acc, metadata_acc]):
            axes[0, 1].text(i, v + 0.02, f'{v:.1%}', ha='center', fontweight='bold')
        
        # Plot 3: Bias analysis
        bias_data = [t['analysis']['metadata_matches'] - t['analysis']['shape_matches'] for t in trials]
        axes[1, 0].hist(bias_data, bins=20, alpha=0.7, color='green', edgecolor='black')
        axes[1, 0].axvline(x=0, color='red', linestyle='--', label='No bias line')
        axes[1, 0].axvline(x=np.mean(bias_data), color='orange', linestyle='-', linewidth=2, label=f'Mean bias: {np.mean(bias_data):.2f}')
        axes[1, 0].set_xlabel('Metadata Matches - Shape Matches')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].set_title('Bias Distribution (Positive = Metadata Preference)')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Trial progression
        trial_numbers = list(range(1, len(trials) + 1))
        cumulative_shape = np.cumsum([t['analysis']['shape_matches'] for t in trials])
        cumulative_metadata = np.cumsum([t['analysis']['metadata_matches'] for t in trials])
        
        axes[1, 1].plot(trial_numbers, cumulative_shape, label='Cumulative Shape Matches', color='red', linewidth=2)
        axes[1, 1].plot(trial_numbers, cumulative_metadata, label='Cumulative Metadata Matches', color='blue', linewidth=2)
        axes[1, 1].set_xlabel('Trial Number')
        axes[1, 1].set_ylabel('Cumulative Matches')
        axes[1, 1].set_title('Cumulative Matches Over Trials')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/spatial_experiment_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Visualizations saved to: {output_dir}/spatial_experiment_analysis.png")
    
    def generate_report(self, statistics: Dict[str, Any], output_file: str = "spatial_experiment_analysis_report.md"):
        """Generate a comprehensive analysis report"""
        
        with open(output_file, 'w') as f:
            f.write("# Spatial Shape vs Metadata Prioritization Experiment Analysis\n\n")
            f.write(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Results File:** {self.results_file}\n\n")
            
            # Executive Summary
            f.write("## Executive Summary\n\n")
            f.write(f"The experiment tested whether LLMs prioritize shape recognition or metadata when making spatial reasoning decisions. ")
            f.write(f"Results from {statistics['basic_stats']['total_trials']} trials show that the LLM demonstrates a **{statistics['bias_analysis']['llm_prioritization']}** prioritization bias ")
            f.write(f"with a strength of {statistics['bias_analysis']['prioritization_strength']:.2f}.\n\n")
            
            # Key Findings
            f.write("## Key Findings\n\n")
            f.write(f"- **Overall Accuracy:** {statistics['basic_stats']['overall_accuracy']:.1%}\n")
            f.write(f"- **Shape Priority Task Accuracy:** {statistics['basic_stats']['shape_accuracy']:.1%}\n")
            f.write(f"- **Metadata Priority Task Accuracy:** {statistics['basic_stats']['metadata_accuracy']:.1%}\n")
            f.write(f"- **Statistical Significance:** {'Yes' if statistics['statistical_tests']['significant'] else 'No'} (p = {statistics['statistical_tests']['p_value']:.4f})\n")
            f.write(f"- **Effect Size:** {statistics['statistical_tests']['effect_size_interpretation']} (Cohen's d = {statistics['statistical_tests']['cohens_d']:.3f})\n\n")
            
            # Detailed Analysis
            f.write("## Detailed Analysis\n\n")
            f.write("### Bias Analysis\n\n")
            f.write(f"The LLM shows a consistent bias towards **{statistics['bias_analysis']['llm_prioritization']}** prioritization:\n\n")
            f.write(f"- **Overall Metadata Bias:** {statistics['bias_analysis']['overall_metadata_bias']:.2f} (positive values indicate metadata preference)\n")
            f.write(f"- **Shape Priority Task Bias:** {statistics['bias_analysis']['shape_priority_bias']:.2f}\n")
            f.write(f"- **Metadata Priority Task Bias:** {statistics['bias_analysis']['metadata_priority_bias']:.2f}\n\n")
            
            f.write("### Match Analysis\n\n")
            f.write("Average matches across different task types:\n\n")
            f.write(f"- **Shape Priority Tasks:**\n")
            f.write(f"  - Average shape matches: {statistics['match_analysis']['avg_shape_matches_shape_tasks']:.2f}\n")
            f.write(f"  - Average metadata matches: {statistics['match_analysis']['avg_metadata_matches_shape_tasks']:.2f}\n\n")
            f.write(f"- **Metadata Priority Tasks:**\n")
            f.write(f"  - Average shape matches: {statistics['match_analysis']['avg_shape_matches_metadata_tasks']:.2f}\n")
            f.write(f"  - Average metadata matches: {statistics['match_analysis']['avg_metadata_matches_metadata_tasks']:.2f}\n\n")
            
            f.write(f"- **Overall Averages:**\n")
            f.write(f"  - Average shape matches: {statistics['match_analysis']['avg_shape_matches_overall']:.2f}\n")
            f.write(f"  - Average metadata matches: {statistics['match_analysis']['avg_metadata_matches_overall']:.2f}\n\n")
            
            # Statistical Tests
            f.write("### Statistical Tests\n\n")
            f.write("A paired t-test comparing metadata matches vs shape matches across all trials:\n\n")
            f.write(f"- **t-statistic:** {statistics['statistical_tests']['t_statistic']:.4f}\n")
            f.write(f"- **p-value:** {statistics['statistical_tests']['p_value']:.4f}\n")
            f.write(f"- **Cohen's d:** {statistics['statistical_tests']['cohens_d']:.4f}\n")
            f.write(f"- **Interpretation:** {statistics['statistical_tests']['effect_size_interpretation']} effect size\n\n")
            
            # Conclusions
            f.write("## Conclusions\n\n")
            if statistics['bias_analysis']['llm_prioritization'] == 'metadata':
                f.write("The LLM demonstrates a **statistical preference for metadata over shape recognition** in spatial reasoning tasks. ")
            else:
                f.write("The LLM demonstrates a **statistical preference for shape recognition over metadata** in spatial reasoning tasks. ")
            
            if statistics['statistical_tests']['significant']:
                f.write("This preference is **statistically significant** (p < 0.05), indicating a reliable bias in the LLM's decision-making process. ")
            else:
                f.write("However, this preference is **not statistically significant** (p ≥ 0.05), suggesting the bias may not be reliable. ")
            
            f.write(f"The effect size is {statistics['statistical_tests']['effect_size_interpretation']}, ")
            if statistics['statistical_tests']['effect_size_interpretation'] in ['medium', 'large']:
                f.write("indicating a practically meaningful difference in prioritization behavior.\n\n")
            else:
                f.write("indicating a small difference in prioritization behavior.\n\n")
            
            # Implications
            f.write("## Implications\n\n")
            f.write("### For Spatial AI Systems:\n")
            f.write("- LLM-based spatial reasoning systems should account for this prioritization bias\n")
            f.write("- Training data should be balanced to avoid reinforcing metadata bias\n")
            f.write("- Explicit instructions may be needed to override natural prioritization tendencies\n\n")
            
            f.write("### For Future Research:\n")
            f.write("- Investigate whether this bias is consistent across different LLM architectures\n")
            f.write("- Test whether fine-tuning can reduce or eliminate the bias\n")
            f.write("- Explore the relationship between bias strength and task complexity\n\n")
            
            # Limitations
            f.write("## Limitations\n\n")
            f.write("- Results are based on simulated LLM responses rather than actual LLM API calls\n")
            f.write("- Limited to warehouse coordination scenarios\n")
            f.write("- Sample size of 100 trials may not capture all behavioral patterns\n")
            f.write("- Task complexity was standardized and may not reflect real-world variability\n\n")
        
        print(f"Analysis report saved to: {output_file}")


def main():
    """Main analysis function"""
    
    # Find the most recent results file
    import glob
    result_files = glob.glob("spatial_shape_metadata_experiment_*.json")
    if not result_files:
        print("No experiment results files found!")
        return
    
    latest_file = max(result_files)
    print(f"Analyzing results from: {latest_file}")
    
    # Initialize analyzer
    analyzer = SpatialExperimentAnalyzer(latest_file)
    
    # Calculate statistics
    print("Calculating statistics...")
    statistics = analyzer.calculate_statistics()
    
    # Generate visualizations
    print("Generating visualizations...")
    analyzer.generate_visualizations()
    
    # Generate report
    print("Generating analysis report...")
    analyzer.generate_report(statistics)
    
    # Print summary
    print("\n" + "="*60)
    print("SPATIAL EXPERIMENT ANALYSIS SUMMARY")
    print("="*60)
    print(f"Total trials: {statistics['basic_stats']['total_trials']}")
    print(f"LLM prioritizes: {statistics['bias_analysis']['llm_prioritization']}")
    print(f"Prioritization strength: {statistics['bias_analysis']['prioritization_strength']:.2f}")
    print(f"Overall accuracy: {statistics['basic_stats']['overall_accuracy']:.1%}")
    print(f"Statistical significance: {'Yes' if statistics['statistical_tests']['significant'] else 'No'}")
    print(f"Effect size: {statistics['statistical_tests']['effect_size_interpretation']}")
    print("="*60)


if __name__ == "__main__":
    main()





