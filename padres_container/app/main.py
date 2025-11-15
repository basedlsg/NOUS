print("--- PING: app/main.py top level ---")
import os

# Path handling for importing from spatial_rl_mvp
import sys
import uuid
import random
from typing import Any, Dict, Optional, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from schelling_model import SchellingModel

class SchellingExperimentParams(BaseModel):
    grid_size: int = Field(50, gt=0, description="Size of the square grid.")
    agent_groups: List[int] = Field([1, 2], description="List of agent group identifiers.")
    satisfaction_threshold: float = Field(0.3, ge=0, le=1, description="Satisfaction threshold for agents.")
    empty_ratio: float = Field(0.1, ge=0, le=1, description="Ratio of empty cells in the grid.")
    max_steps: int = Field(100, gt=0, description="Maximum number of simulation steps.")

# Assuming /padres_app is the WORKDIR and spatial_rl_mvp is at /padres_app/spatial_rl_mvp
# and this file is /padres_app/app/main.py
# Adding /padres_app to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spatial_rl_mvp.spatial_env import ObjectState, SpatialEnvironmentMVP, SpatialTask

app = FastAPI(title="Padres Simulation Service API (Live V2)")

spatial_env_instance: Optional[SpatialEnvironmentMVP] = None

# --- Helper: Neutralize websocket calls for now ---
# This is a bit of a hack. A cleaner way would be to pass a flag to SpatialEnvironmentMVP
# or modify its methods to optionally skip notifications.
original_notify_visualization_clients = None


async def dummy_notify_visualization_clients_func(scene_state: Any):
    # print("DEBUG: notify_visualization_clients (dummy) called, doing nothing.")
    pass


# We'll apply monkeypatch after ensuring module is loaded, e.g. in startup.
# This is because the module might not be loaded at the exact moment of this script parsing.


@app.on_event("startup")
async def startup_event():
    global spatial_env_instance
    global original_notify_visualization_clients

    # Attempt to monkeypatch after imports are surely done and module loaded by SpatialEnvironmentMVP
    if "spatial_rl_mvp.spatial_env" in sys.modules:
        if hasattr(
            sys.modules["spatial_rl_mvp.spatial_env"], "notify_visualization_clients"
        ):
            original_notify_visualization_clients = sys.modules[
                "spatial_rl_mvp.spatial_env"
            ].notify_visualization_clients
            sys.modules["spatial_rl_mvp.spatial_env"].notify_visualization_clients = (
                dummy_notify_visualization_clients_func
            )
            print(
                "INFO: spatial_rl_mvp.spatial_env.notify_visualization_clients has been temporarily neutralized during startup."
            )
        else:
            print(
                "WARN (startup): spatial_rl_mvp.spatial_env.notify_visualization_clients not found for neutralization."
            )
    else:
        print(
            "WARN (startup): spatial_rl_mvp.spatial_env module not found in sys.modules for websocket neutralization."
        )

    try:
        spatial_env_instance = SpatialEnvironmentMVP()
        print("INFO: SpatialEnvironmentMVP instance created on FastAPI startup.")
    except Exception as e:
        print(f"FATAL: Failed to create SpatialEnvironmentMVP instance on startup: {e}")
        import traceback

        traceback.print_exc()
        spatial_env_instance = None


@app.on_event("shutdown")
async def shutdown_event():
    if (
        spatial_env_instance
        and hasattr(spatial_env_instance, "simulator")
        and spatial_env_instance.simulator
    ):
        spatial_env_instance.simulator.cleanup()
        print("INFO: PyBullet simulation cleaned up on FastAPI shutdown.")

    # Restore original if it was patched
    if (
        original_notify_visualization_clients
        and "spatial_rl_mvp.spatial_env" in sys.modules
    ):
        if hasattr(
            sys.modules["spatial_rl_mvp.spatial_env"], "notify_visualization_clients"
        ):
            sys.modules["spatial_rl_mvp.spatial_env"].notify_visualization_clients = (
                original_notify_visualization_clients
            )
            print("INFO: Restored original notify_visualization_clients on shutdown.")


@app.get("/")
async def root():
    return {"message": "Padres API is alive!"}


