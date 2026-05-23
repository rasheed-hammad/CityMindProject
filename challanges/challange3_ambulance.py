# Challenge 3: Ambulance Placement
# Genetic Algorithm to optimize ambulance positions

import random
import sys
import os

class AmbulancePlacement:
    def __init__(self, city_graph, num_ambulances=3):
        self.graph = city_graph
        self.num_ambulances = num_ambulances
        
        # A* router from Challenge 4
        from challanges.challange4_routing import EmergencyRouter
        self.router = EmergencyRouter(city_graph)
        
        self.valid_positions = [
            node for node in city_graph.graph.nodes()
            if city_graph.graph.nodes[node]['type'] is not None
        ]
        
        # GA parameters
        self.population_size = 50
        self.generations = 100
        self.mutation_rate = 0.2
        
        self._dist_cache = {}
        self._cache_valid = False
    
    def _precompute_distances(self):
        self._dist_cache = {}
        for source in self.valid_positions:
            self._dist_cache[source] = {}
            for target in self.valid_positions:
                if source == target:
                    self._dist_cache[source][target] = 0
                    continue
                    #using A* to find shortest path
                path = self.router.find_path(source, target)
                if path:
                    cost = 0
                    for i in range(len(path) - 1):
                        edge_data = self.graph.graph.edges.get((path[i], path[i+1]))
                        if edge_data is None:
                            edge_data = self.graph.graph.edges.get((path[i+1], path[i]))
                        if edge_data:
                            cost += edge_data['travel_cost']
                    self._dist_cache[source][target] = cost
                else:
                    self._dist_cache[source][target] = float('inf')
        self._cache_valid = True
    # getting distance btw two points on graph
    def _graph_distance(self, pos1, pos2):
        
        if not self._cache_valid:
            self._precompute_distances()
        
        if pos1 in self._dist_cache:
            return self._dist_cache[pos1].get(pos2, float('inf'))
     
        path = self.router.find_path(pos1, pos2)
        if path:
            cost = 0
            for i in range(len(path) - 1):
                edge_data = self.graph.graph.edges.get((path[i], path[i+1]))
                if edge_data is None:
                    edge_data = self.graph.graph.edges.get((path[i+1], path[i]))
                if edge_data:
                    cost += edge_data['travel_cost']
            return cost
        return float('inf')
    
    def _calculate_fitness(self, placement):
        if not self.valid_positions:
            return float('-inf')
        
        max_distance = 0
        
        for location in self.valid_positions:
            min_dist_to_ambulance = float('inf')
            
            for ambulance_pos in placement:
                dist = self._graph_distance(location, ambulance_pos)
                min_dist_to_ambulance = min(min_dist_to_ambulance, dist)
            
            max_distance = max(max_distance, min_dist_to_ambulance)
        
        return -max_distance 
    
    def _random_placement(self):
        return random.sample(self.valid_positions, self.num_ambulances)
    # crossover 
    def _crossover(self, parent1, parent2):
        child = []
    
        child.extend(parent1[:self.num_ambulances//2])
        
        for pos in parent2:
            if pos not in child and len(child) < self.num_ambulances:
                child.append(pos)
        
        while len(child) < self.num_ambulances:
            pos = random.choice(self.valid_positions)
            if pos not in child:
                child.append(pos)
        
        return child
    # mutation
    def _mutate(self, placement):
        if random.random() < self.mutation_rate:
            idx = random.randint(0, self.num_ambulances - 1)
            attempts = 0
            while attempts < 20:
                new_pos = random.choice(self.valid_positions)
                if new_pos not in placement:
                    placement[idx] = new_pos
                    break
                attempts += 1
        
        return placement
    # optimization using A*
    def optimize(self):
       
        print("="*60)
        print("Challenge 3: Ambulance Placement (Genetic Algorithm)")
        print("="*60)
        
        if len(self.valid_positions) < self.num_ambulances:
            print(f"[X] ERROR: Not enough buildings ({len(self.valid_positions)}) for {self.num_ambulances} ambulances")
            return []
        
        print("Precomputing graph distances using A* search...")
        self._precompute_distances()
        
        population = [self._random_placement() for _ in range(self.population_size)]
        
        best_fitness = float('-inf')
        best_placement = None
        
        print(f"Running GA: {self.generations} generations, population {self.population_size}")
        
        for generation in range(self.generations):
            
            fitness_scores = [(self._calculate_fitness(p), p) for p in population]
            fitness_scores.sort(reverse=True, key=lambda x: x[0])
            
            # Track best
            if fitness_scores[0][0] > best_fitness:
                best_fitness = fitness_scores[0][0]
                best_placement = fitness_scores[0][1]
                
                if generation % 20 == 0:
                    print(f"  Generation {generation}: Best fitness = {best_fitness:.2f}")
            
            # top 50 % selection 
            survivors = [p for (f, p) in fitness_scores[:self.population_size//2]]
            
            # Create new population
            new_population = survivors.copy()
            
            while len(new_population) < self.population_size:
                parent1 = random.choice(survivors)
                parent2 = random.choice(survivors)
                child = self._crossover(parent1, parent2)
                child = self._mutate(child)
                new_population.append(child)
            
            population = new_population
        
        print(f"\n SUCCESS: Optimal placement found")
        print(f"  Worst-case distance: {-best_fitness:.2f} (graph distance via A*)")
        print(f"  Ambulance positions: {best_placement}")
        
        return best_placement
    
    def re_evaluate(self):
        
        self._cache_valid = False  
        
        orig_gen = self.generations
        orig_pop = self.population_size
        # low paraemter for real time evalutaion
        self.generations = 20
        self.population_size = 15
        
        new_positions = self.optimize()
        
        # Restore original params
        self.generations = orig_gen
        self.population_size = orig_pop
        
        return new_positions
    
    def invalidate_cache(self):
        self._cache_valid = False


# testing
if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
    sys.path.append(parent_dir)
    
    from city_graph import CityGraph
    from challange1_layout import CityLayoutCSP
    
    # Create and populate graph
    graph = CityGraph(10, 10)
    csp = CityLayoutCSP(graph)
    layout = csp.solve()
    
    if layout:
        # Build roads first
        from challange2_roads import RoadNetworkBuilder
        road_builder = RoadNetworkBuilder(graph)
        roads = road_builder.build()
      
        placer = AmbulancePlacement(graph, num_ambulances=3)
        positions = placer.optimize()