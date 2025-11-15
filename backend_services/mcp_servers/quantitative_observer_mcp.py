import numpy as np
import networkx as nx
from backend_services.mcp_servers.base_mcp_server import BaseMCPServer

class QuantitativeObserverMCPServer(BaseMCPServer):
    """
    MCP Server for calculating quantitative social science metrics from simulation state.
    """

    def _validate_config(self):
        """No specific config needed for this server."""
        pass

    def _initialize_client(self):
        """No client to initialize for this server."""
        pass

    def call_tool(self, tool_name: str, parameters: dict) -> any:
        """
        Executes a specific metric calculation tool.
        """
        if tool_name == "calculate_metrics":
            state_data = parameters.get("state_data")
            if not state_data:
                raise ValueError("'state_data' parameter is required for calculate_metrics tool.")
            return self.calculate_metrics(state_data)
        else:
            raise NotImplementedError(f"Tool '{tool_name}' is not supported by {self.server_name}.")

    def calculate_metrics(self, state_data: dict) -> dict:
        """
        Calculates all quantitative metrics from the simulation state.

        Args:
            state_data (dict): The JSON-serialized state object.

        Returns:
            dict: A dictionary containing the calculated metrics.
        """
        agents = state_data.get("agents", [])
        if not agents:
            return {
                "gini_coefficient": 0,
                "agent_centrality": {},
                "global_clustering_coefficient": 0,
            }

        metrics = {
            "gini_coefficient": self._calculate_gini_coefficient(agents),
            "agent_centrality": self._calculate_agent_centrality(agents),
            "global_clustering_coefficient": self._calculate_global_clustering_coefficient(agents),
        }
        return metrics

    def _calculate_gini_coefficient(self, agents: list) -> float:
        """Calculates the Gini coefficient for wealth inequality."""
        wealths = [agent.get("wealth", 0) for agent in agents]
        if not wealths:
            return 0.0
        
        wealths = np.array(wealths, dtype=np.float64)
        if np.sum(wealths) == 0:
            return 0.0

        sorted_wealths = np.sort(wealths)
        n = len(wealths)
        cum_wealths = np.cumsum(sorted_wealths, dtype=np.float64)
        # Calculate the area under the Lorenz curve.
        lorenz_area = cum_wealths.sum() / (n * np.sum(wealths))
        # Gini coefficient is 2 * (area between line of equality and Lorenz curve)
        return 1 - 2 * lorenz_area

    def _calculate_agent_centrality(self, agents: list) -> dict:
        """Calculates the degree centrality for each agent."""
        graph = self._create_social_graph(agents)
        if not graph.nodes:
            return {}
        return nx.degree_centrality(graph)

    def _calculate_global_clustering_coefficient(self, agents: list) -> float:
        """Calculates the global clustering coefficient of the social network."""
        graph = self._create_social_graph(agents)
        if not graph.nodes or len(graph) < 3:
            return 0.0
        # NetworkX's average_clustering is the global clustering coefficient
        return nx.average_clustering(graph)

    def _create_social_graph(self, agents: list) -> nx.Graph:
        """Creates a NetworkX graph from agent connections."""
        graph = nx.Graph()
        agent_ids = [agent["id"] for agent in agents]
        graph.add_nodes_from(agent_ids)

        for agent in agents:
            agent_id = agent["id"]
            connections = agent.get("connections", [])
            for connection_id in connections:
                if connection_id in agent_ids:
                    graph.add_edge(agent_id, connection_id)
        return graph