<div align="center">

# CityMind

### Urban Intelligence System

*An AI-driven city simulator where five algorithms cooperate on a single shared graph to plan layout, build roads, position ambulances, route around floods, and predict crime risk in real time.*

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2.5%2B-FFD43B)
![NetworkX](https://img.shields.io/badge/NetworkX-3.0%2B-FF6F00)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Complete-success.svg)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Algorithms](#algorithms)
  - [Challenge 1 — Layout Planning (CSP)](#challenge-1--layout-planning-csp)
  - [Challenge 2 — Road Network (Kruskal MST)](#challenge-2--road-network-kruskal-mst)
  - [Challenge 3 — Ambulance Placement (Genetic Algorithm)](#challenge-3--ambulance-placement-genetic-algorithm)
  - [Challenge 4 — Emergency Routing (A\*)](#challenge-4--emergency-routing-a)
  - [Challenge 5 — Crime Risk Prediction (K-Means + Random Forest)](#challenge-5--crime-risk-prediction-k-means--random-forest)
- [The Crime Feedback Loop](#the-crime-feedback-loop)
- [Simulation Engine](#simulation-engine)
- [Renderer](#renderer)
- [What Makes It Cohesive](#what-makes-it-cohesive)
- [Team](#team)
- [License](#license)

---

## Overview

CityMind models a 10×10 urban grid as a graph and runs five different AI techniques over the same shared structure. Each module reads from and writes to one [CityGraph](cci:2://file:///d:/Semester-4/AI/CityMindProject/city_graph.py:4:0-80:83) object, so a change made by one algorithm is immediately visible to every other algorithm.

The simulation runs for 20 steps. Roads flood live, emergencies appear at random residentials, ambulances dispatch and reroute around blocked roads, the genetic algorithm re-evaluates positions every 5 steps, and police officers are deployed proportionally to predicted crime risk. A **Chaos Mode** toggle stress-tests the system by sharply increasing flood and emergency rates.

---

![CityMind Demo](docs/demo.gif)

---

## Key Features

<table>
<tr>
<td width="50%" valign="top">

**Five cooperating AI techniques**
CSP, MST, GA, A\*, and an ML pipeline — all sharing one graph object.

**Real-time pygame UI**
Four view modes: City, Roads, Coverage, Crime.

**Dynamic events**
Roads flood and clear, emergencies appear, ambulances reroute on the fly.

</td>
<td width="50%" valign="top">

**End-to-end feedback loop**
Crime predictions change edge costs, which change routes, which change ambulance placements.

**Chaos Mode**
Stress-test toggle that pushes flood and emergency rates to extremes.

**Built from scratch**
No scikit-learn. Only `pygame` and `networkx` required.

</td>
</tr>
</table>

---

## Tech Stack

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Pygame-2.5%2B-FFD43B?logo=python&logoColor=black" alt="Pygame"/>
  <img src="https://img.shields.io/badge/NetworkX-3.0%2B-FF6F00" alt="NetworkX"/>
  <img src="https://img.shields.io/badge/Algorithms-From%20Scratch-brightgreen" alt="From Scratch"/>
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-blue" alt="Platform"/>
</p>

| Layer | Tool | Purpose |
|---|---|---|
| **Language** | Python 3.10+ | Core implementation |
| **Graph** | NetworkX | Edge connectivity, graph utilities |
| **Visualization** | pygame | Real-time UI and animation |
| **Algorithms** | Custom | CSP, Kruskal, GA, A\*, K-Means, Random Forest — no ML libs |

---

## Usage

### Run the full simulation

```bash
python main.py
```

### Run any challenge standalone (for testing)

```bash
python challanges/challange1_layout.py
python challanges/challange2_roads.py
```

### UI controls

| Button | Action |
|---|---|
| **Play / Pause** | Start or freeze the simulation |
| **Step** | Advance one simulation step manually |
| **Chaos** | Toggle high flood / high emergency rates |
| **City / Roads / Coverage / Crime** | Switch between four view modes |
| **Run Again** (after step 20) | Rebuild a brand new city |

---

## Project Structure

```
CityMindProject/
├── city_graph.py              # Shared CityGraph (single source of truth)
├── main.py                    # Entry point and UI loop
├── simulation.py              # Per-step events: floods, emergencies
├── ambulance_manager.py       # Dispatch, movement, replanning
├── challanges/
│   ├── challange1_layout.py   # CSP building placement
│   ├── challange2_roads.py    # Kruskal MST + 2-path redundancy
│   ├── challange3_ambulance.py# Genetic Algorithm placement
│   ├── challange4_routing.py  # A* shortest-path routing
│   └── challange5_crime.py    # K-Means + Random Forest
├── UI/
│   └── renderer.py            # pygame visualization
└── README.md
```

---

## How It Works

When `python main.py` runs, the project executes in this order:

1. **Create the empty grid** — [CityGraph(10, 10)](cci:2://file:///d:/Semester-4/AI/CityMindProject/city_graph.py:4:0-80:83).
2. **Place buildings** — [CityLayoutCSP.solve()](cci:1://file:///d:/Semester-4/AI/CityMindProject/challanges/challange1_layout.py:510:4-529:23) runs CSP backtracking with forward checking to position 31 buildings while satisfying spatial constraints.
3. **Build roads** — [RoadNetworkBuilder.build()](cci:1://file:///d:/Semester-4/AI/CityMindProject/challanges/challange2_roads.py:225:4-235:26) constructs a Kruskal MST, adds redundancy edges so the Hospital-to-Depot link is 2-edge-connected, then patches any residential not within 3 road hops of a hospital.
4. **Recompute accessibility** of all nodes.
5. **Crime analysis** — [CrimePredictor](cci:2://file:///d:/Semester-4/AI/CityMindProject/challanges/challange5_crime.py:274:0-514:33) runs K-Means clustering, trains a Random Forest, writes risk indices onto nodes, multiplies edge costs by `(1 + avg_risk)`, and prepares a police deployment plan.
6. **Place ambulances** — [AmbulancePlacement.optimize()](cci:1://file:///d:/Semester-4/AI/CityMindProject/challanges/challange3_ambulance.py:121:4-173:29) runs a Genetic Algorithm using A\* travel cost as fitness.
7. **Launch the simulation loop** — for each of 20 steps:
   - Flood / clear roads, generate emergencies.
   - Deploy one queued police officer.
   - Re-run A\* for every busy ambulance.
   - Every 5 steps, re-run a fast mini-GA to reposition ambulances.
   - Move ambulances along their paths.
   - Render the frame.

---

## Algorithms

### Challenge 1 — Layout Planning (CSP)

**Goal:** Place 31 buildings (3 Hospital, 12 Residential, 5 Industrial, 6 School, 4 Power, 1 Depot) under three rules:
- Industrial not adjacent to Hospital or School (8-way).
- Every Residential within 3 hops of a Hospital.
- Every Power within 2 hops of an Industrial.

**Approach:** Backtracking + Forward Checking + a domain-aware value-ordering heuristic. If no solution exists, a min-conflict fallback identifies the conflicting rule and produces the lowest-violation layout possible.

**Why not AC-3?** AC-3 only handles binary constraints. Our 3-hop and 2-hop rules are global distance constraints — AC-3 would add overhead without pruning anything useful.

**Why not pure min-conflicts?** It cannot prove infeasibility or identify which rule is unsatisfiable. We use it only as a fallback.

---

### Challenge 2 — Road Network (Kruskal MST)

**Goal:** Connect all buildings at minimum cost, with two independent routes between the primary Hospital and the Depot.

**Approach:**
1. **Kruskal's MST** with Union-Find (path compression + union-by-rank) for the optimal minimum-cost spanning tree.
2. **Redundancy via Menger's theorem** — keep adding the cheapest non-MST edges until `nx.edge_connectivity(Hospital, Depot) ≥ 2`. This is the only mathematically correct way to guarantee a backup route survives any single road failure.
3. **Reachability patch** — ensure every Residential is within 3 *built-road* hops of a Hospital.

**Why not GA?** MST has a polynomial exact solution. GA would trade a mathematical optimality guarantee for a slower approximation.

**Why not Prim's?** Equally optimal, but offers no advantage on our sparse graph.

---

### Challenge 3 — Ambulance Placement (Genetic Algorithm)

**Goal:** Place 3 ambulances to minimize the **worst-case** response time (k-center / minimax problem).

**Approach:** GA with population 50, 100 generations, top-50% selection, single-point crossover, 20% mutation rate. Fitness = `−max_distance_from_any_building_to_nearest_ambulance`, computed using A\* on the live graph (so risk multipliers and blocked roads are respected). A faster mini-GA re-runs every 5 simulation steps.

**Why not brute force?** C(31, 3) is feasible now but does not scale to larger grids.

**Why not simulated annealing?** Single-path search struggles on the bumpy minimax landscape; GA's population maintains diversity.

---

### Challenge 4 — Emergency Routing (A\*)

**Goal:** Find the shortest currently-available path from any cell to any other, while roads may flood mid-journey.

**Approach:** A\* with `heuristic = manhattan(current, goal) * 0.8`. The 0.8 factor is the **minimum possible edge cost** in our graph (residential edges), which keeps the heuristic admissible and consistent. When a flood blocks a road, the ambulance manager simply re-runs A\* from the ambulance's current cell.

**Why not greedy best-first?** Not optimal — unacceptable for emergency response.

**Why not Dijkstra?** Optimal but slower; A\* with an admissible heuristic gives the same guarantee with directional pull toward the goal.

---

### Challenge 5 — Crime Risk Prediction (K-Means + Random Forest)

**Two-part ML pipeline:**

**Part A — K-Means++ clustering (unsupervised):** Groups neighborhoods by `[population_density, industrial_proximity]` into 3 clusters. K-Means++ initialization plus `n_init=10` ensures stable, reproducible clusters across simulation restarts.

**Part B — Random Forest classification (supervised):** Custom-built (50 trees, max depth 6, Gini impurity, bootstrap sampling, feature subset size = √n_features). Trained on rule-based ground-truth labels (Industrial = High; dense residential near industrial = High; hospitals/schools = Low; etc.).

**Why not DBSCAN?** Leaves nodes labeled as noise — we need every neighborhood classified.

**Why not single decision tree?** Overfits on our small dataset of ~31 nodes.

**Why not KNN?** Silently dominated by feature scale (density in hundreds vs. proximity in single digits) and slow at predict time.

---

## The Crime Feedback Loop

This is what makes the project end-to-end rather than five disconnected modules.

```
   K-Means clusters  ──►  Random Forest predicts  ──►  risk_index written to nodes
                                                            │
                                                            ▼
                                          edge_cost = base × (1 + avg_risk)
                                                            │
                                                            ▼
                              A* sees costlier paths   ◄──── GA repositions
                              through risky areas           ambulances every 5 steps
                                                            │
                                                            ▼
                              Police deployed to High-risk areas first
                              (apply_police_deployment multiplies risk by 0.6)
                                                            │
                                                            ▼
                              Risk drops, edge costs drop, routes shift again
```

When a police officer is deployed to a node, that node's `risk_index` drops by 40%, edge costs around it decrease, A\* reroutes ambulances accordingly, and the GA repositions on its next re-evaluation. The whole system reacts as one.

---

## Simulation Engine

[CitySimulation](cci:2://file:///d:/Semester-4/AI/CityMindProject/simulation.py:3:0-129:29) (in [simulation.py](cci:7://file:///d:/Semester-4/AI/CityMindProject/simulation.py:0:0-0:0)) is the clock and weather of the city. Each [run_step()](cci:1://file:///d:/Semester-4/AI/CityMindProject/simulation.py:111:4-129:29):

- Possibly floods one random built road.
- Possibly clears one currently flooded road.
- Possibly creates a new emergency at a random Residential.
- Recomputes node accessibility from the Depot.
- Appends events to `event_log` for the Live Events panel.

[AmbulanceManager](cci:2://file:///d:/Semester-4/AI/CityMindProject/ambulance_manager.py:5:0-149:41) (in [ambulance_manager.py](cci:7://file:///d:/Semester-4/AI/CityMindProject/ambulance_manager.py:0:0-0:0)) handles dispatch, movement, and replanning. It runs A\* whenever a road changes and moves each ambulance pixel-by-pixel along its planned path.

---

## Renderer

[CityRenderer](cci:2://file:///d:/Semester-4/AI/CityMindProject/UI/renderer.py:228:0-1118:19) (in [UI/renderer.py](cci:7://file:///d:/Semester-4/AI/CityMindProject/UI/renderer.py:0:0-0:0)) is a pygame visualizer. It owns the window, top bar, four view modes, particle effects (siren pulses, industrial smoke), animated flood ripples, the Live Events panel, and the completion overlay.

The renderer is purely a consumer of the shared graph — it never modifies state.

---

## What Makes It Cohesive

1. **Single shared graph.** Every module passes [CityGraph](cci:2://file:///d:/Semester-4/AI/CityMindProject/city_graph.py:4:0-80:83) by reference. No copies, no synchronization.
2. **End-to-end feedback loop.** Crime prediction changes edge costs, which change routes, which change ambulance placements, which inform police deployment, which lowers crime risk.
3. **Robust under chaos.** Each module is designed to be re-callable on the current graph state, so flooded roads, new emergencies, and shifting risk are handled gracefully — even with Chaos Mode pushing event rates to extremes.


