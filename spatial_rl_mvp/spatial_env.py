import argparse
import asyncio
import json
import logging
import math
import os
import random
import sys
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pybullet as p
import pybullet_data
import websockets

import wandb

# LLM Service Import
from .llm_services import get_anthropic_completion
from components.spatial_lab.metrics import SpatialPerplexity
from components.spatial_lab.tasks import task_registry, SpatialTask
from components.spatial_lab.baselines import (
    Baseline,
    RandomBaseline,
    GreedyBaseline,
    BaselineImporter,
)


@dataclass
class ObjectState:
    id: str
    type: str  # 'cube', 'sphere'
    position: List[float]
    orientation_quaternion: List[float] = field(
        default_factory=lambda: [0.0, 0.0, 0.0, 1.0]
    )
    scale: List[float] = field(default_factory=lambda: [1.0, 1.0, 1.0])
    color_rgba: List[float] = field(default_factory=lambda: [0.5, 0.5, 0.5, 1.0])


class SimulationContext:
    """A context manager for a PyBullet simulation."""

    def __init__(self):
        self.client_id = -1

    def __enter__(self):
        """Initializes a new PyBullet simulation and returns the client ID."""
        self.client_id = p.connect(p.DIRECT)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.8, physicsClientId=self.client_id)
        p.loadURDF("plane.urdf", physicsClientId=self.client_id)
        print(f"New simulation context created (Client ID: {self.client_id}).")
        return self.client_id

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Disconnects from the PyBullet simulation."""
        if self.client_id != -1:
            p.disconnect(physicsClientId=self.client_id)
            print(f"Simulation context cleaned up (Client ID: {self.client_id}).")
            self.client_id = -1


class MVPPhysicsSimulator:
    def __init__(self, client_id: int):
        self.client_id = client_id
        self.objects_pb_ids: Dict[str, int] = {}
        self.object_configs: Dict[str, ObjectState] = {}

    def initialize(self, objects: List[ObjectState]):
        # Connection is now managed externally by the context manager.
        self.objects_pb_ids = {}
        self.object_configs = {}
        for obj_state in objects:
            self._add_object(obj_state)
        print(f"Physics initialized with {len(self.objects_pb_ids)} objects.")

    def _add_object(self, obj_state: ObjectState):
        half_extents = [s / 2.0 for s in obj_state.scale]
        shape_id = -1
        if obj_state.type == "cube":
            shape_id = p.createCollisionShape(
                p.GEOM_BOX, halfExtents=half_extents, physicsClientId=self.client_id
            )
        elif obj_state.type == "sphere":
            shape_id = p.createCollisionShape(
                p.GEOM_SPHERE, radius=half_extents[0], physicsClientId=self.client_id
            )
        else:
            print(
                f"Warning: Unsupported object type '{obj_state.type}' for object ID '{obj_state.id}'"
            )
            return

        if obj_state.type == "cube":
            visual_shape_id = p.createVisualShape(
                shapeType=p.GEOM_BOX,
                halfExtents=half_extents,
                rgbaColor=obj_state.color_rgba,
                physicsClientId=self.client_id,
            )
        elif obj_state.type == "sphere":
            visual_shape_id = p.createVisualShape(
                shapeType=p.GEOM_SPHERE,
                radius=half_extents[0],
                rgbaColor=obj_state.color_rgba,
                physicsClientId=self.client_id,
            )
        else:
            print(
                f"Warning: Unsupported object type '{obj_state.type}' for object ID '{obj_state.id}'"
            )
            return

        body_id = p.createMultiBody(
            baseMass=1,
            baseCollisionShapeIndex=shape_id,
            baseVisualShapeIndex=visual_shape_id,
            basePosition=obj_state.position,
            baseOrientation=obj_state.orientation_quaternion,
            physicsClientId=self.client_id,
        )
        self.objects_pb_ids[obj_state.id] = body_id
        self.object_configs[obj_state.id] = obj_state

    def move_object(
        self,
        object_id: str,
        target_position: List[float],
        target_orientation_quaternion: Optional[List[float]] = None,
    ):
        if object_id in self.objects_pb_ids:
            body_id = self.objects_pb_ids[object_id]
            if target_orientation_quaternion is None:
                _, current_orientation = p.getBasePositionAndOrientation(
                    body_id, physicsClientId=self.client_id
                )
                target_orientation_quaternion = list(current_orientation)
            p.resetBasePositionAndOrientation(
                body_id,
                target_position,
                target_orientation_quaternion,
                physicsClientId=self.client_id,
            )
        else:
            print(f"Warning: Attempted to move unknown object ID '{object_id}'")

    def simulate_steps(self, steps: int = 10):
        for _ in range(steps):
            p.stepSimulation(physicsClientId=self.client_id)

    def get_current_state_for_visualization(self) -> List[Dict[str, Any]]:
        viz_state = []
        for obj_id, body_id in self.objects_pb_ids.items():
            pos, orn_quat = p.getBasePositionAndOrientation(
                body_id, physicsClientId=self.client_id
            )
            original_config = self.object_configs.get(obj_id)
            if original_config:
                viz_state.append(
                    {
                        "id": obj_id,
                        "type": original_config.type,
                        "position": list(pos),
                        "orientation_quaternion": list(orn_quat),
                        "scale": original_config.scale,
                        "color_rgba": original_config.color_rgba,
                    }
                )
        return viz_state

    def calculate_distance(self, obj1_id: str, obj2_id: str) -> float:
        pos1, pos2 = None, None
        current_state = self.get_current_state_for_visualization()
        for obj_data in current_state:
            if obj_data["id"] == obj1_id:
                pos1 = obj_data["position"]
            if obj_data["id"] == obj2_id:
                pos2 = obj_data["position"]

        if pos1 and pos2:
            return math.sqrt(sum((a - b) ** 2 for a, b in zip(pos1, pos2)))
        return float("inf")

    def cleanup(self):
        # This method is now redundant as the context manager handles disconnection.
        # The containing loop should use a `with SimulationContext():` block.
        pass


connected_visualization_clients = set()
# Global instances removed to ensure trial isolation.
# Each trial will create its own simulator and demo runner instance.


async def notify_visualization_clients(scene_state: List[Dict[str, Any]]):
    if connected_visualization_clients:
        message = json.dumps({"type": "scene_update", "payload": scene_state})
        await asyncio.gather(
            *[client.send(message) for client in connected_visualization_clients]
        )


class InteractiveServerManager:
    """Manages state for the interactive server mode, ensuring isolation."""

    def __init__(self):
        self.lock = asyncio.Lock()

    async def handle_turn(self, use_real_llm: bool = True):
        """Handles a single, isolated experimental turn."""
        async with self.lock:  # Ensure only one turn runs at a time
            with SimulationContext() as client_id:
                demo_runner = MVPDemoRunner(client_id=client_id)
                await demo_runner.run_single_turn_demo(use_real_llm=use_real_llm)

    async def websocket_handler(self, websocket):
        """Handles websocket connections for visualization."""
        connected_visualization_clients.add(websocket)
        print(
            f"Visualization client connected: {websocket.remote_address} (Total: {len(connected_visualization_clients)})"
        )
        try:
            # No initial state to send; each turn is self-contained.
            # Send a ready message to the client.
            await websocket.send(json.dumps({"type": "server_ready"}))

            async for message_str in websocket:
                print(f"Message from viz client: {message_str}")
                try:
                    data = json.loads(message_str)
                    if data.get("command") == "next_llm_task":
                        print("Received 'next_llm_task' command from client.")
                        # Schedule a new, isolated turn to run.
                        asyncio.create_task(self.handle_turn(use_real_llm=True))
                    else:
                        print(f"Unknown command received: {data.get('command')}")
                except json.JSONDecodeError:
                    print(f"Invalid JSON from client: {message_str}")
                except Exception as e:
                    print(f"Error processing client command: {e}")
        except websockets.exceptions.ConnectionClosed:
            print(
                f"Visualization client disconnected. (Total: {len(connected_visualization_clients) - 1})"
            )
        except Exception as e:
            print(f"Error in websocket_handler: {e}")
        finally:
            connected_visualization_clients.remove(websocket)


class SpatialEnvironmentMVP:
    def __init__(self, client_id: int):
        self.simulator = MVPPhysicsSimulator(client_id)
        self.current_task: Optional[SpatialTask] = None
        self.task_id_counter = 0

    async def initialize_task(self, task: SpatialTask):
        """
        Initializes the environment with a specific task definition.
        This method is intended for use by an external service (like an API).
        """
        if not isinstance(task, SpatialTask):
            raise ValueError("Invalid task object provided to initialize_task.")

        self.current_task = task
        print(
            f"SpatialEnvironmentMVP: Initializing for task_id: {task.task_id}, Description: {task.description[:50]}..."
        )
        self.simulator.initialize(task.initial_objects)
        self.grid_size = 10  # Define a 10x10 grid for spatial reasoning
        self.grid_bounds = ((-5, 5), (-5, 5))  # X and Y bounds of the grid

        # Notify visualization clients about the new initial scene
        # This assumes notify_visualization_clients can be called from a potentially new event loop
        # or that this method is always called from within an existing one.
        # If the API service for Padres runs in a separate process, this notification
        # might need to go through a different channel or be initiated by the API service itself.
        await notify_visualization_clients(
            self.simulator.get_current_state_for_visualization()
        )
        print(
            f"SpatialEnvironmentMVP: Task '{task.task_id}' initialized and simulator ready."
        )

    async def apply_action_and_get_outcome(
        self, parsed_action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Applies a parsed action to the environment and returns the outcome (new state, reward, done, etc.).
        This method does NOT call any LLM; it assumes the action is already decided.
        """
        if not self.current_task:
            return {
                "error": "No current task set. Call initialize_task first.",
                "status": "failure",
                "reward": 0.0,
                "done": True,
            }

        print(
            f"SpatialEnvironmentMVP (Task: {self.current_task.task_id}): Applying action: {parsed_action}"
        )

        action_executed_successfully = False
        if parsed_action and parsed_action.get("action_type") == "move_object":
            object_id_to_move = parsed_action.get(
                "object_id", self.current_task.target_object_id
            )
            target_position = parsed_action.get("target_position")
            target_orientation = parsed_action.get(
                "target_orientation_quaternion"
            )  # Optional

            if object_id_to_move and target_position:
                self.simulator.move_object(
                    object_id_to_move, target_position, target_orientation
                )
                action_executed_successfully = True
                print(f"  Moved '{object_id_to_move}' to {target_position}.")
            else:
                print(
                    "  Warning: move_object action lacked object_id or target_position."
                )
        else:
            action_type = parsed_action.get("action_type", "unknown")
            print(
                f"  Warning: Received unhandled or malformed action_type: '{action_type}'. No simulation change."
            )

        # Simulate physics steps after action (or no-action)
        self.simulator.simulate_steps(20 if action_executed_successfully else 5)

        # Get new visual state for clients and for reward calculation
        new_state_viz = self.simulator.get_current_state_for_visualization()
        await notify_visualization_clients(new_state_viz)  # Update viz clients

        # Scoring logic (adapted from collect_trajectories)
        distance = self.simulator.calculate_distance(
            self.current_task.target_object_id, self.current_task.reference_object_id
        )

        initial_ref_pos = None
        for obj_state in self.current_task.initial_objects:
            if obj_state.id == self.current_task.reference_object_id:
                initial_ref_pos = obj_state.position
                break
        initial_ref_pos = initial_ref_pos or [0, 0, 0]  # Fallback

        final_target_pos = None
        for obj_data in new_state_viz:
            if obj_data["id"] == self.current_task.target_object_id:
                final_target_pos = obj_data["position"]
                break
        final_target_pos = final_target_pos or initial_ref_pos  # Fallback

        side_condition_met = False
        if (
            initial_ref_pos[0] != 0
        ):  # Avoid division by zero or ambiguous sign if ref_obj at x=0
            side_condition_met = math.copysign(
                1.0, final_target_pos[0]
            ) == math.copysign(1.0, initial_ref_pos[0])
        else:  # if ref object is at x=0, target should also be very close to x=0 for side condition
            side_condition_met = abs(final_target_pos[0]) < 0.5

        score = 0.0
        if distance <= self.current_task.target_distance:
            score = 0.8
        elif distance <= self.current_task.target_distance * 1.25:
            score = 0.6
        elif distance <= self.current_task.target_distance * 1.75:
            score = 0.4
        elif distance <= self.current_task.target_distance * 2.5:
            score = 0.2
        if side_condition_met:
            score += 0.2
        score = round(min(score, 1.0), 2)

        # Determine if task is done. For now, assume one action completes the task in this service context.
        # More complex tasks might have different done conditions (e.g., max_turns, specific goal state reached).
        is_done = True
        action_type_str = parsed_action.get("action_type", "unknown")
        observation_message = f"Action '{action_type_str}' applied. Distance to ref: {distance:.2f}. Score: {score}. Side condition met: {side_condition_met}."

        return {
            "new_state_viz": new_state_viz,
            "reward": score,
            "done": is_done,
            "observation": observation_message,
            "message": "Action applied and outcome calculated.",
            # "raw_action_applied": parsed_action # Could be useful for logging
        }

    async def get_next_item(self) -> Dict[str, Any]:
        self.task_id_counter += 1
        task_id = f"task_{self.task_id_counter}_{uuid.uuid4().hex[:4]}"

        # Dynamically select a task from the registry
        task_class = task_registry.get_random_task()
        self.current_task = task_class()

        # For now, we'll use a placeholder to generate objects.
        # A more robust solution would have tasks define their object requirements.
        initial_objects = self._generate_objects_for_task(task_class.__name__)

        # Initialize the environment with the new task and objects
        self.simulator.initialize(initial_objects)
        await notify_visualization_clients(
            self.simulator.get_current_state_for_visualization()
        )

        return {
            "task_id": task_id,
            "llm_prompt": self._create_llm_prompt(self.current_task, initial_objects),
        }

    def _generate_objects_for_task(self, task_name: str) -> List[ObjectState]:
        """Generates a list of ObjectState objects for a given task."""
        if task_name == "ObjectStackingTask":
            return [
                ObjectState(id="red_object", type="cube", position=[0, 0, 0.5], color_rgba=[1, 0, 0, 1]),
                ObjectState(id="blue_object", type="cube", position=[0, 0, 1.5], color_rgba=[0, 0, 1, 1]),
            ]
        elif task_name == "ObstacleNavigationTask":
            return [
                ObjectState(id="green_object", type="sphere", position=[-2, 0, 0.5], color_rgba=[0, 1, 0, 1]),
                ObjectState(id="goal_position", type="sphere", position=[2, 0, 0.5], color_rgba=[0, 1, 0, 0.5]),
                ObjectState(id="obstacle", type="cube", position=[0, 0, 0.5], scale=[1, 1, 2], color_rgba=[0.5, 0.5, 0.5, 1]),
            ]
        elif task_name == "ColorMatchingTask":
            return [
                ObjectState(id="yellow_object_1", type="cube", position=[-1, -1, 0.5], color_rgba=[1, 1, 0, 1]),
                ObjectState(id="yellow_object_2", type="sphere", position=[1, 1, 0.5], color_rgba=[1, 1, 0, 1]),
            ]
        return []

    def _create_llm_prompt(
        self, task: SpatialTask, initial_objects_state: List[ObjectState]
    ) -> str:
        objects_desc_parts = []
        for obj_state in initial_objects_state:
            objects_desc_parts.append(
                f"- ID: {obj_state.id}, Type: {obj_state.type}, Current Position: [{obj_state.position[0]:.2f}, {obj_state.position[1]:.2f}, {obj_state.position[2]:.2f}]"
            )
        objects_desc = "\n".join(objects_desc_parts)
        ref_obj_pos_str = "N/A"
        for obj_state in initial_objects_state:
            if obj_state.id == task.reference_object_id:
                ref_obj_pos_str = f"[{obj_state.position[0]:.2f}, {obj_state.position[1]:.2f}, {obj_state.position[2]:.2f}]"
                break
        hint = (
            f"Hint: The blue_sphere (reference object) is currently at {ref_obj_pos_str}. "
            "To keep the red_cube on the opposite side of the YZ plane, its x-coordinate should generally have the opposite sign "
            "to the blue_sphere's x-coordinate. Adjust its position to be about {task.target_distance:.1f} unit away from the blue_sphere."
        )
        return f"""Task: {task.description}
Goal: {task.goal_description}

Available Objects (initial state):
{objects_desc}

{hint}

You control: '{task.target_object_id}'.
The environment is a 10x10 grid from x:(-5, 5) and y:(-5, 5).
Your action MUST be a JSON object. You must provide both a specific target position and a probability distribution over the grid.
{{
    "action_type": "move_object",
    "object_id": "{task.target_object_id}",
    "target_position": [x_float, y_float, z_float],
    "probability_grid": [p_0_0, p_0_1, ..., p_9_9]
}}
The "probability_grid" must be a flattened 100-element array where each element is the probability for a cell in the 10x10 grid. The sum of this array must be 1.0.
Only provide the JSON for the action. Do not add any other text or explanations.
Your JSON action:"""

    async def collect_trajectories(
        self,
        item_from_get_next: Dict[str, Any],
        llm_completion_raw: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Orchestrates a single turn: gets LLM action (if not provided), applies it, scores.
        If llm_completion_raw is provided, it's used directly. Otherwise, LLM is called.
        """
        if not self.current_task:
            # This could happen if get_next_item or initialize_task wasn't called successfully prior.
            # Try to initialize a default task as a fallback if a prompt is part of item_from_get_next.
            if (
                item_from_get_next
                and item_from_get_next.get("llm_prompt")
                and item_from_get_next.get("task_id")
            ):
                print(
                    "Warning: collect_trajectories called with no current_task, attempting to use item_from_get_next to reconstruct."
                )
                # This is a limited reconstruction, initial_objects might be missing for full scoring context.
                # This path is less ideal. Ensure initialize_task or get_next_item is called first.
                mock_initial_objects = [
                    ObjectState(id="dummy", type="cube", position=[0, 0, 0])
                ]  # Minimal for _create_llm_prompt
                self.current_task = SpatialTask(
                    task_id=item_from_get_next["task_id"],
                    description="Reconstructed task from prompt",
                    initial_objects=mock_initial_objects,  # This is insufficient for accurate scoring logic
                    goal_description="Reconstructed goal",
                    target_object_id="unknown_target",  # Placeholder
                    reference_object_id="unknown_reference",  # Placeholder
                )
                # Cannot reliably initialize simulator here without full object state.
                print(
                    f"  Reconstructed task: {self.current_task.task_id}. Scoring might be inaccurate."
                )
            else:
                return {
                    "error": "No current task set. Call get_next_item or initialize_task first.",
                    "score": 0.0,
                }

        llm_prompt_for_api = item_from_get_next.get(
            "llm_prompt",
            self._create_llm_prompt(
                self.current_task, self.current_task.initial_objects
            ),
        )

        parsed_action = None
        actual_llm_response_for_log = (
            llm_completion_raw  # Store the originally passed one for logging
        )

        if llm_completion_raw is None:
            print(
                "DEBUG SPATIAL_ENV: llm_completion_raw not provided, calling get_anthropic_completion with prompt... Timeout in 30s"
            )
            try:
                llm_response_from_service = await asyncio.wait_for(
                    get_anthropic_completion(llm_prompt_for_api), timeout=30.0
                )
                actual_llm_response_for_log = (
                    llm_response_from_service  # Update for logging
                )
            except asyncio.TimeoutError:
                print(
                    "DEBUG SPATIAL_ENV: LLM call timed out after 30s. Using fallback internal mock action."
                )
                actual_llm_response_for_log = '{"error": "LLM Timeout"}'  # Log timeout
            except Exception as e:
                print(
                    f"DEBUG SPATIAL_ENV: Error during get_anthropic_completion: {e}. Using fallback internal mock action."
                )
                actual_llm_response_for_log = (
                    f'{{"error": "LLM Exception: {e}"}}'  # Log exception
                )

        # Parse the action (either provided or from LLM call)
        if actual_llm_response_for_log and isinstance(actual_llm_response_for_log, str):
            try:
                json_str = actual_llm_response_for_log.strip()
                if json_str.startswith("```json"):
                    json_str = json_str[7:]
                if json_str.startswith("```"):
                    json_str = json_str[3:]
                if json_str.endswith("```"):
                    json_str = json_str[:-3]
                json_str = json_str.strip()
                action_data = json.loads(json_str)
                if (
                    action_data.get("action_type") == "move_object"
                    and action_data.get("object_id")
                    == self.current_task.target_object_id
                    and isinstance(action_data.get("target_position"), list)
                    and len(action_data.get("target_position")) == 3
                    and isinstance(action_data.get("probability_grid"), list)
                    and len(action_data.get("probability_grid")) == self.grid_size**2
                ):
                    parsed_action = action_data
                else:
                    print(
                        f"Warning: LLM action malformed or targets wrong object: {action_data}"
                    )
            except json.JSONDecodeError as e:
                print(
                    f"Warning: LLM response not valid JSON: {actual_llm_response_for_log}. Error: {e}"
                )
            except Exception as e:
                print(
                    f"Warning: Unexpected error parsing LLM response: {e}. Response: {actual_llm_response_for_log}"
                )

        if (
            not parsed_action
        ):  # If LLM call failed, timed out, or parsing failed, use a default mock action
            print(
                f"DEBUG SPATIAL_ENV: Using internal mock action as LLM response was problematic ('{str(actual_llm_response_for_log)[:100]}...')."
            )
            parsed_action = {
                "action_type": "move_object",
                "object_id": self.current_task.target_object_id,
                "target_position": [1.0, 0.5, 0.5],
            }  # Example mock
            actual_llm_response_for_log += " (FALLBACK TO MOCK ACTION USED)"

        # Apply action and get outcome
        outcome = await self.apply_action_and_get_outcome(parsed_action)

        # Calculate Spatial Perplexity
        spatial_perplexity = float("inf")
        if parsed_action and "probability_grid" in parsed_action:
            try:
                prob_dist = np.array(parsed_action["probability_grid"]).reshape(
                    (self.grid_size, self.grid_size)
                )
                # Normalize to ensure it sums to 1, handling potential LLM output errors
                if np.sum(prob_dist) > 0:
                    prob_dist /= np.sum(prob_dist)

                # Get ground truth location in continuous space
                true_target_pos = self.current_task.get_goal_position()

                # Discretize the ground truth location
                x_range = self.grid_bounds[0]
                y_range = self.grid_bounds[1]
                col = int(
                    (true_target_pos[0] - x_range[0])
                    / (x_range[1] - x_range[0])
                    * self.grid_size
                )
                row = int(
                    (true_target_pos[1] - y_range[0])
                    / (y_range[1] - y_range[0])
                    * self.grid_size
                )
                ground_truth_location = (
                    np.clip(row, 0, self.grid_size - 1),
                    np.clip(col, 0, self.grid_size - 1),
                )

                perplexity_calculator = SpatialPerplexity()
                spatial_perplexity = perplexity_calculator.calculate(
                    prob_dist, ground_truth_location
                )
                print(f"  Calculated Spatial Perplexity: {spatial_perplexity:.2f}")

            except Exception as e:
                print(f"Warning: Could not calculate Spatial Perplexity. Error: {e}")

        return {
            "request_id": self.current_task.task_id,
            "prompt_used": llm_prompt_for_api,
            "llm_completion_raw": actual_llm_response_for_log,
            "parsed_action": parsed_action,
            "score": outcome.get("reward"),  # Use reward from outcome
            "metadata": {
                "task_description": self.current_task.description,
                "final_distance": self.simulator.calculate_distance(
                    self.current_task.target_object_id,
                    self.current_task.reference_object_id,
                ),  # Recalculate for log, or get from outcome
                "target_distance": self.current_task.target_distance,
                "spatial_perplexity": spatial_perplexity,
                "side_condition_met": "N/A in this refactor yet",  # This was part of scoring logic
                "final_sim_state_viz": outcome.get("new_state_viz"),
                "observation_from_action": outcome.get("observation"),
                "action_done_status": outcome.get("done"),
            },
        }


class MVPDemoRunner:
    def __init__(self, client_id: int, baseline: Optional[str] = None):
        self.env = SpatialEnvironmentMVP(client_id)
        self.baseline_agent: Optional[Baseline] = None
        if baseline:
            if baseline == "random":
                self.baseline_agent = RandomBaseline()
            elif baseline == "greedy":
                self.baseline_agent = GreedyBaseline()
            else:
                raise ValueError(f"Unknown baseline: {baseline}")

    async def run_single_turn_demo(self, use_real_llm: bool = True):
        print("\n--- Running MVP Demo Turn ---")
        next_item_data = (
            await self.env.get_next_item()
        )  # This now calls initialize_task with a default task
        task_id = next_item_data["task_id"]
        print(f"Task ID: {task_id}")

        if self.baseline_agent:
            print(f"Running baseline: {self.baseline_agent.__class__.__name__}")
            # The environment is not fully compatible with gym, so we pass it directly
            # We also need to pass the task for context
            baseline_results = self.baseline_agent.run_experiment(self.env.simulator, self.env.current_task)
            
            # Format results to match LLM structure
            result = {
                "request_id": task_id,
                "prompt_used": "N/A (Baseline)",
                "llm_completion_raw": "N/A (Baseline)",
                "parsed_action": "N/A (Baseline)",
                "score": baseline_results.get("total_reward", 0.0),
                "metadata": {
                    "task_description": self.env.current_task.description,
                    "final_distance": self.env.simulator.calculate_distance(
                        self.env.current_task.target_object_id,
                        self.env.current_task.reference_object_id,
                    ),
                    "target_distance": self.env.current_task.target_distance,
                    "side_condition_met": "N/A (Baseline)",
                    "final_sim_state_viz": self.env.simulator.get_current_state_for_visualization(),
                    "observation_from_action": f"Baseline run completed in {baseline_results.get('steps', 0)} steps.",
                    "action_done_status": True,
                    "success": baseline_results.get("success", False),
                },
            }
        else:
            # collect_trajectories will call the LLM if llm_completion_raw is None (default behavior)
            result = await self.env.collect_trajectories(
                next_item_data, llm_completion_raw=None
            )

        print(f"\n--- Result for Task {task_id} ---")
        print(f"Final Score: {result['score']:.2f}")
        print(
            f"Achieved Distance: {result['metadata']['final_distance']:.2f} (Target: {result['metadata']['target_distance']:.2f})"
        )
        return result


async def process_mode(args):
    print(
        f"Running in 'process' mode: generating {args.num_turns} trajectories to {args.output_file}"
    )

    run_name = f"padres_process_{args.num_turns}turns_{uuid.uuid4().hex[:4]}"
    wandb_is_initialized = False
    try:
        wandb.init(
            project="nous_hackathon_padres",
            name=run_name,
            config=vars(args),
        )
        print(f"W&B Run initialized: {run_name}. View at: {wandb.run.get_url()}")
        wandb_is_initialized = True
    except Exception as e:
        print(f"W&B initialization failed: {e}. Proceeding without W&B logging.")

    results_to_write = []

    try:
        for i in range(args.num_turns):
            turn_num = i + 1
            print(f"\n--- Generating Trajectory Turn {turn_num}/{args.num_turns} ---")

            # Use the context manager to ensure a clean, isolated simulation for each turn.
            with SimulationContext() as client_id:
                demo_runner = MVPDemoRunner(client_id, baseline=args.baseline)
                turn_result = await demo_runner.run_single_turn_demo()
                results_to_write.append(turn_result)

                if wandb_is_initialized and wandb.run:
                    wandb_log_data = {
                        "turn": turn_num,
                        "task_id": turn_result.get("request_id", "N/A"),
                        "score": turn_result.get("score", 0.0),
                        "final_distance": turn_result.get("metadata", {}).get(
                            "final_distance", float("inf")
                        ),
                        "target_distance": turn_result.get("metadata", {}).get(
                            "target_distance", 0.0
                        ),
                        "spatial_perplexity": turn_result.get("metadata", {}).get(
                            "spatial_perplexity", float("inf")
                        ),
                        "side_condition_met": int(
                            turn_result.get("metadata", {}).get("side_condition_met", False)
                        ),
                    }
                    if turn_result.get("parsed_action"):
                        parsed_action = turn_result["parsed_action"]
                        wandb_log_data["action_object_id"] = parsed_action.get("object_id")
                        target_pos = parsed_action.get("target_position", [None, None, None])
                        wandb_log_data["action_target_x"] = target_pos[0] if target_pos and len(target_pos) > 0 else None
                        wandb_log_data["action_target_y"] = target_pos[1] if target_pos and len(target_pos) > 1 else None
                        wandb_log_data["action_target_z"] = target_pos[2] if target_pos and len(target_pos) > 2 else None

                    wandb.log(wandb_log_data)
                    print(f"Logged to W&B: Turn {turn_num}, Score: {turn_result.get('score')}")

            await asyncio.sleep(0.1)

        with open(args.output_file, "w") as f:
            for result_item in results_to_write:
                f.write(json.dumps(result_item) + "\n")
        print(f"\nSuccessfully wrote {len(results_to_write)} trajectories to {args.output_file}")

    finally:
        # Cleanup is now handled by the SimulationContext's __exit__ method.
        if wandb_is_initialized and wandb.run:
            wandb.finish()
            print("Processing complete. W&B run finished.")
        else:
            print("Processing complete. (W&B was not initialized or did not start a run)")


async def server_mode():
    manager = InteractiveServerManager()

    websocket_server = await websockets.serve(
        manager.websocket_handler, "localhost", 8765
    )
    print("Visualization WebSocket Server started on ws://localhost:8765")
    print("Open visualization/index.html in your browser.")
    print("You can run multiple demo turns. Press Ctrl+C to stop everything.")

    try:
        # Run initial automatic turns, each in its own isolated environment.
        for i in range(5):
            print(f"\n--- Auto Demo Turn {i+1} ---")
            await manager.handle_turn(use_real_llm=True)
            await asyncio.sleep(2)

        print(
            "\nAutomatic demo turns complete. Server is still running for manual interaction."
        )
        await websocket_server.wait_closed()
    except KeyboardInterrupt:
        print("\nShutting down servers...")
    finally:
        websocket_server.close()
        await websocket_server.wait_closed()
        # Cleanup is handled by the context manager within each turn.
        print("Server stopped.")


async def main():
    parser = argparse.ArgumentParser(description="Spatial RL Environment MVP")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    process_parser = subparsers.add_parser("process", help="Generate trajectory data")
    process_parser.add_argument(
        "--num_turns",
        type=int,
        default=5,
        help="Number of trajectory turns to generate",
    )
    process_parser.add_argument(
        "--output_file",
        type=str,
        default="trajectories.jsonl",
        help="File to save trajectory data",
    )
    process_parser.add_argument(
        "--baseline",
        type=str,
        default=None,
        choices=["random", "greedy"],
        help="Run a baseline agent instead of the LLM.",
    )

    args, unknown = parser.parse_known_args()

    if args.command == "process":
        await process_mode(args)
    elif args.command is None and not unknown:
        print("No command specified, running in default server mode.")
        await server_mode()
    elif unknown:
        print(f"Unknown arguments or command: {unknown}")
        parser.print_help()
        sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
