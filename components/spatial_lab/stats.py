import numpy as np
from scipy import stats

class Statistics:
    """
    A class to perform statistical analysis on two sets of scores.
    """
    def __init__(self, scores1, scores2):
        """
        Initializes the Statistics class with two sets of scores.

        Args:
            scores1 (list or np.ndarray): The first set of scores.
            scores2 (list or np.ndarray): The second set of scores.
        """
        self.scores1 = np.array(scores1)
        self.scores2 = np.array(scores2)

    def paired_ttest(self):
        """
        Calculates the paired t-test for the two sets of scores.

        Returns:
            tuple: A tuple containing the t-statistic and the p-value.
        """
        t_statistic, p_value = stats.ttest_rel(self.scores1, self.scores2)
        return t_statistic, p_value

    def cohens_d(self):
        """
        Calculates Cohen's d for the two sets of scores.

        Returns:
            float: The value of Cohen's d.
        """
        diff = self.scores1 - self.scores2
        return np.mean(diff) / np.std(diff, ddof=1)

    def confidence_interval(self, confidence_level=0.95):
        """
        Calculates the confidence interval for the mean difference between the scores.

        Args:
            confidence_level (float, optional): The desired confidence level. Defaults to 0.95.

        Returns:
            tuple: A tuple containing the lower and upper bounds of the confidence interval.
        """
        diff = self.scores1 - self.scores2
        n = len(diff)
        mean_diff = np.mean(diff)
        std_err = stats.sem(diff)
        
        t_critical = stats.t.ppf((1 + confidence_level) / 2, df=n-1)
        margin_of_error = t_critical * std_err
        
        return mean_diff - margin_of_error, mean_diff + margin_of_error