import argparse
import json
from collections import Counter
import numpy as np
from stats import Statistics
from components.spatial_lab.failure_analysis import FailureClassifier

def analyze_trajectories(file_path):
    """
    Analyzes trajectories from a .jsonl file to extract scores, perplexities, and classify failures.

    Args:
        file_path (str): The path to the trajectories.jsonl file.

    Returns:
        tuple: A tuple containing lists of scores, spatial perplexities, and failure categories.
    """
    scores = []
    perplexities = []
    failures = []
    with open(file_path, 'r') as f:
        for line in f:
            data = json.loads(line)
            scores.append(data.get('score', 0.0)) # Use .get for safety
            
            # Extract spatial perplexity, defaulting to a high value (or None) if not present
            perplexity = data.get("metadata", {}).get("spatial_perplexity")
            if perplexity is not None and perplexity != float('inf'):
                perplexities.append(perplexity)

            if data.get('score', 0.0) < 1.0:
                # Assuming FailureClassifier might need the 'score' key, not 'normalized_score'
                # If it needs the original structure, this might need adjustment
                failure_classifier_data = data.copy()
                failure_classifier_data['normalized_score'] = data.get('score', 0.0)
                classifier = FailureClassifier(failure_classifier_data)
                failure_category = classifier.classify_failure()
                failures.append(failure_category)
    return scores, perplexities, failures

def main():
    """
    Main function to run the statistical analysis and failure classification.
    """
    parser = argparse.ArgumentParser(description="Perform statistical analysis and failure classification on trajectory files.")
    parser.add_argument("model_file", help="Path to the model's trajectories.jsonl file.")
    parser.add_argument("baseline_file", help="Path to the baseline's trajectories.jsonl file.")
    args = parser.parse_args()

    model_scores, model_perplexities, model_failures = analyze_trajectories(args.model_file)
    baseline_scores, _, _ = analyze_trajectories(args.baseline_file) # Baseline doesn't have perplexity

    stats = Statistics(model_scores, baseline_scores)

    t_statistic, p_value = stats.paired_ttest()
    cohen_d = stats.cohens_d()
    ci_lower, ci_upper = stats.confidence_interval()

    print("Statistical Analysis Report")
    print("===========================")
    print(f"Paired t-test: t-statistic={t_statistic:.4f}, p-value={p_value:.4f}")
    print(f"Cohen's d: {cohen_d:.4f}")
    print(f"95% Confidence Interval for the Mean Difference: [{ci_lower:.4f}, {ci_upper:.4f}]")
    
    if model_perplexities:
        avg_perplexity = np.mean(model_perplexities)
        print(f"Average Spatial Perplexity: {avg_perplexity:.4f}")

    print("\n")

    if model_failures:
        failure_counts = Counter(model_failures)
        total_failures = len(model_failures)
        
        print("Failure Report")
        print("==============")
        print(f"Total failed trials: {total_failures}")
        for category, count in failure_counts.items():
            percentage = (count / total_failures) * 100
            print(f"- {category}: {count} ({percentage:.2f}%)")

if __name__ == "__main__":
    main()