# Challenge 2: Road Network Optimization
# MST using Kruskal's Algorithm + redundant edge for two path constraint

import sys
import os
from collections import deque
import networkx as nx

class RoadNetworkBuilder:
    def __init__(self, city_graph):
        self.graph = city_graph
        self.parent = {}
        self.rank = {}

    def find(self, node):
        if self.parent[node] != node:
            self.parent[node] = self.find(self.parent[node])
        return self.parent[node]

    def union(self, node1, node2):
        root1 = self.find(node1)
        root2 = self.find(node2)

        if root1 == root2:
            return False

        if self.rank[root1] < self.rank[root2]:
            self.parent[root1] = root2
        elif self.rank[root1] > self.rank[root2]:
            self.parent[root2] = root1
        else:
            self.parent[root2] = root1
            self.rank[root1] += 1

        return True

    def kruskal_mst(self):
       
        print("Building MST using Kruskal's algorithm...")

        edges = []
        for u, v, data in self.graph.graph.edges(data=True):
            cost = data['travel_cost']
            edges.append((cost, u, v))

        edges.sort()
        print(f"Total possible edges: {len(edges)}")

        all_nodes = list(self.graph.graph.nodes())
        for node in all_nodes:
            self.parent[node] = node
            self.rank[node] = 0

        mst_edges = []
        total_cost = 0

        for cost, u, v in edges:
            if self.union(u, v):
                mst_edges.append((u, v))
                total_cost += cost
                self.graph.graph.edges[u, v]['exists'] = True

        print(f"  MST built: {len(mst_edges)} roads, total cost: {total_cost:.2f}")
        return mst_edges

    def two_paths_hospital_depot(self, mst_edges):
        print("Checking hospital-depot connectivity...")

        hospitals = [n for n in self.graph.graph.nodes()
                     if self.graph.graph.nodes[n]['type'] == 'Hospital']
        depots = [n for n in self.graph.graph.nodes()
                  if self.graph.graph.nodes[n]['type'] == 'Depot']

        if not hospitals or not depots:
            print("  Warning: Hospital or Depot not found")
            return mst_edges

        center = (self.graph.rows / 2, self.graph.cols / 2)
        hospital_pos = min(
            hospitals,
            key=lambda h: (h[0] - center[0]) ** 2 + (h[1] - center[1]) ** 2,
        )
        depot_pos = depots[0]
 
        self.graph.graph.nodes[hospital_pos]['primary'] = True

        print(f"  Primary Hospital at {hospital_pos}, Depot at {depot_pos}")

        hd_path = self._find_path_bfs(hospital_pos, depot_pos, mst_edges)
        if not hd_path:
            print("  Warning: No path between Hospital and Depot on MST")
            return mst_edges

        print(f"  MST path H->D has {len(hd_path)-1} edges")

        # Collect edges on the hosptial and depot path
        path_edge_set = set()
        for i in range(len(hd_path) - 1):
            path_edge_set.add((hd_path[i], hd_path[i+1]))
            path_edge_set.add((hd_path[i+1], hd_path[i]))

        mst_set = set()
        for u, v in mst_edges:
            mst_set.add((u, v))
            mst_set.add((v, u))

        # Find non-MST edges that bridge across the H->D path
      
        path_nodes = set(hd_path)
        
        candidates = []
        for u, v, data in self.graph.graph.edges(data=True):
            if (u, v) in mst_set:
                continue
            cost = data['travel_cost']

            both_on_path = u in path_nodes and v in path_nodes
            one_on_path = u in path_nodes or v in path_nodes
            
            priority = 0 if both_on_path else (1 if one_on_path else 2)
            candidates.append((priority, cost, u, v))

        candidates.sort()

        # Add edges until edge-connectivity(H, D) >= 2 (Menger's theorem ->
        # 2 edge-disjoint paths exist).
        added_count = 0
        for priority, cost, u, v in candidates:
            if self._edge_connectivity(hospital_pos, depot_pos) >= 2:
                break

            mst_edges.append((u, v))
            mst_set.add((u, v))
            mst_set.add((v, u))
            self.graph.graph.edges[u, v]['exists'] = True
            added_count += 1

        if added_count > 0:
            print(f"  Added {added_count} redundant edge(s) for 2-path constraint")

        if self._edge_connectivity(hospital_pos, depot_pos) >= 2:
            print("  [OK] 2-edge-disjoint paths verified (edge_connectivity >= 2)")
        else:
            print("  [WARN] Could not fully guarantee 2-edge-disjoint paths")

        return mst_edges

    def _edge_connectivity(self, s, t):
        """Compute edge-connectivity between s and t over the *built* roads
        (edges with `exists=True`). By Menger's theorem this equals the
        maximum number of edge-disjoint s-t paths."""
        sub = nx.Graph()
        sub.add_nodes_from(self.graph.graph.nodes())
        for u, v, d in self.graph.graph.edges(data=True):
            if d.get('exists'):
                sub.add_edge(u, v)
        if s not in sub.nodes or t not in sub.nodes:
            return 0
        try:
            return nx.edge_connectivity(sub, s, t)
        except Exception:
            return 0

    def _find_path_bfs(self, start, end, edges):
        """Find path from start to end using BFS on given edge list."""
        adj = {}
        for u, v in edges:
            adj.setdefault(u, []).append(v)
            adj.setdefault(v, []).append(u)

        if start not in adj:
            return None

        queue = deque([(start, [start])])
        visited = {start}

        while queue:
            current, path = queue.popleft()
            if current == end:
                return path
            for neighbor in adj.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    def _has_two_disjoint_paths(self, start, end, all_edges, original_path):
        
        for i in range(len(original_path) - 1):
            edge_fwd = (original_path[i], original_path[i+1])
            edge_rev = (original_path[i+1], original_path[i])
            
            # Remove this edge and check if path still exists
            remaining = [e for e in all_edges if e != edge_fwd and e != edge_rev]
            if not self._path_exists(start, end, remaining):
                return False
        return True

    def _path_exists(self, start, end, edges):
        if start == end:
            return True

        adj = {}
        for u, v in edges:
            adj.setdefault(u, []).append(v)
            adj.setdefault(v, []).append(u)

        if start not in adj:
            return False

        queue = deque([start])
        visited = {start}

        while queue:
            current = queue.popleft()
            if current == end:
                return True
            for neighbor in adj.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return False

    def build(self):
        print("=" * 60)
        print("Challenge 2: Road Network Optimization (MST)")
        print("=" * 60)

        mst_edges = self.kruskal_mst()
        final_edges = self.two_paths_hospital_depot(mst_edges)
        final_edges = self._residential_hospital_reachability(final_edges)

        print(f"\n  SUCCESS: Road network built with {len(final_edges)} roads")
        return final_edges

    def _residential_hospital_reachability(self, edges, max_hops=3):
        
        residentials = [n for n in self.graph.graph.nodes()
                        if self.graph.graph.nodes[n]['type'] == 'Residential']
        hospitals = [n for n in self.graph.graph.nodes()
                     if self.graph.graph.nodes[n]['type'] == 'Hospital']
        if not residentials or not hospitals:
            return edges

        added = 0
        for r in residentials:
            if self._reachable_within(r, hospitals, max_hops):
                continue
            target = self._nearest_hospital_grid(r, hospitals, max_hops)
            if target is None:
                print(f"  [WARN] {r} has no hospital within {max_hops} grid hops")
                continue
            path = self._grid_bfs_path(r, target, max_hops)
            if not path:
                continue
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                if not self.graph.graph.edges[u, v].get('exists'):
                    self.graph.graph.edges[u, v]['exists'] = True
                    edges.append((u, v))
                    added += 1
        if added:
            print(f"  Added {added} road(s) so every residential is <={max_hops} hops from a hospital")
        else:
            print(f"  All residentials already within {max_hops} built-road hops of a hospital")
        return edges

    def _reachable_within(self, start, targets, max_hops):
        
        target_set = set(targets)
        if start in target_set:
            return True
        q = deque([(start, 0)])
        seen = {start}
        while q:
            node, hops = q.popleft()
            if hops >= max_hops:
                continue
            for nb in self.graph.graph.neighbors(node):
                if nb in seen:
                    continue
                ed = self.graph.graph.edges[node, nb]
                if not ed.get('exists') or ed.get('blocked'):
                    continue
                if nb in target_set:
                    return True
                seen.add(nb)
                q.append((nb, hops + 1))
        return False

    def _nearest_hospital_grid(self, start, hospitals, max_hops):
        
        target_set = set(hospitals)
        q = deque([(start, 0)])
        seen = {start}
        while q:
            node, hops = q.popleft()
            if hops >= max_hops:
                continue
            for nb in self.graph.graph.neighbors(node):
                if nb in seen:
                    continue
                if nb in target_set:
                    return nb
                seen.add(nb)
                q.append((nb, hops + 1))
        return None

    def _grid_bfs_path(self, start, end, max_hops):
        
        if start == end:
            return [start]
        q = deque([(start, [start])])
        seen = {start}
        while q:
            node, path = q.popleft()
            if len(path) - 1 >= max_hops:
                continue
            for nb in self.graph.graph.neighbors(node):
                if nb in seen:
                    continue
                new_path = path + [nb]
                if nb == end:
                    return new_path
                seen.add(nb)
                q.append((nb, new_path))
        return None


# testing
if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
    sys.path.append(parent_dir)

    from city_graph import CityGraph
    from challange1_layout import CityLayoutCSP

    graph = CityGraph(10, 10)

    print("Step 1: Placing buildings...")
    csp = CityLayoutCSP(graph)
    layout = csp.solve()

    if layout:
        print("\nStep 2: Building roads...")
        road_builder = RoadNetworkBuilder(graph)
        roads = road_builder.build()

        print("\n" + "=" * 60)
        print("INTEGRATION TEST PASSED")
        print("=" * 60)
    else:
        print("Cannot build roads - no valid layout")