@app.get("/status")
async def get_status_endpoint():  # Renamed from get_status to avoid conflict if imported elsewhere
    global spatial_env_instance
    env_status = "Not initialized or instance creation failed"
    task_id = "N/A"
    pybullet_client_id = "N/A"

    if spatial_env_instance:
        env_status = "Instance created"
        if (
            hasattr(spatial_env_instance, "simulator")
            and spatial_env_instance.simulator
        ):
            pybullet_client_id = str(spatial_env_instance.simulator.client_id)
            if spatial_env_instance.simulator.client_id != -1:
                env_status += ", PyBullet Client Connected"
            else:
                env_status += ", PyBullet Client NOT Connected"
        else:
            env_status += ", Simulator object not found"

        if (
            hasattr(spatial_env_instance, "current_task")
            and spatial_env_instance.current_task
        ):
            task_id = spatial_env_instance.current_task.task_id
            env_status += f", Task '{task_id}' loaded"
        else:
            env_status += ", No task loaded"

    return {
        "api_status": "OPERATIONAL",
        "simulation_status_summary": env_status,
        "pybullet_direct_client_id": pybullet_client_id,
        "current_task_id": task_id,
        "notes": "This is the LIVE API wrapping spatial_rl_mvp (V2 structure).",
    }


# Enhanced Spatial Tasks with Complexity Gradients and Statistical Controls
# Addresses Stanford professor's critique about task complexity and experimental rigor

def generate_complexity_variants(base_task, complexity_level):
    """Generate tasks with varying complexity levels for statistical analysis"""
    variants = []
    for i in range(3):  # Generate 3 variants per complexity level
        task_id = f"{base_task.task_id}_complexity_{complexity_level}_variant_{i}"
        # Add randomization and complexity scaling
        modified_objects = []
        for obj in base_task.initial_objects:
            # Add position noise based on complexity level
            noise_factor = complexity_level * 0.1
            new_position = [
                obj.position[0] + random.uniform(-noise_factor, noise_factor),
                obj.position[1] + random.uniform(-noise_factor, noise_factor),
                obj.position[2]
            ]
            modified_objects.append(ObjectState(
                id=f"{obj.id}_v{i}",
                type=obj.type,
                position=new_position,
                scale=obj.scale,
                color_rgba=obj.color_rgba
            ))
        
        variants.append(SpatialTask(
            task_id=task_id,
            description=f"{base_task.description} (Complexity: {complexity_level}, Variant: {i})",
            initial_objects=modified_objects,
            goal_description=base_task.goal_description,
            target_object_id=f"{base_task.target_object_id}_v{i}",
            reference_object_id=f"{base_task.reference_object_id}_v{i}",
            target_distance=base_task.target_distance * (1 + complexity_level * 0.1)
        ))
    return variants

