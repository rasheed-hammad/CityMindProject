
# Challenge 5 Crime Risk Prediction
# K-Means clustering + Random Forest classification

import random
import sys
import os
import math


def _accuracy_score(y_true, y_pred):
    correct = sum(1 for a, b in zip(y_true, y_pred) if a == b)
    return correct / len(y_true) if y_true else 0.0


def _train_test_split(X, y, test_size=0.25, random_state=42, stratify=None):

    rng = random.Random(random_state)

    if stratify is not None:
        # Group indices by class label
        class_idx = {}
        for i, label in enumerate(stratify):
            class_idx.setdefault(label, []).append(i)

        train_idx, test_idx = [], []
        for label, indices in class_idx.items():
            shuffled = indices[:]
            rng.shuffle(shuffled)
            n_test = max(1, int(len(shuffled) * test_size))
            test_idx.extend(shuffled[:n_test])
            train_idx.extend(shuffled[n_test:])
    else:
        indices = list(range(len(X)))
        rng.shuffle(indices)
        n_test = max(1, int(len(indices) * test_size))
        test_idx = indices[:n_test]
        train_idx = indices[n_test:]

    X_train = [X[i] for i in train_idx]
    X_test  = [X[i] for i in test_idx]
    y_train = [y[i] for i in train_idx]
    y_test  = [y[i] for i in test_idx]
    return X_train, X_test, y_train, y_test


# k mean algo

class KMeans:
    

    def __init__(self, n_clusters=3, random_state=42, n_init=10, max_iter=300):
        self.k          = n_clusters
        self.random_state = random_state
        self.n_init     = n_init
        self.max_iter   = max_iter
        self.centroids  = None

    @staticmethod
    def _dist2(a, b):
        return sum((x - y) ** 2 for x, y in zip(a, b))

    def _assign(self, X, centroids):
        labels = []
        for point in X:
            dists = [self._dist2(point, c) for c in centroids]
            labels.append(dists.index(min(dists)))
        return labels

    def _inertia(self, X, labels, centroids):
        return sum(self._dist2(X[i], centroids[labels[i]]) for i in range(len(X)))

    def _run_once(self, X, seed):
        rng = random.Random(seed)
        n_features = len(X[0])

        # K-Means++ initialization
        centroids = [list(X[rng.randrange(len(X))])]
        while len(centroids) < self.k:
            dists = [min(self._dist2(x, c) for c in centroids) for x in X]
            total = sum(dists)
            probs = [d / total for d in dists]
            # weighted random pick
            r = rng.random()
            cumulative = 0.0
            chosen = len(X) - 1
            for idx, p in enumerate(probs):
                cumulative += p
                if r <= cumulative:
                    chosen = idx
                    break
            centroids.append(list(X[chosen]))

        for _ in range(self.max_iter):
            labels = self._assign(X, centroids)

            # Recompute centroids
            new_centroids = []
            for k in range(self.k):
                pts = [X[i] for i in range(len(X)) if labels[i] == k]
                if pts:
                    new_c = [sum(p[j] for p in pts) / len(pts) for j in range(n_features)]
                else:
                    new_c = centroids[k][:]
                new_centroids.append(new_c)

            if new_centroids == centroids:
                break
            centroids = new_centroids

        return labels, centroids, self._inertia(X, labels, centroids)

    def fit_predict(self, X):

        X = [list(row) for row in X]         
        best_labels, best_centroids, best_inertia = None, None, float('inf')
        for i in range(self.n_init):
            labels, centroids, inertia = self._run_once(X, self.random_state + i)
            if inertia < best_inertia:
                best_inertia   = inertia
                best_labels    = labels
                best_centroids = centroids

        self.centroids = best_centroids
        return best_labels


