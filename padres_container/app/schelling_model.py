import random
from typing import List, Tuple, Dict, Any

class SchellingModel:
    """
    Implements Schelling's Segregation Model.
    """

    def __init__(self, grid_size: int, empty_ratio: float, agent_groups: List[int], satisfaction_threshold: float):
        self.grid_size = grid_size
        self.empty_ratio = empty_ratio
        self.agent_groups = agent_groups
        self.satisfaction_threshold = satisfaction_threshold
        self.grid: List[List[int]] = [[0] * grid_size for _ in range(grid_size)]
        self.agents: Dict[Tuple[int, int], int] = {}
        self._setup_grid()

    def _setup_grid(self):
        """Populates the grid with agents and empty spaces."""
        num_empty = int(self.grid_size * self.grid_size * self.empty_ratio)
        num_agents = self.grid_size * self.grid_size - num_empty
        
        locations = [(r, c) for r in range(self.grid_size) for c in range(self.grid_size)]
        random.shuffle(locations)

        for i in range(num_agents):
            loc = locations[i]
            group = random.choice(self.agent_groups)
            self.grid[loc[0]][loc[1]] = group
            self.agents[loc] = group

    def is_satisfied(self, r: int, c: int) -> bool:
        """Checks if an agent at a given location is satisfied."""
        agent_group = self.grid[r][c]
        if agent_group == 0:
            return True  # Empty spaces are always "satisfied"

        neighbors = []
        similar_neighbors = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size and self.grid[nr][nc] != 0:
                    neighbors.append(self.grid[nr][nc])
                    if self.grid[nr][nc] == agent_group:
                        similar_neighbors += 1
        
        if not neighbors:
            return True # No neighbors, so not unhappy

        return (similar_neighbors / len(neighbors)) >= self.satisfaction_threshold

    def run_simulation_step(self) -> Dict[str, Any]:
        """Runs a single step of the simulation."""
        unhappy_agents = []
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if self.grid[r][c] != 0 and not self.is_satisfied(r, c):
                    unhappy_agents.append((r, c))

        if not unhappy_agents:
            return {"moved_agents": 0, "unhappy_count": 0, "is_stable": True}

        empty_locations = [(r, c) for r in range(self.grid_size) for c in range(self.grid_size) if self.grid[r][c] == 0]
        random.shuffle(unhappy_agents)

        moved_agents = 0
        for r, c in unhappy_agents:
            if not empty_locations:
                break  # No more empty spots to move to
            
            new_loc = empty_locations.pop(0)
            agent_group = self.grid[r][c]
            
            # Move agent
            self.grid[new_loc[0]][new_loc[1]] = agent_group
            self.grid[r][c] = 0
            
            # Update agent dictionary
            del self.agents[(r, c)]
            self.agents[new_loc] = agent_group
            
            moved_agents += 1

        return {"moved_agents": moved_agents, "unhappy_count": len(unhappy_agents), "is_stable": False}

    def run_full_simulation(self, max_steps: int = 100) -> Dict[str, Any]:
        """Runs the simulation until it stabilizes or max_steps is reached."""
        history = []
        for step in range(max_steps):
            step_result = self.run_simulation_step()
            history.append({
                "step": step,
                "unhappy_count": step_result["unhappy_count"],
                "moved_agents": step_result["moved_agents"],
                "grid": [row[:] for row in self.grid] # Deep copy of the grid state
            })
            if step_result["is_stable"]:
                return {"status": "stable", "steps": step + 1, "history": history}
        
        return {"status": "max_steps_reached", "steps": max_steps, "history": history}
