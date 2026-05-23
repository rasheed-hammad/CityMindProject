# Challenge 4: Emergency Routing
# A* search for shortest path with dynamic rerouting

import heapq
import sys
import os

class EmergencyRouter:
    def __init__(self, city_graph):
        self.graph = city_graph
    #admissible herusitic
    def _heuristic(self, pos1, pos2):
       
        manhattan = abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        return manhattan * 0.8  
    
    def find_path(self, start, goal):
    
        counter = 0
        frontier = [(0, counter, start, [start])]
        visited = set()
        g_scores = {start: 0}
        
        while frontier:
            f_score, _, current, path = heapq.heappop(frontier)
            
            if current == goal:
                return path
            
            if current in visited:
                continue
            
            visited.add(current)
            current_g = g_scores[current]
            
            # Check neighbors
            for neighbor in self.graph.get_neighbors(current):
                edge_data = self.graph.graph.edges.get((current, neighbor))
                if edge_data is None:
                    edge_data = self.graph.graph.edges.get((neighbor, current))
                
                if not edge_data:
                    continue
                
                if edge_data.get('blocked', False):
                    continue
                
                if not edge_data.get('exists', False):
                    continue
       
                tentative_g = current_g + edge_data['travel_cost']
                
                if neighbor in g_scores and tentative_g >= g_scores[neighbor]:
                    continue
                
                g_scores[neighbor] = tentative_g
                h_score = self._heuristic(neighbor, goal)
                f = tentative_g + h_score
                
                new_path = path + [neighbor]
                counter += 1
                heapq.heappush(frontier, (f, counter, neighbor, new_path))
        
        return None  
    
    def route_multi_target(self, start, targets, flood_callback=None):
        print("="*60)
        print("Challenge 4: Emergency Routing (A*)")
        print("="*60)
        
        all_paths = []
        current = start
        
        for i, target in enumerate(targets):
            print(f"\n[{i+1}/{len(targets)}] Routing from {current} to {target}...")
        
            if flood_callback:
                flooded = flood_callback()
                if flooded:
                    print(f"  [!] Road conditions changed! Recalculating route...")
            
            path = self.find_path(current, target)
            
            if path:
                print(f"  [OK] Path found: {len(path)} steps, cost: {self._path_cost(path):.2f}")
                all_paths.append(path)
                current = target
            else:
                print(f"  [X] No path available to {target}!")
                print(f"  Attempting to skip target {target} and continue...")
                continue
        
        print(f"\n  Reached {len(all_paths)}/{len(targets)} targets")
        return all_paths
    # total cost
    def _path_cost(self, path):
        total = 0
        for i in range(len(path) - 1):
            edge_data = self.graph.graph.edges.get((path[i], path[i+1]))
            if edge_data is None:
                edge_data = self.graph.graph.edges.get((path[i+1], path[i]))
            if edge_data:
                total += edge_data['travel_cost']
        return total


# testing
if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
    sys.path.append(parent_dir)
    
    from city_graph import CityGraph
    from challange1_layout import CityLayoutCSP
    from challange2_roads import RoadNetworkBuilder
    
    # Setup
    graph = CityGraph(10, 10)
    csp = CityLayoutCSP(graph)
    layout = csp.solve()
    
    if layout:
        road_builder = RoadNetworkBuilder(graph)
        roads = road_builder.build()
        
        # Test routing
        router = EmergencyRouter(graph)
        
        # Find two buildings
        hospitals = [pos for pos, btype in layout.items() if btype == 'Hospital']
        if len(hospitals) >= 2:
            path = router.find_path(hospitals[0], hospitals[1])
            if path:
                cost = router._path_cost(path)
                print(f"\n[OK] Test successful: Found path with {len(path)} steps, cost {cost:.2f}")
           
            print("\n--- Testing dynamic rerouting ---")
            import random
            
            def simulate_flood():
                available = [(u, v) for (u, v, d) in graph.graph.edges(data=True)
                            if d.get('exists') and not d.get('blocked')]
                if available and random.random() < 0.5:
                    edge = random.choice(available)
                    graph.graph.edges[edge]['blocked'] = True
                    print(f"  [FLOOD] Road {edge[0]}<->{edge[1]} flooded!")
                    return True
                return False
            
            residentials = [pos for pos, btype in layout.items() if btype == 'Residential']
            targets = residentials[:3]
            if targets:
                paths = router.route_multi_target(hospitals[0], targets, flood_callback=simulate_flood)