class DecisionTree:
    
    def __init__(self, max_depth=6, min_samples_split=2,
                 max_features=None, random_state=0):
        self.max_depth        = max_depth
        self.min_samples_split = min_samples_split
        self.max_features     = max_features
        self.random_state     = random_state
        self._rng             = random.Random(random_state)
        self.tree             = None
    #using gini
    @staticmethod
    def _gini(y):
        if not y:
            return 0.0
        n = len(y)
        counts = {}
        for label in y:
            counts[label] = counts.get(label, 0) + 1
        return 1.0 - sum((c / n) ** 2 for c in counts.values())

    def _best_split(self, X, y, feature_indices):
        best_gini  = float('inf')
        best_feat  = None
        best_thresh = None
        n = len(y)

        for feat in feature_indices:
            values = sorted(set(row[feat] for row in X))
            thresholds = [(values[i] + values[i + 1]) / 2
                          for i in range(len(values) - 1)]

            for thresh in thresholds:
                left_y  = [y[i] for i in range(n) if X[i][feat] <= thresh]
                right_y = [y[i] for i in range(n) if X[i][feat] >  thresh]
                if not left_y or not right_y:
                    continue
                g = (len(left_y) / n) * self._gini(left_y) + \
                    (len(right_y) / n) * self._gini(right_y)
                if g < best_gini:
                    best_gini  = g
                    best_feat  = feat
                    best_thresh = thresh

        return best_feat, best_thresh

    def _build(self, X, y, depth):
      
        if (depth >= self.max_depth or
                len(y) < self.min_samples_split or
                len(set(y)) == 1):
            counts = {}
            for lbl in y:
                counts[lbl] = counts.get(lbl, 0) + 1
            return {'leaf': True, 'label': max(counts, key=counts.get)}

        n_features = len(X[0])
        if self.max_features:
            k = min(self.max_features, n_features)
            feat_idx = self._rng.sample(range(n_features), k)
        else:
            feat_idx = list(range(n_features))

        feat, thresh = self._best_split(X, y, feat_idx)
        if feat is None:
            counts = {}
            for lbl in y:
                counts[lbl] = counts.get(lbl, 0) + 1
            return {'leaf': True, 'label': max(counts, key=counts.get)}

        left_idx  = [i for i in range(len(X)) if X[i][feat] <= thresh]
        right_idx = [i for i in range(len(X)) if X[i][feat] >  thresh]

        return {
            'leaf':   False,
            'feat':   feat,
            'thresh': thresh,
            'left':   self._build([X[i] for i in left_idx],
                                  [y[i] for i in left_idx], depth + 1),
            'right':  self._build([X[i] for i in right_idx],
                                  [y[i] for i in right_idx], depth + 1),
        }

    def fit(self, X, y):
        self._rng = random.Random(self.random_state)
        self.tree = self._build([list(r) for r in X], list(y), 0)

    def _predict_one(self, node, x):
        if node['leaf']:
            return node['label']
        if x[node['feat']] <= node['thresh']:
            return self._predict_one(node['left'], x)
        return self._predict_one(node['right'], x)

    def predict(self, X):
        return [self._predict_one(self.tree, list(row)) for row in X]


# random Forest

class RandomForest:
    
    def __init__(self, n_estimators=50, random_state=42, max_depth=6):
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.max_depth    = max_depth
        self.trees        = []

    def fit(self, X, y):
        rng    = random.Random(self.random_state)
        X_list = [list(row) for row in X]
        y_list = list(y)
        n      = len(X_list)
        n_feat = len(X_list[0])
        max_features = max(1, int(math.sqrt(n_feat)))

        self.trees = []
        for i in range(self.n_estimators):
            # Bootstrap sample (sample with replacement)
            indices = [rng.randrange(n) for _ in range(n)]
            X_boot  = [X_list[j] for j in indices]
            y_boot  = [y_list[j] for j in indices]

            tree = DecisionTree(
                max_depth=self.max_depth,
                min_samples_split=2,
                max_features=max_features,
                random_state=self.random_state + i,
            )
            tree.fit(X_boot, y_boot)
            self.trees.append(tree)

    def predict(self, X):
        X_list   = [list(row) for row in X]
        all_preds = [tree.predict(X_list) for tree in self.trees]
        result   = []
        for j in range(len(X_list)):
            votes  = [all_preds[t][j] for t in range(len(self.trees))]
            counts = {}
            for v in votes:
                counts[v] = counts.get(v, 0) + 1
            result.append(max(counts, key=counts.get))
        return result


# crime predictor 

