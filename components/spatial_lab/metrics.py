import numpy as np
from typing import Tuple

class SpatialPerplexity:
    """
    Calculates Spatial Perplexity, a measure of a model's uncertainty about
    the correct spatial configuration.

    This metric is based on the concept of perplexity in language models, but
    adapted for a spatial domain. It evaluates how "surprised" the model is by the
    ground-truth action, given its own predicted probability distribution over
    a discretized space.

    A lower perplexity score indicates that the model assigned a higher
    probability to the correct location, signifying greater confidence and
    accuracy in its spatial reasoning.
    """

    def calculate(
        self,
        probability_distribution: np.ndarray,
        ground_truth_location: Tuple[int, int],
    ) -> float:
        """
        Calculates the perplexity score from a probability distribution.

        Args:
            probability_distribution: A 2D numpy array representing the model's
                                      output probability distribution over a grid.
                                      The values in this grid should sum to 1.
            ground_truth_location: A tuple (row, col) representing the true
                                   goal location on the grid.

        Returns:
            The calculated perplexity score. Returns float('inf') if the
            probability of the ground truth location is zero.
        """
        prob_ground_truth = probability_distribution[
            ground_truth_location[0], ground_truth_location[1]
        ]

        if prob_ground_truth == 0:
            return float("inf")

        # The cross-entropy for a single ground-truth sample is -log2(p_correct).
        cross_entropy = -np.log2(prob_ground_truth)

        # Perplexity is defined as 2 raised to the power of the cross-entropy.
        perplexity = np.power(2.0, cross_entropy)

        return perplexity