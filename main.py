
#CityMind project

import pygame
import sys
from city_graph import CityGraph
from challanges.challange1_layout import CityLayoutCSP
from challanges.challange2_roads import RoadNetworkBuilder
from challanges.challange3_ambulance import AmbulancePlacement
from challanges.challange5_crime import CrimePredictor
from simulation import CitySimulation
from UI.renderer import CityRenderer
from ambulance_manager import AmbulanceManager


def build_session():
    # building city and runing algos
    print("[W] Initializing system...\n")

    city = CityGraph(10, 10)
    print("   [OK] City grid created")

    layout_solver = CityLayoutCSP(city)
    layout = layout_solver.solve()
    if not layout:
        print("\n[X] ERROR: Layout planning failed")
        return None
    print(f"   [OK] Placed {len(layout)} buildings")

    print("\n   --- Post-solve constraint check ---")
    ok, viol = layout_solver.validate_all_constraints(layout)
    if ok:
        print("   [PASS] All Challenge-1 rules satisfied (8-way adjacency,")
        print("          residential<=3 hops to hospital, power<=2 hops to industrial)")
    else:
        print("   [FAIL] Layout violates rules:")
        for v in viol:
            print(f"     - {v['constraint']}: {len(v['positions'])} violation(s)")
            for p in v['positions'][:5]:
                print(f"         {p}")

    road_builder = RoadNetworkBuilder(city)
    roads = road_builder.build()
    print(f"   [OK] Built {len(roads)} roads")

    city.recompute_accessibility()

    crime = CrimePredictor(city)
    crime.cluster_neighborhoods()
    crime.train_classifier()
    crime.update_graph_risk()
    police_plan = crime.calculate_police_deployments()
    deployed_police = {}
    print("   [OK] Crime analysis complete. Police deployment plan generated.")

    ambulance_placer = AmbulancePlacement(city, num_ambulances=3)
    ambulance_positions = ambulance_placer.optimize()
    print(f"   [OK] Deployed {len(ambulance_positions)} ambulances")

    sim = CitySimulation(city)
    ambulance_mgr = AmbulanceManager(city, ambulance_positions)
    ambulance_mgr.dispatch_to_emergencies(sim)

    return {
        'city': city,
        'layout': layout,
        'crime': crime,
        'police_plan': police_plan,
        'deployed_police': deployed_police,
        'ambulance_placer': ambulance_placer,
        'sim': sim,
        'ambulance_mgr': ambulance_mgr,
    }


def main():
    print("\n" + "="*70)
    print(" "*22 + "[C]  CITYMIND")
    print(" "*15 + "Urban Intelligence System")
    print("="*70 + "\n")

    pygame.init()
    clock = pygame.time.Clock()
    renderer = None
    running = True

    while running:
        # new session
        session = build_session()
        if session is None:
            return

        city = session['city']
        layout = session['layout']
        crime = session['crime']
        police_plan = session['police_plan']
        deployed_police = session['deployed_police']
        ambulance_placer = session['ambulance_placer']
        sim = session['sim']
        ambulance_mgr = session['ambulance_mgr']

        if renderer is None:
            renderer = CityRenderer(city, cell_size=65)
        else:
            renderer.graph = city
        renderer._police_locations = deployed_police

        print("\n" + "="*70)
        print("[G] LAUNCHING SIMULATION")
        print("="*70 + "\n")

        view_mode = 'city'
        paused = False
        last_step_time = pygame.time.get_ticks()
        step_interval = 3000
        restart_requested = False

        while running and sim.step < 20 and not restart_requested:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                result = renderer.handle_button_events(event)

                if result:
                    action_type, action = result

                    if action_type == 'control':
                        if action == 'play':
                            paused = False
                            print("[>]  Simulation RUNNING")
                        elif action == 'pause':
                            paused = True
                            print("[||]  Simulation PAUSED")
                        elif action == 'step':
                            total, blocked = sim.run_step(ambulance_manager=ambulance_mgr)
                            if police_plan:
                                node = police_plan.pop(0)
                                crime.apply_police_deployment(node)
                                deployed_police[node] = deployed_police.get(node, 0) + 1
                                sim.event_log.append(f"[Step {sim.step}] Police: Officer deployed to {node} to reduce crime!")
                            ambulance_mgr.handle_road_change()
                            ambulance_mgr.dispatch_to_emergencies(sim)
                        elif action == 'chaos':
                            sim.set_chaos_mode(not sim.chaos_mode)
                            print(f"[!]  Chaos mode: {'ON' if sim.chaos_mode else 'OFF'}")

                    elif action_type == 'view':
                        view_mode = action
                        print(f"[E]  View mode: {view_mode.upper()}")

            if not paused and pygame.time.get_ticks() - last_step_time > step_interval:
                total_roads, blocked_roads = sim.run_step(ambulance_manager=ambulance_mgr)

                if police_plan:
                    node = police_plan.pop(0)
                    crime.apply_police_deployment(node)
                    deployed_police[node] = deployed_police.get(node, 0) + 1
                    sim.event_log.append(f"[Step {sim.step}] Police: Officer deployed to {node} to reduce crime!")

                ambulance_mgr.handle_road_change()

                if sim.step % 5 == 0:
                    new_positions = ambulance_placer.re_evaluate()
                    if new_positions:
                        ambulance_mgr.reassign_home_positions(new_positions)
                        print(f"   [OK] Ambulances re-positioned to {new_positions}")

                ambulance_mgr.dispatch_to_emergencies(sim)
                last_step_time = pygame.time.get_ticks()

            if not paused:
                ambulance_mgr.update(cell_size=renderer.cell_size, simulation=sim)

            total_roads = sum(1 for (u, v, d) in city.graph.edges(data=True) if d.get('exists'))
            blocked_roads = sum(1 for (u, v, d) in city.graph.edges(data=True) if d.get('blocked'))

            stats = {
                'step': sim.step,
                'roads': total_roads,
                'blocked': blocked_roads,
                'ambulances': len(ambulance_mgr.ambulances),
                'buildings': len(layout),
                'emergencies': len(sim.active_emergencies),
                'rescued': len(sim.resolved_emergencies),
                'police': sum(deployed_police.values()),
                'chaos': sim.chaos_mode, 
            }

            renderer.render(
                ambulances=ambulance_mgr.get_positions(),
                event_log=sim.event_log,
                stats=stats,
                view_mode=view_mode,
                paused=paused,
                emergencies=sim.active_emergencies
            )

            clock.tick(60)

        if not running:
            break
        if restart_requested:
            continue

        print("\n" + "="*70)
        print("[OK] SIMULATION COMPLETE")
        print(f"   Steps completed: {sim.step}/20")
        print("="*70 + "\n")

        # start again option
        finished_loop = True
        while finished_loop and running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    finished_loop = False
                    break
                result = renderer.handle_button_events(event, finished=True)
                if result and result == ('control', 'run_again'):
                    print("[R] Run Again pressed -- rebuilding city...\n")
                    finished_loop = False

            renderer.render(
                ambulances=ambulance_mgr.get_positions(),
                event_log=sim.event_log,
                stats=stats,
                view_mode=view_mode,
                paused=True,
                emergencies=sim.active_emergencies,
                finished=True,
            )
            clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()