class CrimePredictor:
    def __init__(self, city_graph):
        self.graph      = city_graph
        self.clusters   = None
        self.classifier = None
        self.num_police = 10

    def _get_industrial_proximity(self, node):
        
        industrials = [
            n for n in self.graph.graph.nodes()
            if self.graph.graph.nodes[n]['type'] == 'Industrial'
        ]
        if not industrials:
            return self.graph.rows + self.graph.cols

        return min(
            abs(node[0] - ind[0]) + abs(node[1] - ind[1])
            for ind in industrials
        )

    def _encode_location_type(self, node_type):
        type_encoding = {
            'Industrial': 5,
            'Residential': 3,
            'Depot': 2,
            'Power': 2,
            'School': 1,
            'Hospital': 1,
        }
        return type_encoding.get(node_type, 0)

    def cluster_neighborhoods(self):
       # k means clustering
        print("=" * 60)
        print("Challenge 5: Crime Prediction (Part 1 - Clustering)")
        print("=" * 60)

        features, nodes = [], []
        for node in self.graph.graph.nodes():
            if self.graph.graph.nodes[node]['type'] is not None:
                density          = self.graph.graph.nodes[node]['population_density']
                industrial_prox  = self._get_industrial_proximity(node)
                features.append([density, industrial_prox])
                nodes.append(node)

        if len(features) < 3:
            print("[!] Not enough data for clustering")
            return

        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        labels = kmeans.fit_predict(features)

        self.clusters = dict(zip(nodes, labels))

        print(f"[OK] Clustered {len(nodes)} neighborhoods into 3 groups")
        print(f"  Features used: population_density, industrial_proximity")

        cluster_counts = [0, 0, 0]
        for lbl in labels:
            cluster_counts[lbl] += 1
        for i, count in enumerate(cluster_counts):
            print(f"  Cluster {i}: {count} neighborhoods")

        return self.clusters

    def train_classifier(self):
        # random forest
        print("\n" + "=" * 60)
        print("Challenge 5: Crime Prediction (Part 2 - Classification)")
        print("=" * 60)

        if not self.clusters:
            print("[!] No clusters available - run cluster_neighborhoods() first")
            return

        features, labels, nodes = [], [], []

        for node in self.graph.graph.nodes():
            node_type = self.graph.graph.nodes[node]['type']
            if node_type is None:
                continue

            density         = self.graph.graph.nodes[node]['population_density']
            row, col        = node
            industrial_prox = self._get_industrial_proximity(node)
            type_encoded    = self._encode_location_type(node_type)
            cluster_id      = self.clusters.get(node, -1)

            features.append([density, type_encoded, industrial_prox, row, col, cluster_id])

            if node_type == 'Industrial':
                risk = 'High'
            elif node_type == 'Residential' and density > 500 and industrial_prox <= 3:
                risk = 'High'
            elif node_type == 'Residential' and density > 500:
                risk = 'Medium'
            elif node_type == 'Residential' and industrial_prox <= 2:
                risk = 'Medium'
            elif node_type in ['Hospital', 'School']:
                risk = 'Low'
            elif node_type in ['Power', 'Depot']:
                risk = 'Medium'
            else:
                risk = 'Low'

            labels.append(risk)
            nodes.append(node)

        if len(features) < 5:
            print("[!] Not enough data for classification")
            return

        X_train, X_test, y_train, y_test = _train_test_split(
            features, labels, test_size=0.25, random_state=42, stratify=labels
        )

        # training Random Forest 
        self.classifier = RandomForest(
            n_estimators=50, random_state=42, max_depth=6
        )
        self.classifier.fit(X_train, y_train)

        y_pred_test = self.classifier.predict(X_test)
        accuracy    = _accuracy_score(y_test, y_pred_test)

        print(f"[OK] Trained classifier on {len(X_train)} samples, "
              f"tested on {len(X_test)}")
        print(f"  Test accuracy: {accuracy:.2%}")

        self.classifier.fit(features, labels)
        print(f"  Retrained on full dataset ({len(features)} samples) for deployment")

        predictions = self.classifier.predict(features)
        risk_counts = {'Low': 0, 'Medium': 0, 'High': 0}
        for pred in predictions:
            risk_counts[pred] = risk_counts.get(pred, 0) + 1

        print("  Risk distribution:")
        for risk, count in risk_counts.items():
            print(f"    {risk}: {count} areas")

        self._node_predictions = dict(zip(nodes, predictions))
        # updating on basis of risk
    def update_graph_risk(self):
    
        print("\n" + "=" * 60)
        print("Challenge 5: Updating Graph with Risk Scores")
        print("=" * 60)

        if self.classifier is None:
            print("[!] Classifier not trained yet")
            return

        risk_map = {'Low': 0.2, 'Medium': 0.5, 'High': 0.9}

        for node in self.graph.graph.nodes():
            if self.graph.graph.nodes[node]['type'] is None:
                continue

            density         = self.graph.graph.nodes[node]['population_density']
            row, col        = node
            industrial_prox = self._get_industrial_proximity(node)
            type_encoded    = self._encode_location_type(
                self.graph.graph.nodes[node]['type']
            )
            cluster_id      = (self.clusters or {}).get(node, -1)

            risk_label = self.classifier.predict(
                [[density, type_encoded, industrial_prox, row, col, cluster_id]]
            )[0]
            risk_value = risk_map[risk_label]

            self.graph.graph.nodes[node]['risk_index'] = risk_value

        self.graph.update_edge_costs_with_risk()

        print("[OK] Risk scores updated in city graph")
        print("[OK] Edge travel costs updated with risk multiplier")

    def calculate_police_deployments(self):
        print("\n" + "=" * 60)
        print("Challenge 5: Calculating Police Deployment Plan")
        print("=" * 60)

        if not hasattr(self, '_node_predictions') or not self._node_predictions:
            print("[!] No predictions available — train classifier first")
            return []

        risk_nodes = {'High': [], 'Medium': [], 'Low': []}
        for node, risk in self._node_predictions.items():
            risk_nodes[risk].append(node)

        weights = {
            'High':   3 * len(risk_nodes['High']),
            'Medium': 2 * len(risk_nodes['Medium']),
            'Low':    1 * len(risk_nodes['Low']),
        }
        total_weight = sum(weights.values())

        if total_weight == 0:
            print("[!] No neighbourhoods to patrol")
            return []

        allocation = {}
        remaining  = self.num_police
        for risk_level in ['High', 'Medium', 'Low']:
            count = round(self.num_police * weights[risk_level] / total_weight)
            count = min(count, remaining)
            allocation[risk_level] = count
            remaining -= count

        if remaining > 0:
            allocation['High'] += remaining

        print(f"  Police allocation ({self.num_police} officers):")

        deployment_plan = []
        for risk_level in ['High', 'Medium', 'Low']:
            num_officers    = allocation[risk_level]
            available_nodes = risk_nodes[risk_level]
            print(f"    {risk_level} risk: {num_officers} officers "
                  f"-> {len(available_nodes)} areas")

            if available_nodes and num_officers > 0:
                for i in range(num_officers):
                    node = available_nodes[i % len(available_nodes)]
                    deployment_plan.append(node)

        return deployment_plan

    def apply_police_deployment(self, node):
    
        old_risk = self.graph.graph.nodes[node]['risk_index']
        new_risk = old_risk * 0.60
        self.graph.graph.nodes[node]['risk_index'] = new_risk
        self.graph.update_edge_costs_with_risk()
        return old_risk, new_risk


# testing

if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    parent_dir  = os.path.abspath(os.path.join(current_dir, '..'))
    sys.path.append(parent_dir)

    from city_graph import CityGraph
    from challange1_layout import CityLayoutCSP
    from challange2_roads import RoadNetworkBuilder

    graph = CityGraph(10, 10)
    csp   = CityLayoutCSP(graph)
    layout = csp.solve()

    if layout:
        road_builder = RoadNetworkBuilder(graph)
        road_builder.build()

        predictor = CrimePredictor(graph)
        predictor.cluster_neighborhoods()
        predictor.train_classifier()
        predictor.update_graph_risk()
        plan = predictor.calculate_police_deployments()

        print("\n[OK] Crime prediction complete!")

        sample_edges = [(u, v, d) for u, v, d in graph.graph.edges(data=True)
                        if d.get('exists')][:5]
        print("\nSample edge costs (with risk multiplier):")
        for u, v, d in sample_edges:
            print(f"  {u}<->{v}: base={d['base_travel_cost']:.2f}, "
                  f"effective={d['travel_cost']:.2f}")