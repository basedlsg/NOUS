import redis
import json

class StateManagerMCP:
    def __init__(self, redis_host='localhost', redis_port=6379):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=0)

    def save_state(self, simulation_id, state_data):
        """
        Saves the simulation state to Redis.
        
        Args:
            simulation_id (str): The ID of the simulation.
            state_data (dict): The simulation state to save.
        """
        state_json = json.dumps(state_data)
        self.redis_client.set(simulation_id, state_json)
        print(f"State for simulation {simulation_id} saved.")

    def load_state(self, simulation_id):
        """
        Loads the simulation state from Redis.
        
        Args:
            simulation_id (str): The ID of the simulation.
            
        Returns:
            dict: The loaded simulation state, or None if not found.
        """
        state_json = self.redis_client.get(simulation_id)
        if state_json:
            print(f"State for simulation {simulation_id} loaded.")
            return json.loads(state_json)
        else:
            print(f"No state found for simulation {simulation_id}.")
            return None