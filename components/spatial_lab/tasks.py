import numpy as np
import random
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type

class SpatialTask(ABC):
    """Abstract base class for a spatial reasoning task."""

    @abstractmethod
    def get_description(self) -> str:
        """Returns a description of the task."""
        pass

    @abstractmethod
    def get_reward(self, state: Any) -> float:
        """Calculates the reward for the given state."""
        pass

    @abstractmethod
    def is_goal_state(self, state: Any) -> bool:
        """Determines if the given state is a goal state."""
        pass

    @abstractmethod
    def get_goal_position(self) -> np.ndarray:
        """Returns the ground-truth goal position for the task."""
        pass

class TaskRegistry:
    """A registry for discovering and managing spatial tasks."""

    def __init__(self):
        self._tasks: Dict[str, Type[SpatialTask]] = {}

    def register(self, task_class: Type[SpatialTask]):
        """Registers a task class."""
        self._tasks[task_class.__name__] = task_class

    def get_task(self, name: str) -> Type[SpatialTask]:
        """Returns a task class by name."""
        return self._tasks[name]

    def list_tasks(self) -> List[str]:
        """Returns a list of all registered task names."""
        return list(self._tasks.keys())

    def get_random_task(self) -> Type[SpatialTask]:
        """Returns a random task class."""
        return random.choice(list(self._tasks.values()))

# Create a global registry
task_registry = TaskRegistry()

def register_task(task_class: Type[SpatialTask]) -> Type[SpatialTask]:
    """A decorator for registering a task class."""
    task_registry.register(task_class)
    return task_class
@register_task
class ObjectStackingTask(SpatialTask):
    """A task that requires placing one object on top of another."""

    def get_description(self) -> str:
        return "Place the red object on top of the blue object."

    def get_reward(self, state: Any) -> float:
        # This is a simplified reward function. A more complex function could
        # consider the distance between the objects, their alignment, and stability.
        red_object_pos = state.get("red_object_pos")
        blue_object_pos = state.get("blue_object_pos")
        distance = np.linalg.norm(red_object_pos - blue_object_pos)
        return -distance

    def is_goal_state(self, state: Any) -> bool:
        red_object_pos = state.get("red_object_pos")
        blue_object_pos = state.get("blue_object_pos")
        return np.allclose(red_object_pos, blue_object_pos + np.array([0, 0, 1]), atol=0.1)

    def get_goal_position(self) -> np.ndarray:
        # For this task, the goal is relative to the blue object.
        # This is a simplification; a real implementation might need state.
        return np.array([0, 0, 1.5])  # Example: Assumes blue object is at [0, 0, 0.5]

@register_task
class ObstacleNavigationTask(SpatialTask):
    """A task that requires moving an object around an obstacle."""

    def get_description(self) -> str:
        return "Move the green object to the goal position while avoiding the obstacle."

    def get_reward(self, state: Any) -> float:
        green_object_pos = state.get("green_object_pos")
        goal_pos = state.get("goal_pos")
        obstacle_pos = state.get("obstacle_pos")

        dist_to_goal = np.linalg.norm(green_object_pos - goal_pos)
        dist_to_obstacle = np.linalg.norm(green_object_pos - obstacle_pos)

        # Penalize proximity to the obstacle
        obstacle_penalty = 0
        if dist_to_obstacle < 0.2:
            obstacle_penalty = -1.0

        return -dist_to_goal + obstacle_penalty

    def is_goal_state(self, state: Any) -> bool:
        green_object_pos = state.get("green_object_pos")
        goal_pos = state.get("goal_pos")
        return np.allclose(green_object_pos, goal_pos, atol=0.1)

    def get_goal_position(self) -> np.ndarray:
        return np.array([2, 0, 0.5])

@register_task
class ColorMatchingTask(SpatialTask):
    """A task that requires moving an object to another object of the same color."""

    def get_description(self) -> str:
        return "Move the yellow object to the other yellow object."

    def get_reward(self, state: Any) -> float:
        yellow_object_1_pos = state.get("yellow_object_1_pos")
        yellow_object_2_pos = state.get("yellow_object_2_pos")
        distance = np.linalg.norm(yellow_object_1_pos - yellow_object_2_pos)
        return -distance

    def is_goal_state(self, state: Any) -> bool:
        yellow_object_1_pos = state.get("yellow_object_1_pos")
        yellow_object_2_pos = state.get("yellow_object_2_pos")
        return np.allclose(yellow_object_1_pos, yellow_object_2_pos, atol=0.1)

    def get_goal_position(self) -> np.ndarray:
        return np.array([1, 1, 0.5])