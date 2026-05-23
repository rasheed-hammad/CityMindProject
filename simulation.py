# 20 step simulation
import random

class CitySimulation:
    def __init__(self, city_graph):
        self.graph = city_graph
        self.step = 0
        self.event_log = []
        self.flood_history = []
        self.active_emergencies = []
        self.resolved_emergencies = []

        # chaos mode flag
        self.chaos_mode = False

        # event rates
        self._rates_normal = {'flood': 0.30, 'clear': 0.20, 'emergency': 0.40,'path_bias': 0.75}
        self._rates_chaos = {'flood': 0.90, 'clear': 0.10, 'emergency': 0.90,'path_bias': 0.95}

    def set_chaos_mode(self, enabled: bool):
        self.chaos_mode = bool(enabled)
        if self.chaos_mode:
            self.log("chaos mode enabled", important=True)
        else:
            self.log("chaos mode disabled")

    def _rate(self, key):
        return (self._rates_chaos if self.chaos_mode else self._rates_normal)[key]

    def log(self, msg, important=False):
        
        prefix = "[!] " if important else ""
        event = f"{prefix}[Step {self.step}] {msg}"
        self.event_log.append(event)
        print(event)

    def random_flood(self, ambulance_manager = None):
   
        available = [(u, v) for (u, v, d) in self.graph.graph.edges(data=True)
                    if d.get('exists') and not d.get('blocked')]

        if not available:
            return False

        if random.random() >= self._rate('flood'):
            return False

        edge = random.choice(available)

        self.graph.graph.edges[edge]['blocked'] = True
        self.flood_history.append(edge)

        self.log(f"road {edge[0]}<->{edge[1]} flooded!", important=True)
        self.log("recalculating routes...")
        return True

    def _collect_active_path_edges(self, ambulance_manager):
       
        edges = set()

        for amb in ambulance_manager.ambulances:
            path = amb.get('path') or []
            idx = amb.get('path_index', 0)

            remaining = path[idx + 1:]

            for u, v in zip(remaining, remaining[1:]):
                edges.add((u, v))

        return edges

    def random_clear(self):
        blocked = [(u, v) for (u, v, d) in self.graph.graph.edges(data=True)
                  if d.get('blocked')]

        if blocked and random.random() < self._rate('clear'):
            edge = random.choice(blocked)
            self.graph.graph.edges[edge]['blocked'] = False

            self.log(f"road {edge[0]}<->{edge[1]} cleared")
            return True

        return False
    # emergency
    def generate_emergency(self):
        residential = [n for n in self.graph.graph.nodes()
                      if self.graph.graph.nodes[n]['type'] == 'Residential']

        if residential and random.random() < self._rate('emergency'):
            location = random.choice(residential)

            active_locations = [e[0] for e in self.active_emergencies]

            if location not in active_locations:
                self.active_emergencies.append((location, self.step))
                self.log(f"emergency at {location}!", important=True)
                return location

        return None
        # emergency solver
    def resolve_emergency(self, location):

        for e in self.active_emergencies[:]:
            if e[0] == location:
                self.active_emergencies.remove(e)
                self.resolved_emergencies.append((location, self.step))
                self.log(f"civilian at {location} rescued!")
                return True

        return False
    
    def run_step(self, ambulance_manager=None):
        self.step += 1
        self.log("=== new step ===")

        flooded = self.random_flood(ambulance_manager)
        cleared = self.random_clear()
        emergency = self.generate_emergency()

        if not flooded and not cleared and not emergency:
            self.log("city operating normally")

        self.graph.recompute_accessibility()

        total = sum(1 for (u, v, d) in self.graph.graph.edges(data=True)
                    if d.get('exists'))
        blocked = sum(1 for (u, v, d) in self.graph.graph.edges(data=True)
                      if d.get('blocked'))

        return total, blocked