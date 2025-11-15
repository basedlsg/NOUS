import asyncio
import sys
import os
import argparse

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend_services.experiment_orchestrator import ExperimentOrchestrator
from backend_services.mcp_manager import MCPManager
from backend_services.mcp_servers.padres_mcp_server import PadresMCPServer

async def main(satisfaction_threshold: float):
    """
    Configures and runs a Schelling Segregation Model experiment.
    """
    # Configuration for the Padres MCP Server
    padres_config = {
        "mock_mode": False,
        "service_base_url": "http://localhost:8088",
    }

    # Create and register the Padres MCP Server
    padres_server = PadresMCPServer(server_name="padres_main", config=padres_config)
    
    mcp_manager = MCPManager()
    mcp_manager.register_server(padres_server)

    # Create the Experiment Orchestrator
    orchestrator = ExperimentOrchestrator(mcp_manager)

    # Define the Schelling experiment configuration
    schelling_experiment_config = {
        "id": "schelling_validation_001",
        "schelling_parameters": {
            "grid_size": 50,
            "agent_groups": [1, 2],
            "satisfaction_threshold": satisfaction_threshold,
            "empty_ratio": 0.1,
            "max_steps": 1000, # Increased max_steps for larger grid
        },
    }

    print(f"--- Running Schelling Segregation Model Experiment (Satisfaction Threshold: {satisfaction_threshold}) ---")
    try:
        results = await orchestrator.run_schelling_experiment(schelling_experiment_config)
        print("\n--- Experiment Results ---")
        print(f"Status: {results.get('status')}")
        print(f"Steps: {results.get('steps')}")
        # Optionally, print the final grid from the last step in history
        if results.get('history'):
            final_grid = results['history'][-1]['grid']
            print("\nFinal Grid State:")
            for row in final_grid:
                print(" ".join(map(str, row)))

    except Exception as e:
        print(f"\n--- Experiment Failed ---")
        print(f"An error occurred: {e}")
    finally:
        await padres_server.close_client()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a Schelling Segregation Model experiment.")
    parser.add_argument(
        "--satisfaction_threshold",
        type=float,
        required=True,
        help="The satisfaction threshold for agents (e.g., 0.3, 0.5, 0.7).",
    )
    args = parser.parse_args()

    # This script requires the padres_container to be running
    # To run it:
    # 1. cd padres_container
    # 2. uvicorn app.main:app --host 0.0.0.0 --port 8088
    #
    # Then, in a separate terminal, run this script from the project root:
    # python -m scripts.run_schelling_validation --satisfaction_threshold 0.3
    
    # Note: You might need to adjust PYTHONPATH if running from a different directory
    # export PYTHONPATH=$PYTHONPATH:$(pwd)
    
    asyncio.run(main(args.satisfaction_threshold))