# Base tasks for experimental design
BASE_TASKS = {
    "multi_step_tower_build": SpatialTask(
        task_id="multi_step_tower_build",
        description="Build a stable tower by stacking cubes in the correct order, requiring multi-step spatial reasoning.",
        initial_objects=[
            ObjectState(id="foundation_cube", type="cube", position=[0, 0, 0.1], scale=[0.3, 0.3, 0.1], color_rgba=[0.5,0.5,0.5,1]),
            ObjectState(id="base_cube", type="cube", position=[-0.8, 0, 0.1], scale=[0.25, 0.25, 0.2], color_rgba=[1,0,0,1]),
            ObjectState(id="mid_cube", type="cube", position=[0.8, 0, 0.1], scale=[0.2, 0.2, 0.15], color_rgba=[0,1,0,1]),
            ObjectState(id="top_cube", type="cube", position=[0, 0.8, 0.1], scale=[0.15, 0.15, 0.1], color_rgba=[0,0,1,1]),
            ObjectState(id="distractor_cube", type="cube", position=[0, -0.8, 0.1], scale=[0.1, 0.1, 0.05], color_rgba=[1,1,0,1]),
        ],
        goal_description="Stack cubes on foundation in descending size order: base, mid, top (distractors must be ignored).",
        target_object_id="base_cube",
        reference_object_id="foundation_cube",
        target_distance=0.05,
    ),
    
    "complex_maze_navigation": SpatialTask(
        task_id="complex_maze_navigation",
        description="Navigate through a complex maze with multiple paths, dead ends, and optimal route planning.",
        initial_objects=[
            ObjectState(id="agent", type="sphere", position=[-2.5, -2.5, 0.1], scale=[0.1, 0.1, 0.1], color_rgba=[1,1,0,1]),
            ObjectState(id="goal", type="sphere", position=[2.5, 2.5, 0.1], scale=[0.1, 0.1, 0.1], color_rgba=[0,1,1,1]),
            # Complex maze walls creating multiple paths
            ObjectState(id="wall_1", type="cube", position=[-1, -2, 0.5], scale=[0.1, 1, 1], color_rgba=[0.5,0.5,0.5,1]),
            ObjectState(id="wall_2", type="cube", position=[1, -2, 0.5], scale=[0.1, 1, 1], color_rgba=[0.5,0.5,0.5,1]),
            ObjectState(id="wall_3", type="cube", position=[-2, 0, 0.5], scale=[1, 0.1, 1], color_rgba=[0.5,0.5,0.5,1]),
            ObjectState(id="wall_4", type="cube", position=[2, 0, 0.5], scale=[1, 0.1, 1], color_rgba=[0.5,0.5,0.5,1]),
            ObjectState(id="wall_5", type="cube", position=[0, 1, 0.5], scale=[2, 0.1, 1], color_rgba=[0.5,0.5,0.5,1]),
            ObjectState(id="trap_wall", type="cube", position=[0, -1, 0.5], scale=[1.5, 0.1, 1], color_rgba=[0.7,0.3,0.3,1]),
        ],
        goal_description="Agent reaches goal while avoiding dead ends and finding optimal path through maze.",
        target_object_id="agent",
        reference_object_id="goal",
        target_distance=0.2,
    ),
    
    "spatial_memory_sequence": SpatialTask(
        task_id="spatial_memory_sequence",
        description="Remember and reproduce a complex spatial sequence with multiple objects and relationships.",
        initial_objects=[
            ObjectState(id="target_1", type="cube", position=[-1.5, 0, 0.1], scale=[0.2, 0.2, 0.2], color_rgba=[1,0,0,1]),
            ObjectState(id="target_2", type="sphere", position=[0, 1.5, 0.1], scale=[0.2, 0.2, 0.2], color_rgba=[0,1,0,1]),
            ObjectState(id="target_3", type="cube", position=[1.5, 0, 0.1], scale=[0.2, 0.2, 0.2], color_rgba=[0,0,1,1]),
            ObjectState(id="movable_1", type="cube", position=[-2, -2, 0.1], scale=[0.15, 0.15, 0.15], color_rgba=[1,0.5,0.5,1]),
            ObjectState(id="movable_2", type="sphere", position=[0, -2, 0.1], scale=[0.15, 0.15, 0.15], color_rgba=[0.5,1,0.5,1]),
            ObjectState(id="movable_3", type="cube", position=[2, -2, 0.1], scale=[0.15, 0.15, 0.15], color_rgba=[0.5,0.5,1,1]),
            ObjectState(id="sequence_marker", type="sphere", position=[0, 0, 0.05], scale=[0.05, 0.05, 0.05], color_rgba=[1,1,1,1]),
        ],
        goal_description="Move objects to targets in correct sequence: red cube to red target, green sphere to green target, blue cube to blue target.",
        target_object_id="movable_1",
        reference_object_id="target_1",
        target_distance=0.1,
    ),
    
    # Control conditions for statistical analysis
    "random_baseline": SpatialTask(
        task_id="random_baseline",
        description="Random object placement task (baseline control for statistical comparison).",
        initial_objects=[
            ObjectState(id="random_obj", type="cube", position=[random.uniform(-1, 1), random.uniform(-1, 1), 0.1], 
                       scale=[0.2, 0.2, 0.2], color_rgba=[0.5,0.5,0.5,1]),
        ],
        goal_description="Random task - no specific goal (control condition).",
        target_object_id="random_obj",
        reference_object_id="random_obj",
        target_distance=0.5,
    ),
    
    "simple_baseline": SpatialTask(
        task_id="simple_baseline", 
        description="Extremely simple single-object movement (minimal complexity baseline).",
        initial_objects=[
            ObjectState(id="simple_cube", type="cube", position=[0, 0, 0.1], scale=[0.2, 0.2, 0.2], color_rgba=[1,1,1,1]),
            ObjectState(id="simple_target", type="sphere", position=[0.5, 0, 0.1], scale=[0.1, 0.1, 0.1], color_rgba=[0,1,0,1]),
        ],
        goal_description="Move white cube to green target (simplest possible task).",
        target_object_id="simple_cube",
        reference_object_id="simple_target",
        target_distance=0.1,
    ),
}

# Generate full catalog with complexity variants
SPATIAL_TASKS_CATALOG = {}

# Add base tasks
for task_name, task in BASE_TASKS.items():
    SPATIAL_TASKS_CATALOG[task_name] = task
    
    # Generate complexity variants for experimental rigor
    if task_name not in ["random_baseline", "simple_baseline"]:  # Don't add variants to control conditions
        for complexity in [1, 2, 3]:  # Low, medium, high complexity
            variants = generate_complexity_variants(task, complexity)
            for variant in variants:
                SPATIAL_TASKS_CATALOG[variant.task_id] = variant

