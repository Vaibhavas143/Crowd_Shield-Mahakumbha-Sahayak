import heapq

class PathfindingGraph:
    def __init__(self):
        # This is a simplified graph representation.
        # In a real-world scenario, this would be loaded from a map data source.
        # Nodes are represented by integers (e.g., 0, 1, 2, ...)
        # Edges are represented as (destination_node, distance)
        self.graph = {
            0: [(1, 10), (2, 5)],
            1: [(0, 10), (3, 8), (4, 15)],
            2: [(0, 5), (3, 12)],
            3: [(1, 8), (2, 12), (5, 7)],
            4: [(1, 15), (5, 6)],
            5: [(3, 7), (4, 6)]
        }
        # Mapping of nodes to approximate crowd density zones (e.g., stream IDs)
        # This is a placeholder and needs to be refined based on actual camera placement.
        self.node_crowd_zones = {
            0: None, # No camera coverage
            1: 0,    # Corresponds to video_streams[0]
            2: 1,    # Corresponds to video_streams[1]
            3: None,
            4: 2,    # Corresponds to video_streams[2]
            5: None
        }

    def get_neighbors(self, node):
        return self.graph.get(node, [])

    def get_crowd_cost(self, density_level):
        # Assign a cost multiplier based on crowd density
        if density_level == "Normal":
            return 1.0
        elif density_level == "High":
            return 5.0  # Significantly higher cost for high density
        elif density_level == "Critical":
            return 20.0 # Very high cost to avoid critical areas
        else:
            return 1.0 # Default for unknown or no density info

    def find_optimal_path(self, start_node, end_node, current_stream_densities):
        # Dijkstra's algorithm to find the shortest path considering crowd density
        distances = {node: float('inf') for node in self.graph}
        distances[start_node] = 0
        priority_queue = [(0, start_node)] # (cost, node)

        paths = {node: [] for node in self.graph}
        paths[start_node] = [start_node]

        while priority_queue:
            current_cost, current_node = heapq.heappop(priority_queue)

            if current_cost > distances[current_node]:
                continue

            if current_node == end_node:
                return paths[end_node]

            for neighbor, distance in self.get_neighbors(current_node):
                # Calculate crowd cost for the neighbor's zone
                crowd_zone_id = self.node_crowd_zones.get(neighbor)
                density_level = "Normal" # Default to normal if no info
                if crowd_zone_id is not None and crowd_zone_id < len(current_stream_densities):
                    density_level = current_stream_densities[crowd_zone_id]

                crowd_multiplier = self.get_crowd_cost(density_level)
                
                # Total cost is distance * crowd_multiplier
                new_cost = current_cost + (distance * crowd_multiplier)

                if new_cost < distances[neighbor]:
                    distances[neighbor] = new_cost
                    paths[neighbor] = paths[current_node] + [neighbor]
                    heapq.heappush(priority_queue, (new_cost, neighbor))
        
        return None # No path found
