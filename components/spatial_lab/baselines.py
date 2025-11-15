import abc
import random

class Baseline(abc.ABC):
    """Abstract base class for all baselines."""

    @abc.abstractmethod
    def run_experiment(self, env, task):
        """
        Run a single experiment.

        Args:
            env: The environment to run the experiment in.
            task: The task to run.

        Returns:
            A dictionary of results.
        """
        raise NotImplementedError

    def report_results(self, results):
        """
        Report the results of an experiment.

        Args:
            results: A dictionary of results from the experiment.
        """
        print("Baseline Results:")
        for key, value in results.items():
            print(f"  {key}: {value}")


class BaselineImporter:
    """Loads public, human-level performance data."""

    @staticmethod
    def get_public_benchmarks():
        """
        Returns a dictionary of well-known benchmark scores.
        """
        return {
            "CLEVR": 0.99,
            "RAVEN": 0.95,
            "CLOSURE": 0.92,
        }


class RandomBaseline(Baseline):
    """An agent that executes random, valid actions."""

    def run_experiment(self, env, task):
        """
        Run a single experiment with random actions.
        """
        obs, info = env.reset()
        done = False
        total_reward = 0
        steps = 0
        while not done:
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            total_reward += reward
            steps += 1
        
        results = {
            "total_reward": total_reward,
            "steps": steps,
            "success": info.get("success", False),
        }
        return results


class GreedyBaseline(Baseline):
    """An agent that implements a simple greedy strategy."""

    def run_experiment(self, env, task):
        """
        Run a single experiment with a greedy strategy.
        """
        obs, info = env.reset()
        done = False
        total_reward = 0
        steps = 0
        
        goal = task.get("goal_position")

        while not done:
            current_pos = obs["agent_position"]
            if goal:
                # Simple greedy action: move towards the goal
                action = 0  # Default action
                if goal[0] > current_pos[0]:
                    action = 3  # Move right
                elif goal[0] < current_pos[0]:
                    action = 2  # Move left
                elif goal[1] > current_pos[1]:
                    action = 1  # Move down
                elif goal[1] < current_pos[1]:
                    action = 0  # Move up
            else:
                action = env.action_space.sample()

            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            total_reward += reward
            steps += 1

        results = {
            "total_reward": total_reward,
            "steps": steps,
            "success": info.get("success", False),
        }
        return results