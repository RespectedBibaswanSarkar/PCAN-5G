import numpy as np
import networkx as nx
import random
from typing import Dict, List, Tuple


class FiveGEnvironment:
    """
    Simulates a 5G C-RAN (Cloud Radio Access Network) environment.
    Jointly handles PHY, Network, and Resource layers.
    """

    def __init__(self):
        self.topology = self._create_cran_topology()
        self.slices = {
            'eMBB': {'id': 0, 'min_bw': 100, 'priority': 1, 'target_latency': 10},
            'URLLC': {'id': 1, 'min_bw': 10, 'priority': 3, 'target_latency': 1},
            'mMTC': {'id': 2, 'min_bw': 1, 'priority': 2, 'target_latency': 50}
        }
        self.reset()

    def _create_cran_topology(self):
        G = nx.DiGraph()
        # Node 0: CU (Core)
        # Nodes 1-2: DUs
        # Nodes 3-5: RRHs (gNodeBs)
        # Nodes 6-9: UE Hotspots

        edges = [
            (0, 1, {'cap': 1000, 'lat': 1}),  # CU to DU1
            (0, 2, {'cap': 1000, 'lat': 1}),  # CU to DU2
            (1, 3, {'cap': 500, 'lat': 2}),  # DU1 to RRH1
            (1, 4, {'cap': 500, 'lat': 2}),  # DU1 to RRH2
            (2, 5, {'cap': 500, 'lat': 2}),  # DU2 to RRH3
            # Wireless Access Links
            (3, 6, {'cap': 200, 'lat': 5}),
            (3, 7, {'cap': 200, 'lat': 5}),
            (4, 7, {'cap': 200, 'lat': 5}),
            (5, 8, {'cap': 200, 'lat': 5}),
            (5, 9, {'cap': 200, 'lat': 5}),
        ]
        for u, v, d in edges:
            G.add_edge(u, v, **d)
            G.add_edge(v, u, **d)

        self.positions = {
            0: (0, 0), 1: (-2, 2), 2: (2, 2),
            3: (-4, 4), 4: (-2, 4), 5: (4, 4),
            6: (-5, 6), 7: (-3, 6), 8: (3, 6), 9: (5, 6)
        }
        return G

    def reset(self):
        self.step_count = 0
        self.slice_bw_alloc = {
            s: self.slices[s]['min_bw'] for s in self.slices}
        self.queue_lengths = {node: 0 for node in self.topology.nodes}
        self.traffic_load = {s: random.randint(50, 200) for s in self.slices}
        self.link_degradation = {edge: 1.0 for edge in self.topology.edges}
        return self._get_state()

    def _get_phy_metrics(self) -> Dict:
        metrics = {}
        for edge in self.topology.edges:
            u, v = edge
            dist = np.sqrt((self.positions[u][0] - self.positions[v][0])**2 +
                           (self.positions[u][1] - self.positions[v][1])**2)
            rsrp = 30 - 10 * np.log10(dist + 1) - random.uniform(0, 5)
            sinr = rsrp - (-90) - random.uniform(5, 15)
            metrics[edge] = {'rsrp': rsrp, 'sinr': sinr}
        return metrics

    def _get_state(self):
        phy = self._get_phy_metrics()
        avg_rsrp = np.mean([m['rsrp'] for m in phy.values()])
        avg_sinr = np.mean([m['sinr'] for m in phy.values()])

        state = [
            avg_rsrp, avg_sinr,
            *self.slice_bw_alloc.values(),
            *self.queue_lengths.values(),
            *self.traffic_load.values()
        ]
        return np.array(state, dtype=np.float32)

    def step(self, action_idx: int):
        routing_action = action_idx // 3
        bw_action = (action_idx % 3) - 1

        for s in self.slices:
            self.slice_bw_alloc[s] = max(self.slices[s]['min_bw'],
                                         self.slice_bw_alloc[s] + bw_action * 10)

        metrics = self._simulate_traffic()
        reward = self._calculate_reward(metrics)
        self.step_count += 1
        done = self.step_count >= 100
        return self._get_state(), reward, done, metrics

    def _simulate_traffic(self):
        """Simulate traffic flow and compute per-slice metrics."""
        # Handle "Task Switching" - Explicit detection scenario
        if self.step_count % 30 == 0 and self.step_count > 0:
            target_slice = random.choice(list(self.slices.keys()))
            for s in self.slices:
                self.traffic_load[s] = 250 if s == target_slice else 50
        else:
            for s in self.slices:
                self.traffic_load[s] = max(
                    50, self.traffic_load[s] + random.randint(-15, 15))

        # Get physical metrics
        phy_metrics = self._get_phy_metrics()
        phy_factor = np.mean([m['sinr'] for m in phy_metrics.values()]) / 20.0
        avg_phy = {
            'avg_rsrp': np.mean([m['rsrp'] for m in phy_metrics.values()]),
            'avg_sinr': np.mean([m['sinr'] for m in phy_metrics.values()]),
            'phy_factor': max(0.1, phy_factor)
        }

        results = {}
        for s_name, s_info in self.slices.items():
            load = self.traffic_load[s_name]
            alloc = self.slice_bw_alloc[s_name]
            eff_capacity = alloc * max(0.1, phy_factor)

            if eff_capacity > load:
                latency = 1 / (eff_capacity - load + 1e-6)
                packet_loss = 0.01
            else:
                latency = 50
                packet_loss = (load - eff_capacity) / load

            # Congestion level (0-1)
            congestion_level = min(1.0, load / (alloc + 1e-6))
            queue_length = int(congestion_level * 100)

            results[s_name] = {
                'latency': latency * 10,
                'packet_loss': min(1.0, packet_loss),
                'throughput': min(load, eff_capacity),
                'congestion_level': congestion_level,
                'queue_length': queue_length,
                'satisfaction': min(1.0, eff_capacity / load),
                'allocated_bw': alloc,
                'traffic_load': load,
                'phy_factor': avg_phy['phy_factor'],
                'slice_name': s_name
            }

        # Store PHY metrics for logging
        self._last_phy_metrics = avg_phy

        return results

    def _calculate_reward(self, metrics):
        t_reward = sum(m['throughput'] for m in metrics.values()) / 500
        l_penalty = sum(m['latency'] for m in metrics.values()) / 100
        p_penalty = sum(m['packet_loss'] for m in metrics.values()) * 10
        satisfactions = [m['satisfaction'] for m in metrics.values()]
        fairness = 1.0 - np.std(satisfactions)
        reward = (2.0 * t_reward) - (1.0 * l_penalty) - \
            (5.0 * p_penalty) + (3.0 * fairness)
        return float(reward)
