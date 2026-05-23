# shared city graph for all challanges

import networkx as nx

class CityGraph:
    def __init__(self, rows=10, cols=10):
        self.rows = rows
        self.cols = cols
        self.graph = nx.Graph()
        self._initialize_empty_grid()
    
    def _initialize_empty_grid(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.graph.add_node(
                    (r, c),
                    type=None,
                    population_density=0,
                    risk_index=0.0,
                    accessibility=True
                )
        
        for r in range(self.rows):
            for c in range(self.cols):
                if c < self.cols - 1:
                    self.graph.add_edge(
                        (r, c), (r, c+1),
                        travel_cost=1.0,
                        base_travel_cost=1.0,
                        blocked=False,
                        exists=False
                    )
                if r < self.rows - 1:
                    self.graph.add_edge(
                        (r, c), (r+1, c),
                        travel_cost=1.0,
                        base_travel_cost=1.0,
                        blocked=False,
                        exists=False
                    )
    
    def set_node_type(self, position, building_type, density=0):
        self.graph.nodes[position]['type'] = building_type
        self.graph.nodes[position]['population_density'] = density
        
        if building_type == 'Residential':
            for neighbor in self.graph.neighbors(position):
                if self.graph.has_edge(position, neighbor):
                    self.graph.edges[position, neighbor]['travel_cost'] = 0.8
                    self.graph.edges[position, neighbor]['base_travel_cost'] = 0.8
    # building type
    def get_node_type(self, position):
        return self.graph.nodes[position]['type']
    
    def get_neighbors(self, position):
        return list(self.graph.neighbors(position))
    
    def get_all_buildings(self):
        return [node for node in self.graph.nodes() 
                if self.graph.nodes[node]['type'] is not None]
    
    def update_edge_costs_with_risk(self):
        for u, v, data in self.graph.edges(data=True):
            risk_u = self.graph.nodes[u].get('risk_index', 0.0)
            risk_v = self.graph.nodes[v].get('risk_index', 0.0)
            avg_risk = (risk_u + risk_v) / 2.0
            data['travel_cost'] = data['base_travel_cost'] * (1 + avg_risk)
    # accessibilty if path blocked or not
    def recompute_accessibility(self):
        
        for node in self.graph.nodes():
            reachable = False
            for nbr in self.graph.neighbors(node):
                d = self.graph.edges[node, nbr]
                if d.get('exists') and not d.get('blocked'):
                    reachable = True
                    break
            self.graph.nodes[node]['accessibility'] = reachable
    
    def __str__(self):
        return f"CityGraph({self.rows}x{self.cols}, {len(self.graph.nodes)} nodes)"


if __name__ == "__main__":
    print("="*50)
    print("Testing CityGraph")
    print("="*50)
    
    graph = CityGraph(10, 10)
    print(f" Graph created: {graph}")
    print(f" Total nodes: {len(graph.graph.nodes)}")
    print(f" Total edges: {len(graph.graph.edges)}")
    
    graph.set_node_type((1, 2), 'Hospital', density=200)
    print(f" Node (1,2) type: {graph.get_node_type((1, 2))}")
    
    neighbors = graph.get_neighbors((5, 5))
    print(f" Node (5,5) has {len(neighbors)} neighbors")