class TaskInfo(BaseModel):
    task_name: Optional[str] = None
    task_params: Optional[Dict[str, Any]] = None

@app.post("/setup_environment", status_code=201)
async def setup_environment_endpoint(request: TaskInfo):
    global spatial_env_instance
    if not spatial_env_instance:
        print("ERROR: /setup_environment called but spatial_env_instance is None.")
        raise HTTPException(
            status_code=500,
            detail="Spatial environment instance not available. Check server logs for startup errors.",
        )

    task_name = request.task_name
    if not task_name or task_name not in SPATIAL_TASKS_CATALOG:
        print(f"WARN: Task '{task_name}' not found or not provided. Selecting a random task.")
        task_name = random.choice(list(SPATIAL_TASKS_CATALOG.keys()))
    
    selected_task = SPATIAL_TASKS_CATALOG[task_name]
    
    # Add a unique identifier to the task_id to differentiate runs
    unique_task_id = f"{selected_task.task_id}_{uuid.uuid4().hex[:6]}"
    final_task = selected_task.copy(update={"task_id": unique_task_id})

    try:
        print(f"API CALL: /setup_environment - Initializing task: {final_task.task_id}")
        await spatial_env_instance.initialize_task(final_task)
        print(f"API CALL: /setup_environment - Task '{final_task.task_id}' initialized.")
        return {
            "message": f"Environment initialized with task: {task_name}",
            "task_id": final_task.task_id,
            "status": "SUCCESS",
        }
    except Exception as e:
        print(f"ERROR in /setup_environment: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Failed to initialize environment: {str(e)}"
        )


@app.post("/execute_action")
async def execute_action_endpoint():
    global spatial_env_instance
    if not spatial_env_instance:
        print("ERROR: /execute_action called but spatial_env_instance is None.")
        raise HTTPException(
            status_code=500, detail="Spatial environment instance not available."
        )
    if (
        not hasattr(spatial_env_instance, "current_task")
        or not spatial_env_instance.current_task
    ):
        raise HTTPException(
            status_code=400,
            detail="Environment not initialized with a task. Call /setup_environment first.",
        )

    target_obj_id = spatial_env_instance.current_task.target_object_id
    ref_obj_initial_pos = [0.0, 0.0, 0.0]  # Default if not found
    # Find the reference object's initial position to make the action relative
    for obj_state in spatial_env_instance.current_task.initial_objects:
        if obj_state.id == spatial_env_instance.current_task.reference_object_id:
            ref_obj_initial_pos = obj_state.position
            break

    # Hardcoded action: move target_obj_id slightly towards where reference_object_id was initially
    action_to_apply = {
        "action_type": "move_object",
        "object_id": target_obj_id,
        "target_position": [
            (
                ref_obj_initial_pos[0] + 0.1
                if target_obj_id == "red_cube"
                else ref_obj_initial_pos[0] - 0.1
            ),  # Simplistic move towards center
            ref_obj_initial_pos[1],
            ref_obj_initial_pos[2],
        ],
    }

    try:
        task_id = spatial_env_instance.current_task.task_id
        print(
            f"API CALL: /execute_action for task '{task_id}' - Applying action: {action_to_apply}"
        )
        outcome = await spatial_env_instance.apply_action_and_get_outcome(
            action_to_apply
        )
        obs_msg = outcome.get("observation", "No observation string found in outcome.")
        print(
            f"API CALL: /execute_action for task '{task_id}' - Observation: {obs_msg}"
        )

        return {
            "message": "Action executed.",
            "task_id": task_id,
            "action_applied": action_to_apply,
            "observation": obs_msg,
            "reward": outcome.get("reward"),
            "done": outcome.get("done"),
            "full_outcome_debug": outcome,  # Useful for debugging
        }
    except Exception as e:
        print(f"ERROR in /execute_action: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Failed to execute action: {str(e)}"
        )


@app.post("/run_schelling_simulation")
async def run_schelling_simulation(params: SchellingExperimentParams):
   """
   Runs a Schelling Segregation Model simulation.
   """
   try:
       model = SchellingModel(
           grid_size=params.grid_size,
           empty_ratio=params.empty_ratio,
           agent_groups=params.agent_groups,
           satisfaction_threshold=params.satisfaction_threshold,
       )
       result = model.run_full_simulation(max_steps=params.max_steps)
       return result
   except Exception as e:
       raise HTTPException(status_code=500, detail=str(e))


# Old mock definitions and Pydantic models from previous version are removed.
# The uvicorn.run call is handled by Dockerfile CMD.
