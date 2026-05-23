# Challenge 1: City Layout Planning
# CSP solver using Backtracking with Forward Checking

import sys
import os
from collections import deque
import random


class CityLayoutCSP:
    def __init__(self, city_graph):
        self.graph = city_graph
        self.rows = city_graph.rows
        self.cols = city_graph.cols

        self.building_requirements = {
            'Hospital': 3,
            'Residential': 12,
            'Industrial': 5,
            'School': 6,
            'Power': 4,
            'Depot': 1
        }

        self.constraints = self._define_constraints()

    def _define_constraints(self):
        return [
            {
                'name': 'Industrial not adjacent to Hospital',
                'check': self._industrial_hospital_adjacent
            },
            {
                'name': 'Industrial not adjacent to School',
                'check': self._industrial_school_adjacent
            },
            {
                'name': 'Residential within 3 hops of Hospital',
                'check': self._residential_hospital_distance
            },
            {
                'name': 'Power within 2 hops of Industrial',
                'check': self._power_industrial_distance
            }
        ]

    # bfs calculating distance moving through complete grid not layout

    def _bfs_road_hops(self, start, end, max_hops):
        
        if start == end:
            return True
        
        queue = deque([(start, 0)])  
        visited = {start}
        
        while queue:
            current, hops = queue.popleft()
            
            if hops >= max_hops:
                continue
  
            for neighbor in self.graph.get_neighbors(current):
                if neighbor in visited:
                    continue
                
                if neighbor == end:
                    return True  
                
                visited.add(neighbor)
                queue.append((neighbor, hops + 1))
        
        return False  

    #constraint checking
    def _get_grid_neighbors(self, pos):
        r, c = pos
        out = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    out.append((nr, nc))
        return out

    def _industrial_hospital_adjacent(self, layout):
        violations = []
        for pos, building_type in layout.items():
            if building_type == 'Industrial':
                for neighbor in self._get_grid_neighbors(pos):
                    if layout.get(neighbor) == 'Hospital':
                        violations.append((pos, neighbor))
        return (len(violations) == 0, violations)

    def _industrial_school_adjacent(self, layout):
     
        violations = []
        for pos, building_type in layout.items():
            if building_type == 'Industrial':
                for neighbor in self._get_grid_neighbors(pos):
                    if layout.get(neighbor) == 'School':
                        violations.append((pos, neighbor))
        return (len(violations) == 0, violations)

    def _residential_hospital_distance(self, layout):
        #using bfs
        violations = []
        hospitals = [pos for pos, btype in layout.items() if btype == 'Hospital']

        if len(hospitals) < self.building_requirements['Hospital']:
            return (True, [])

        for pos, btype in layout.items():
            if btype == 'Residential':
                reachable = any(
                    self._bfs_road_hops(pos, h, max_hops=3)
                    for h in hospitals
                )
                
                if not reachable:
                    violations.append((pos, "No hospital within 3 road hops"))

        return (len(violations) == 0, violations)
    # within two hops distance
    def _power_industrial_distance(self, layout):
        
        violations = []
        industrials = [pos for pos, btype in layout.items() if btype == 'Industrial']
        powers = [pos for pos, btype in layout.items() if btype == 'Power']

        if len(industrials) < self.building_requirements['Industrial']:
            return (True, [])

        for pw in powers:
            min_dist = min(
                abs(pw[0] - ind[0]) + abs(pw[1] - ind[1])
                for ind in industrials
            )
            if min_dist > 2:
                violations.append((pw, f"Power has no industrial within 2 hops (nearest={min_dist})"))

        return (len(violations) == 0, violations)

    def validate_all_constraints(self, layout):
        violations = []
        for constraint in self.constraints:
            is_valid, violated_positions = constraint['check'](layout)
            if not is_valid:
                violations.append({
                    'constraint': constraint['name'],
                    'positions': violated_positions
                })
        return (len(violations) == 0, violations)

    # placement checking

    def _check_placement(self, layout, pos, building_type):
       
        # rule 1 industrial not adjacent to hospital or School
        if building_type == 'Industrial':
            for neighbor in self._get_grid_neighbors(pos):
                nb_type = layout.get(neighbor)
                if nb_type in ('Hospital', 'School'):
                    return False

        if building_type in ('Hospital', 'School'):
            for neighbor in self._get_grid_neighbors(pos):
                if layout.get(neighbor) == 'Industrial':
                    return False

        # rule 2 Residential within 3 hops of Hospital
        
        hospitals = [p for p, bt in layout.items() if bt == 'Hospital']
        if len(hospitals) == self.building_requirements['Hospital']:
            if building_type == 'Residential':
                min_dist = min(
                    abs(pos[0] - h[0]) + abs(pos[1] - h[1]) for h in hospitals
                )
                if min_dist > 3:
                    return False
            if building_type == 'Hospital':
                for p, bt in layout.items():
                    if bt == 'Residential':
                        min_dist = min(
                            abs(p[0] - h[0]) + abs(p[1] - h[1]) for h in hospitals
                        )
                        if min_dist > 3:
                            return False

        # rule 3 power within 2 hops of an Industrial 
        industrials = [p for p, bt in layout.items() if bt == 'Industrial']
        if building_type == 'Power' and industrials:
            min_dist = min(
                abs(pos[0] - ind[0]) + abs(pos[1] - ind[1]) for ind in industrials
            )
            if min_dist > 2:
                return False

        return True

    def _adjacency_conflict(self, type_a, type_b):
        bad_pairs = {
            ('Industrial', 'Hospital'), ('Hospital', 'Industrial'),
            ('Industrial', 'School'),   ('School',   'Industrial')
        }
        return (type_a, type_b) in bad_pairs

    # setting position smartly

    def _get_candidate_positions(self, building_type, available_positions, layout):
        
        available_positions = list(available_positions)
        random.shuffle(available_positions)
        
        hospitals = [p for p, bt in layout.items() if bt == 'Hospital']
        industrials = [p for p, bt in layout.items() if bt == 'Industrial']
        same_type = [p for p, bt in layout.items() if bt == building_type]
        center = (self.rows // 2, self.cols // 2)

        if building_type == 'Power' and industrials:
            available_positions = [
                p for p in available_positions
                if min(abs(p[0]-i[0]) + abs(p[1]-i[1]) for i in industrials) <= 2
            ]

        if building_type == 'Residential' and hospitals:
            available_positions = [
                p for p in available_positions
                if min(abs(p[0]-h[0]) + abs(p[1]-h[1]) for h in hospitals) <= 3
            ]

        def score(pos):
            spacing = 0
            if same_type:
                min_same_dist = min(
                    abs(pos[0]-s[0]) + abs(pos[1]-s[1]) for s in same_type
                )
                spacing = -min_same_dist * 2  

            if building_type == 'Hospital':
                dist_to_center = abs(pos[0]-center[0]) + abs(pos[1]-center[1])
                mid_ring_bonus = -abs(dist_to_center - 3)
                return spacing + mid_ring_bonus

            elif building_type == 'Industrial':
                
                dist_to_center = abs(pos[0]-center[0]) + abs(pos[1]-center[1])
                edge_penalty = 0
                if pos[0] <= 0 or pos[0] >= self.rows-1:
                    edge_penalty += 2
                if pos[1] <= 0 or pos[1] >= self.cols-1:
                    edge_penalty += 2
                return spacing + edge_penalty

            elif building_type == 'Residential' and hospitals:
                nearest_hosp = min(
                    abs(pos[0]-h[0]) + abs(pos[1]-h[1]) for h in hospitals
                )
                hospital_penalty = max(0, nearest_hosp - 3) * 10
                return spacing + hospital_penalty

            elif building_type == 'Power' and industrials:
                # Prefer positions closest to the industrial having no power
               
                power_plants = [p for p, bt in layout.items() if bt == 'Power']
                
                best_score = float('inf')
                for ind in industrials:
                    ind_coverage = sum(
                        1 for pw in power_plants
                        if abs(ind[0]-pw[0]) + abs(ind[1]-pw[1]) <= 2
                    )
                    dist_to_ind = abs(pos[0]-ind[0]) + abs(pos[1]-ind[1])
                   
                    candidate_score = ind_coverage * 100 + dist_to_ind
                    best_score = min(best_score, candidate_score)
                
                return best_score

            elif building_type == 'School':
                if industrials:
                    nearest_ind = min(
                        abs(pos[0]-i[0]) + abs(pos[1]-i[1]) for i in industrials
                    )
                    return spacing - nearest_ind 
                return spacing

            elif building_type == 'Depot':
                dist_to_center = abs(pos[0]-center[0]) + abs(pos[1]-center[1])
                return dist_to_center  # Prefer near center

            else:
                return abs(pos[0]-center[0]) + abs(pos[1]-center[1])

        return sorted(available_positions, key=score)

    # backtracking search

    def backtracking_search(self, use_constraints=None):
        
        print("Starting backtracking search...")

        all_positions = [(r, c) for r in range(self.rows) for c in range(self.cols)]
            #using MRV placing bulidings
        assignments = []
        assignments.extend(['Hospital'] * self.building_requirements['Hospital'])
        assignments.extend(['Industrial'] * self.building_requirements['Industrial'])
        assignments.extend(['Power'] * self.building_requirements['Power'])
        assignments.extend(['Depot'] * self.building_requirements['Depot'])
        assignments.extend(['School'] * self.building_requirements['School'])
        assignments.extend(['Residential'] * self.building_requirements['Residential'])

        print(f"Total positions: {len(all_positions)}")
        print(f"Buildings to place: {len(assignments)}")
        
        original_constraints = self.constraints
        if use_constraints is not None:
            self.constraints = [original_constraints[i] for i in use_constraints]

        layout = {}
       
        self._nodes_explored = 0
        self._max_nodes = 5000  

        result = self._backtrack(layout, assignments, all_positions, 0)

        if self._nodes_explored >= self._max_nodes:
            print(f"[!] Backtracking aborted after exploring {self._max_nodes} nodes (too constrained).")

        self.constraints = original_constraints
        return result

    def _backtrack(self, layout, remaining_buildings, available_positions, depth):
    
        if getattr(self, '_nodes_explored', 0) >= getattr(self, '_max_nodes', 5000):
            return None
            
        self._nodes_explored += 1

        if not remaining_buildings:
            is_valid, _ = self.validate_all_constraints(layout)
            if is_valid:
                print(f"[OK] Valid solution found at depth {depth} after {self._nodes_explored} nodes!")
                return layout.copy()
            return None

        building = remaining_buildings[0]

        ordered_positions = self._get_candidate_positions(
            building, available_positions, layout
        )

        for pos in ordered_positions:
            idx = available_positions.index(pos)

            layout[pos] = building
       
            if not self._check_placement(layout, pos, building):
                del layout[pos]
                continue

            remaining_pos = available_positions[:idx] + available_positions[idx+1:]

            result = self._backtrack(
                layout, remaining_buildings[1:], remaining_pos, depth + 1
            )
            
            if result is not None:
                return result

            del layout[pos]

        return None
    # min conflict solution greedy + local search

    def _minimum_conflict_solution(self):
        
        print("\n Analyzing which constraints cause conflict...")

        all_constraint_indices = list(range(len(self.constraints)))
        conflicting_constraints = []

        for i, constraint in enumerate(self.constraints):
            print(f"  Testing without: '{constraint['name']}'...")
            subset = [j for j in all_constraint_indices if j != i]
            solution = self.backtracking_search(use_constraints=subset)
            if solution:
                conflicting_constraints.append(constraint['name'])
                print(f"    -> This constraint causes conflict")
            else:
                print(f"    -> Still infeasible without this")

        if conflicting_constraints:
            print(f"\n Conflicting constraint(s):")
            for name in conflicting_constraints:
                print(f"  [X] {name}")
        else:
            print(" Multiple constraints interact to cause infeasibility")


        print("\n Building minimum-conflict solution...")
        best_layout = self._greedy_placement()
        best_violations = self._count_violations(best_layout)

        max_iterations = 500
        positions = list(best_layout.keys())
        
        for iteration in range(max_iterations):
            if best_violations == 0:
                break

            _, violation_details = self.validate_all_constraints(best_layout)
            if not violation_details:
                break

            # Pick a violated position
            violated_pos = self._extract_violated_position(violation_details[0]['positions'][0])
            if violated_pos not in best_layout:
                continue

            # Try swapping with other positions
            improved = False
            random.shuffle(positions)
            for other_pos in positions:
                if other_pos == violated_pos:
                    continue

                # Swap
                best_layout[violated_pos], best_layout[other_pos] = \
                    best_layout[other_pos], best_layout[violated_pos]

                new_violations = self._count_violations(best_layout)
                if new_violations < best_violations:
                    best_violations = new_violations
                    improved = True
                    break
                else:
                    # Undo swap
                    best_layout[violated_pos], best_layout[other_pos] = \
                        best_layout[other_pos], best_layout[violated_pos]

        _, remaining_violations = self.validate_all_constraints(best_layout)
        print(f"\n Minimum-conflict solution: {best_violations} violation(s)")
        if remaining_violations:
            for v in remaining_violations:
                print(f"  [!] {v['constraint']}: {len(v['positions'])} violations")
        else:
            print("  [OK] All constraints satisfied!")

        return best_layout

    def _extract_violated_position(self, violation_entry):
        if isinstance(violation_entry, tuple):
            
            if isinstance(violation_entry[0], tuple):
                return violation_entry[0]
            if len(violation_entry) == 2 and isinstance(violation_entry[0], int):
                return violation_entry
        return violation_entry

    def _greedy_placement(self):
        all_positions = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        random.shuffle(all_positions)

        layout = {}
        priority = ['Hospital', 'Industrial', 'Power', 'Depot', 'School', 'Residential']
        assignments = []
        for bt in priority:
            assignments.extend([bt] * self.building_requirements[bt])

        for building in assignments:
            placed = False
            for pos in all_positions:
                if pos in layout:
                    continue
                
                layout[pos] = building
                ok = True
     
                if building == 'Industrial':
                    for nb in self.graph.get_neighbors(pos):
                        if layout.get(nb) in ('Hospital', 'School'):
                            ok = False
                            break
                elif building in ('Hospital', 'School'):
                    for nb in self.graph.get_neighbors(pos):
                        if layout.get(nb) == 'Industrial':
                            ok = False
                            break
                
                if ok:
                    placed = True
                    break
                else:
                    del layout[pos]

            if not placed:
                # Force placement
                for pos in all_positions:
                    if pos not in layout:
                        layout[pos] = building
                        break

        return layout

    def _count_violations(self, layout):
        total = 0
        for constraint in self.constraints:
            _, violated = constraint['check'](layout)
            total += len(violated)
        return total

    # main solver   

    def solve(self):
        
        print("=" * 60)
        print("Challenge 1: City Layout Planning (CSP)")
        print("=" * 60)

        solution = self.backtracking_search()

        if solution:
            print(f"\n[OK] SUCCESS: Valid layout found with {len(solution)} buildings")
            self._apply_solution_to_graph(solution)
            return solution
        else:
            print("\n[X] No valid layout via backtracking")
            print(" Identifying conflicting constraints...")
            min_conflict = self._minimum_conflict_solution()
            if min_conflict:
                self._apply_solution_to_graph(min_conflict)
                return min_conflict
            return None

    def _apply_solution_to_graph(self, solution):
        density_map = {
            'Hospital': 200, 'Residential': 600, 'Industrial': 800,
            'School': 300, 'Power': 100, 'Depot': 150
        }
        for position, building_type in solution.items():
            self.graph.set_node_type(
                position, building_type, density_map.get(building_type, 0)
            )
        print(" Layout applied to city graph")


# testing
if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
    sys.path.append(parent_dir)

    from city_graph import CityGraph

    graph = CityGraph(10, 10)
    csp = CityLayoutCSP(graph)
    solution = csp.solve()

    if solution:
        print("\nFinal Layout:")
        print("-" * 40)
        building_counts = {}
        for pos, building in solution.items():
            building_counts[building] = building_counts.get(building, 0) + 1
        for building, count in building_counts.items():
            print(f"  {building}: {count} buildings")

        # constraint verification
        print("\n" + "=" * 60)
        print("DETAILED CONSTRAINT VERIFICATION")
        print("=" * 60)

        industrials = [p for p, b in solution.items() if b == 'Industrial']
        hospitals = [p for p, b in solution.items() if b == 'Hospital']
        powers = [p for p, b in solution.items() if b == 'Power']
        residentials = [p for p, b in solution.items() if b == 'Residential']
        schools = [p for p, b in solution.items() if b == 'School']
            # industrial to school and hospital
        print("\n[Rule 1] Industrial NOT adjacent to Hospital/School:")
        rule1_ok = True
        for ind in industrials:
            for nb in csp._get_grid_neighbors(ind):
                nb_type = solution.get(nb)
                if nb_type in ('Hospital', 'School'):
                    print(f"  VIOLATION: Industrial{ind} adjacent to {nb_type}{nb}")
                    rule1_ok = False
        if rule1_ok:
            print("  [PASS] No violations")

        #  residnetial hosptial distance
        print("\n[Rule 2] Residential within 3 road hops of Hospital:")
        rule2_ok = True
        for res in residentials:
            reachable = any(csp._bfs_road_hops(res, h, 3) for h in hospitals)
            nearest = min(abs(res[0]-h[0]) + abs(res[1]-h[1]) for h in hospitals)
            status = "PASS" if reachable else "FAIL"
            print(f"  Residential{res} -> nearest hospital manhattan={nearest}, BFS reachable in 3 hops: {reachable} [{status}]")
            if not reachable:
                rule2_ok = False
        if rule2_ok:
            print("  [PASS] All residentials within 3 hops of a hospital")

        #  Power within 2 road hops of Industrial
        print("\n[Rule 3] Power within 2 road hops of Industrial:")
        rule3_ok = True
        for pw in powers:
            reachable = any(csp._bfs_road_hops(pw, ind, 2) for ind in industrials)
            nearest = min(abs(pw[0]-ind[0]) + abs(pw[1]-ind[1]) for ind in industrials)
            status = "PASS" if reachable else "FAIL"
            print(f"  Power{pw} -> nearest industrial manhattan={nearest}, BFS reachable in 2 hops: {reachable} [{status}]")
            if not reachable:
                rule3_ok = False
        if rule3_ok:
            print("  [PASS] All power plants within 2 hops of an industrial")
        else:
            print("  [FAIL] Some power plants violate the 2-hop rule!")

        print("\n[Rule 4] Full CSP validation:")
        is_valid, violations = csp.validate_all_constraints(solution)
        if is_valid:
            print("  [PASS] All constraints satisfied - this is a VALID solution (not min-conflict)")
        else:
            print("  [FAIL] Violations found (this would be a min-conflict solution):")
            for v in violations:
                print(f"    {v['constraint']}: {len(v['positions'])} violation(s)")