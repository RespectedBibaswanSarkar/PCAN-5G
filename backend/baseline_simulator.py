"""
BASELINE SIMULATOR - No Optimization, Static Routing
This represents traditional 5G network behavior without any AI optimization.
"""
import numpy as np
import networkx as nx
from typing import Dict, List, Tuple
import random


class BaselineSimulator:
    """
    Simulates 5G network with static routing and no optimization.
    Uses shortest-path routing and fixed bandwidth allocation.
    """

    def __init__(self, topology, slices, positions):
        """
        Initialize baseline simulator with network topology.

        Args:
            topology: NetworkX DiGraph representation of the network
            slices: Dictionary of slice configurations
            positions: Dictionary of node positions
        """
        self.topology = topology.copy()
        self.slices = slices
        self.positions = positions
        self.step_count = 0

        # Static allocation: fixed proportional distribution
        self.slice_bw_alloc = {
            s: slices[s]['min_bw'] * 2  # Fixed at 2x minimum
            for s in slices
        }

        # Initialize state
        self.queue_lengths = {node: 0 for node in self.topology.nodes}
        self.traffic_load = {s: random.randint(50, 200) for s in self.slices}
        self.link_degradation = {edge: 1.0 for edge in self.topology.edges}

        # Metrics tracking
        self.all_latencies = []
        self.all_packet_losses = []
        self.all_throughputs = []
        self.all_congestion = []

    def reset(self):
        """Reset simulator to initial state."""
        self.step_count = 0
        self.queue_lengths = {node: 0 for node in self.topology.nodes}
        self.traffic_load = {s: random.randint(50, 200) for s in self.slices}
        self.all_latencies = []
        self.all_packet_losses = []
        self.all_throughputs = []
        self.all_congestion = []
        return self._get_state()

    def _get_phy_metrics(self) -> Dict:
        """
        Calculate PHY layer metrics (RSRP, SINR) for all links.
        Same as in FiveGEnvironment for consistency.
        """
        metrics = {}
        for edge in self.topology.edges:
            u, v = edge
            dist = np.sqrt((self.positions[u][0] - self.positions[v][0])**2 +
                           (self.positions[u][1] - self.positions[v][1])**2)
            rsrp = 30 - 10 * np.log10(dist + 1) - random.uniform(0, 5)
            sinr = rsrp - (-90) - random.uniform(5, 15)
            metrics[edge] = {
                'rsrp': rsrp,
                'sinr': sinr,
                # Normalized link quality
                'link_quality': max(0.1, min(1.0, (sinr + 10) / 30))
            }
        return metrics

    def _shortest_path_route(self, src, dst):
        """
        Calculate shortest path between source and destination.
        Always uses hop-count as metric (no optimization).
        """
        try:
            path = nx.shortest_path(self.topology, src, dst, weight=None)
            return path
        except nx.NetworkXNoPath:
            return None

    def _get_state(self):
        """
        Get current network state.
        Simplified compared to optimized version (no predictions).
        """
        phy = self._get_phy_metrics()
        avg_rsrp = np.mean([m['rsrp'] for m in phy.values()])
        avg_sinr = np.mean([m['sinr'] for m in phy.values()])

        state = [
            avg_rsrp, avg_sinr,
            *self.slice_bw_alloc.values(),
            *list(self.queue_lengths.values()),
            *self.traffic_load.values()
        ]
        return np.array(state, dtype=np.float32)

    def step(self):
        """
        Execute one simulation step with static baseline routing.
        No action input - everything is predetermined.

        Returns:
            state, reward (always 0 for baseline), done, detailed_metrics
        """
        # Update traffic: slower than optimized (more realistic baseline)
        if self.step_count % 25 == 0 and self.step_count > 0:
            target_slice = random.choice(list(self.slices.keys()))
            for s in self.slices:
                self.traffic_load[s] = 200 if s == target_slice else 75
        else:
            for s in self.slices:
                self.traffic_load[s] = max(
                    50, self.traffic_load[s] + random.randint(-10, 10))

        # Simulate traffic with static routing (NO OPTIMIZATION)
        metrics = self._simulate_traffic_baseline()

        # Calculate baseline reward (just average latency for tracking)
        avg_latency = np.mean([m['latency'] for m in metrics.values()])
        reward = -avg_latency / 100.0  # Negative reward indicates lack of optimization

        self.step_count += 1
        done = self.step_count >= 100

        return self._get_state(), float(reward), done, metrics

    def _simulate_traffic_baseline(self):
        """
        Simulate traffic flow with static routing.
        No dynamic resource allocation or congestion control.
        """
        phy_metrics = self._get_phy_metrics()

        results = {}
        for s_name, s_info in self.slices.items():
            load = self.traffic_load[s_name]
            alloc = self.slice_bw_alloc[s_name]

            # PHY factor: affected by SINR
            phy_factor = np.mean([m['link_quality']
                                 for m in phy_metrics.values()])
            eff_capacity = alloc * phy_factor

            # Static routing penalty: add inherent latency overhead
            routing_overhead = 1.5  # No optimization = higher overhead

            if eff_capacity > load:
                # Under-capacity: queue-based latency
                latency = routing_overhead * \
                    (1 + (load / (eff_capacity + 1e-6)))
                packet_loss = 0.01  # Minimal baseline loss
            else:
                # Over-capacity: packet dropping
                latency = routing_overhead * 50  # Heavy penalty
                packet_loss = (load - eff_capacity) / load

            # Congestion level (queue depth)
            congestion = min(1.0, load / (alloc + 1e-6))

            results[s_name] = {
                'latency': latency * 10,              # ms
                'packet_loss': packet_loss,          # fraction
                'throughput': min(load, eff_capacity),  # Mbps
                'congestion_level': congestion,      # 0-1
                'queue_length': int(congestion * 100),  # packets
                'slice_name': s_name,
                'allocated_bw': alloc,
                'traffic_load': load,
                'phy_factor': phy_factor
            }

            # Track for statistics
            self.all_latencies.append(results[s_name]['latency'])
            self.all_packet_losses.append(packet_loss)
            self.all_throughputs.append(results[s_name]['throughput'])
            self.all_congestion.append(congestion)

        return results

    def run_episode(self, num_steps=100):
        """
        Run complete episode and collect metrics.

        Returns:
            Dictionary with aggregated metrics from the episode
        """
        episode_data = {
            'latencies': [],
            'packet_losses': [],
            'throughputs': [],
            'congestions': [],
            'rewards': [],
            'phy_metrics': []
        }

        self.reset()
        for _ in range(num_steps):
            state, reward, done, metrics = self.step()

            # Log detailed metrics
            episode_data['latencies'].append(
                np.mean([m['latency'] for m in metrics.values()]))
            episode_data['packet_losses'].append(
                np.mean([m['packet_loss'] for m in metrics.values()]))
            episode_data['throughputs'].append(
                np.mean([m['throughput'] for m in metrics.values()]))
            episode_data['congestions'].append(
                np.mean([m['congestion_level'] for m in metrics.values()]))
            episode_data['rewards'].append(reward)

            phy = self._get_phy_metrics()
            episode_data['phy_metrics'].append({
                'avg_rsrp': np.mean([m['rsrp'] for m in phy.values()]),
                'avg_sinr': np.mean([m['sinr'] for m in phy.values()])
            })

            if done:
                break

        # Compute summary statistics
        results = {
            'avg_latency': np.mean(episode_data['latencies']),
            'max_latency': np.max(episode_data['latencies']),
            'avg_packet_loss': np.mean(episode_data['packet_losses']),
            'avg_throughput': np.mean(episode_data['throughputs']),
            'avg_congestion': np.mean(episode_data['congestions']),
            'episode_data': episode_data
        }

        return results
