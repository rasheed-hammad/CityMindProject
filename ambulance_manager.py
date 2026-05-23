# Ambulance Manager Emergency Dispatch and Routing
# Uses A* routing from Challenge 4

from challanges.challange4_routing import EmergencyRouter

class AmbulanceManager:
    def __init__(self, city_graph, initial_positions):
        self.graph = city_graph
        self.router = EmergencyRouter(city_graph)
        
        #const
        default_CS = 65
        self.ambulances = []
        for i, (row, col) in enumerate(initial_positions):
            self.ambulances.append({
                'id': i,
                'row': row,
                'col': col,
                'x': col * default_CS + default_CS / 2,
                'y': row * default_CS + default_CS / 2,
                '_cell_size': default_CS,           
                'target': None,
                'path': [],
                'path_index': 0,
                'speed': 2.0,                       
                'status': 'idle',                  
                'emergency_location': None,         
                'home': (row, col),                
            })
    # responsing to emergnecies
    def dispatch_to_emergencies(self, simulation):
        
        for emergency_loc, step_created in simulation.active_emergencies:
    
            already_assigned = any(
                amb['emergency_location'] == emergency_loc
                for amb in self.ambulances
            )
            if already_assigned:
                continue
            
            best_amb = None
            best_dist = float('inf')
            for amb in self.ambulances:
                if amb['status'] == 'idle':
                    dist = abs(amb['row'] - emergency_loc[0]) + abs(amb['col'] - emergency_loc[1])
                    if dist < best_dist:
                        best_dist = dist
                        best_amb = amb
            
            if best_amb:
                best_amb['status'] = 'responding'
                best_amb['emergency_location'] = emergency_loc
                best_amb['target'] = emergency_loc
                self._calculate_path(best_amb)
                simulation.log(f"Ambulance {best_amb['id']} dispatched to {emergency_loc}")
    
        for amb in self.ambulances:
            if amb['status'] != 'idle':
                continue
            home = amb.get('home')
            if home is None:
                continue
            
            at_home = (amb['row'], amb['col']) == home
            no_path = (not amb['path']) or amb['path_index'] >= len(amb['path']) - 1
            if at_home and no_path:
                amb['target'] = None
                amb['path'] = []
                continue
            if not at_home and (no_path or amb['target'] != home):
                amb['target'] = home
                self._calculate_path(amb)
    # using A* for path
    def _calculate_path(self, ambulance):
        start = (ambulance['row'], ambulance['col'])
        target = ambulance['target']
        
        if not target:
            return
        
        path = self.router.find_path(start, target)
        
        if path:
            ambulance['path'] = path
            ambulance['path_index'] = 0
        else:
            ambulance['path'] = []
            ambulance['target'] = None
    
    def update(self, cell_size=65, simulation=None):
        for amb in self.ambulances:
            if amb['_cell_size'] != cell_size:
                if amb['x'] is None or amb['_cell_size'] is None:
                    amb['x'] = amb['col'] * cell_size + cell_size / 2
                    amb['y'] = amb['row'] * cell_size + cell_size / 2
                else:
                    ratio = cell_size / amb['_cell_size']
                    amb['x'] *= ratio
                    amb['y'] *= ratio
                amb['_cell_size'] = cell_size

            if not amb['path'] or amb['path_index'] >= len(amb['path']) - 1:
                if amb['status'] == 'responding' and amb['emergency_location']:
                    if simulation:
                        simulation.resolve_emergency(amb['emergency_location'])
                    amb['status'] = 'idle'
                    amb['emergency_location'] = None
                    amb['target'] = None
                continue
            
            next_waypoint = amb['path'][amb['path_index'] + 1]
        
            target_x = next_waypoint[1] * cell_size + cell_size / 2
            target_y = next_waypoint[0] * cell_size + cell_size / 2
            
            dx = target_x - amb['x']
            dy = target_y - amb['y']
            distance = (dx**2 + dy**2) ** 0.5
            
            if distance < amb['speed']:
              
                amb['x'] = target_x
                amb['y'] = target_y
                amb['row'] = next_waypoint[0]
                amb['col'] = next_waypoint[1]
                amb['path_index'] += 1
            else:
                amb['x'] += (dx / distance) * amb['speed']
                amb['y'] += (dy / distance) * amb['speed']
    
    def handle_road_change(self):
        for amb in self.ambulances:
            if amb['target']:
                self._calculate_path(amb)
    
    def get_positions(self):
        return self.ambulances
    
    def reassign_home_positions(self, new_positions):
            # Update ambulance home according to latest GA positions
            
        for i, amb in enumerate(self.ambulances):
            if i >= len(new_positions):
                continue
            new_home = new_positions[i]
            amb['home'] = new_home
            if amb['status'] == 'idle':
                amb['target'] = new_home
                self._calculate_path(amb)