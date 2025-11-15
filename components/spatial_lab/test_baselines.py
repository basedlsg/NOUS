import unittest
import asyncio
from unittest.mock import MagicMock, patch

from components.spatial_lab.baselines import RandomBaseline, GreedyBaseline
from spatial_rl_mvp.spatial_env import SpatialEnvironmentMVP, ObjectState, SpatialTask


class TestBaselines(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.env = SpatialEnvironmentMVP()

        # Mock the task
        self.task = SpatialTask(
            task_id="test_task",
            description="Test task",
            goal_description="Reach the goal",
            initial_objects=[
                ObjectState(
                    id="agent",
                    type="sphere",
                    position=[0, 0, 0.5],
                    color_rgba=[0, 1, 0, 1],
                ),
                ObjectState(
                    id="goal",
                    type="sphere",
                    position=[5, 5, 0.5],
                    color_rgba=[1, 0, 0, 1],
                ),
            ],
            target_object_id="agent",
            reference_object_id="goal",
            target_distance=1.0,
        )

    def tearDown(self):
        self.loop.close()

    def test_random_baseline(self):
        async def run_test():
            # Initialize the environment with the task
            await self.env.initialize_task(self.task)

            # Run the baseline
            baseline = RandomBaseline()
            results = baseline.run_experiment(self.env.simulator, self.task)

            # Check results
            self.assertIn("total_reward", results)
            self.assertIn("steps", results)
            self.assertIn("success", results)
            self.assertGreaterEqual(results["steps"], 1)

        self.loop.run_until_complete(run_test())

    def test_greedy_baseline(self):
        async def run_test():
            # Initialize the environment with the task
            await self.env.initialize_task(self.task)

            # Run the baseline
            baseline = GreedyBaseline()
            results = baseline.run_experiment(self.env.simulator, self.task)

            # Check results
            self.assertIn("total_reward", results)
            self.assertIn("steps", results)
            self.assertIn("success", results)
            self.assertGreaterEqual(results["steps"], 1)

        self.loop.run_until_complete(run_test())


if __name__ == "__main__":
    unittest.main()