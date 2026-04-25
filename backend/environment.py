import numpy as np
import networkx as nx
import random
from typing import Dict, List, Tuple, Optional


class FiveGEnvironment:
    """
    Simulates a 5G C-RAN (Cloud Radio Access Network) environment.
    Jointly handles PHY, Network, and Resource layers.

    Supports two simulation modes:
        - 'ideal': Original logical network behavior (default, backward-compatible)
        - 'realistic_rf': Physical signal layer with hardware abstraction
    """

    def __init__(self, simulation_mode: str = 'ideal'):
        """
        Initialize the 5G environment.

        Args:
            simulation_mode: 'ideal' (original behavior) or 'realistic_rf' (RF hardware layer)
        """
        self.simulation_mode = simulation_mode
        self.topology = self._create_cran_topology()
        self.slices = {
            'eMBB': {'id': 0, 'min_bw': 100, 'priority': 1, 'target_latency': 10},
            'URLLC': {'id': 1, 'min_bw': 10, 'priority': 3, 'target_latency': 1},
            'mMTC': {'id': 2, 'min_bw': 1, 'priority': 2, 'target_latency': 50}
        }

        # Hardware layer (initialized only in realistic_rf mode)
        self.waveguides = {}
        self.node_pipelines = {}
        self._rf_metrics_cache = {}

        if self.simulation_mode == 'realistic_rf':
            self._init_hardware_layer()

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

    def _get_node_type(self, node_id: int) -> str:
        """Get the type of a node by its ID."""
        if node_id == 0:
            return 'CU'
        elif node_id < 3:
            return 'DU'
        elif node_id < 6:
            return 'RRH'
        else:
            return 'UE'

    # ─────────────────────────────────────────────
    # Hardware Layer Initialization (RF mode only)
    # ─────────────────────────────────────────────

    def _init_hardware_layer(self):
        """Initialize waveguide links and node signal pipelines for RF mode."""
        from hardware.waveguide import create_waveguide_from_edge
        from hardware.signal_pipeline import create_pipeline_for_node

        # Create waveguide for every edge
        for u, v in self.topology.edges():
            src_type = self._get_node_type(u)
            tgt_type = self._get_node_type(v)
            wg = create_waveguide_from_edge(
                source=u, target=v,
                positions=self.positions,
                source_type=src_type,
                target_type=tgt_type,
                scale_km=0.5,
            )
            self.waveguides[(u, v)] = wg

        # Create signal pipeline for every node
        for node_id in self.topology.nodes():
            node_type = self._get_node_type(node_id)
            self.node_pipelines[node_id] = create_pipeline_for_node(node_id, node_type)

    def set_simulation_mode(self, mode: str):
        """
        Switch simulation mode at runtime.

        Args:
            mode: 'ideal' or 'realistic_rf'
        """
        if mode not in ('ideal', 'realistic_rf'):
            raise ValueError(f"Invalid simulation mode: {mode}. Use 'ideal' or 'realistic_rf'.")

        if mode == self.simulation_mode:
            return

        self.simulation_mode = mode

        if mode == 'realistic_rf' and not self.waveguides:
            self._init_hardware_layer()

    # ─────────────────────────────────────────────
    # Core Environment Methods (preserved, extended)
    # ─────────────────────────────────────────────

    def reset(self):
        self.step_count = 0
        self.slice_bw_alloc = {
            s: self.slices[s]['min_bw'] for s in self.slices}
        self.queue_lengths = {node: 0 for node in self.topology.nodes}
        self.traffic_load = {s: random.randint(50, 200) for s in self.slices}
        self.link_degradation = {edge: 1.0 for edge in self.topology.edges}
        self._rf_metrics_cache = {}

        # Reset oscillator counters in RF mode
        if self.simulation_mode == 'realistic_rf':
            for pipeline in self.node_pipelines.values():
                pipeline.oscillator.reset_counter()

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

    def _get_rf_metrics(self) -> Dict:
        """
        Compute RF signal metrics for all links and nodes (realistic_rf mode only).
        Propagates signals through waveguides and node pipelines.

        Returns:
            Dictionary with per-link and per-node RF metrics.
        """
        if self.simulation_mode != 'realistic_rf':
            return {}

        from hardware.signal_model import Signal

        link_metrics = {}
        node_metrics = {}

        # Get base PHY metrics to seed signals
        phy = self._get_phy_metrics()

        for (u, v), wg in self.waveguides.items():
            # Create input signal from PHY metrics
            phy_data = phy.get((u, v), {'rsrp': 20.0, 'sinr': 15.0})
            input_signal = Signal.from_phy_metrics(
                rsrp=phy_data['rsrp'],
                sinr=phy_data['sinr'],
            )

            # Dynamic interference injection
            interference_spike = random.uniform(0, 0.05)
            wg.set_interference(wg.interference_factor + interference_spike)

            # Propagate through waveguide
            propagated = wg.propagate(input_signal)

            # Process through destination node pipeline
            dst_pipeline = self.node_pipelines.get(v)
            if dst_pipeline:
                # Inject node-local noise
                noise_injection = random.uniform(0.0001, 0.001)
                propagated = dst_pipeline.inject_noise(propagated, noise_injection)

                # Run through pipeline
                output = dst_pipeline.process(propagated)
            else:
                output = propagated

            link_metrics[(u, v)] = {
                'input_snr': round(input_signal.snr, 2),
                'output_snr': round(output.snr, 2),
                'input_amplitude': round(input_signal.amplitude, 4),
                'output_amplitude': round(output.amplitude, 4),
                'attenuation_db': round(wg.get_total_attenuation_db(), 2),
                'interference': round(wg.interference_factor, 3),
                'propagation_delay_ms': round(wg.propagation_delay_ms, 4),
                'link_quality': round(wg.get_quality_score(), 3),
                'noise': round(output.noise, 6),
            }

            # Reset interference spike (keep only base)
            wg.set_interference(max(0, wg.interference_factor - interference_spike))

        # Collect per-node pipeline metrics
        for node_id, pipeline in self.node_pipelines.items():
            node_metrics[node_id] = pipeline.get_current_signal_quality()
            node_metrics[node_id]['node_type'] = pipeline.node_type
            node_metrics[node_id]['regeneration_count'] = pipeline.oscillator.total_regenerations

        self._rf_metrics_cache = {
            'links': link_metrics,
            'nodes': node_metrics,
        }
        return self._rf_metrics_cache

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

        # Extend state with RF features in realistic_rf mode
        if self.simulation_mode == 'realistic_rf':
            rf = self._get_rf_metrics()
            link_data = rf.get('links', {})

            if link_data:
                avg_link_snr = np.mean([m['output_snr'] for m in link_data.values()])
                avg_interference = np.mean([m['interference'] for m in link_data.values()])
                avg_link_quality = np.mean([m['link_quality'] for m in link_data.values()])
                avg_noise = np.mean([m['noise'] for m in link_data.values()])
                min_snr = min(m['output_snr'] for m in link_data.values())
                max_interference = max(m['interference'] for m in link_data.values())
                regen_count = sum(
                    1 for n in rf.get('nodes', {}).values()
                    if n.get('regenerated', False)
                )
            else:
                avg_link_snr = 0.0
                avg_interference = 0.0
                avg_link_quality = 0.5
                avg_noise = 0.001
                min_snr = 0.0
                max_interference = 0.0
                regen_count = 0

            state.extend([
                avg_link_snr,
                avg_interference,
                avg_link_quality,
                avg_noise * 1000,  # Scale up for NN input
                min_snr,
                max_interference,
                float(regen_count),
            ])

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

        # RF mode: get signal quality and apply to effective capacity
        rf_factor = 1.0
        rf_data = {}
        if self.simulation_mode == 'realistic_rf':
            rf = self._get_rf_metrics()
            link_data = rf.get('links', {})
            if link_data:
                avg_snr = np.mean([m['output_snr'] for m in link_data.values()])
                avg_quality = np.mean([m['link_quality'] for m in link_data.values()])
                avg_interference = np.mean([m['interference'] for m in link_data.values()])

                # RF factor: SNR-based capacity modifier (Shannon-inspired)
                rf_factor = max(0.1, min(1.5, avg_snr / 25.0)) * avg_quality
                rf_factor *= (1.0 - avg_interference * 0.5)  # Interference penalty

                rf_data = {
                    'avg_snr': round(avg_snr, 2),
                    'avg_quality': round(avg_quality, 3),
                    'avg_interference': round(avg_interference, 3),
                    'rf_factor': round(rf_factor, 3),
                }

        results = {}
        for s_name, s_info in self.slices.items():
            load = self.traffic_load[s_name]
            alloc = self.slice_bw_alloc[s_name]

            if self.simulation_mode == 'realistic_rf':
                # RF mode: capacity affected by both PHY and RF signal quality
                eff_capacity = alloc * max(0.1, phy_factor) * rf_factor
            else:
                # Ideal mode: original behavior
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

            # Add RF-specific metrics when in RF mode
            if self.simulation_mode == 'realistic_rf' and rf_data:
                results[s_name]['rf_factor'] = rf_data['rf_factor']
                results[s_name]['avg_snr'] = rf_data['avg_snr']
                results[s_name]['avg_interference'] = rf_data['avg_interference']

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

        # RF mode: add signal quality reward component
        if self.simulation_mode == 'realistic_rf' and self._rf_metrics_cache:
            link_data = self._rf_metrics_cache.get('links', {})
            if link_data:
                avg_snr = np.mean([m['output_snr'] for m in link_data.values()])
                snr_bonus = max(-2.0, min(2.0, (avg_snr - 10) / 10))
                interference_penalty = np.mean(
                    [m['interference'] for m in link_data.values()]
                ) * 3.0
                reward += snr_bonus - interference_penalty

        return float(reward)

    # ─────────────────────────────────────────────
    # RF Routing Cost (new, realistic_rf mode only)
    # ─────────────────────────────────────────────

    def compute_routing_cost(self, u: int, v: int) -> float:
        """
        Compute the routing cost for a link considering signal quality.

        Routing Cost = f(latency, congestion, SNR, interference)

        Only used in realistic_rf mode. In ideal mode, returns base latency.

        Args:
            u: Source node ID
            v: Target node ID

        Returns:
            Routing cost (lower is better)
        """
        base_cost = self.topology[u][v].get('lat', 1)

        if self.simulation_mode != 'realistic_rf':
            return float(base_cost)

        # Congestion factor
        congestion = self.queue_lengths.get(v, 0) / 100.0

        # RF factors
        wg = self.waveguides.get((u, v))
        if wg:
            interference = wg.interference_factor
            link_quality = wg.get_quality_score()
        else:
            interference = 0.0
            link_quality = 0.5

        # Signal quality from cache
        link_data = self._rf_metrics_cache.get('links', {}).get((u, v), {})
        link_snr = link_data.get('output_snr', 15.0)
        snr_penalty = max(0.0, (15 - link_snr) / 15)

        cost = base_cost * (1.0 + congestion + snr_penalty + interference * 2.0)
        cost /= max(0.1, link_quality)

        return float(cost)

    def get_snr_threshold_violations(self, threshold_db: float = 5.0) -> List[tuple]:
        """
        Get list of links where SNR falls below threshold.
        Used for adaptive rerouting decisions.

        Args:
            threshold_db: Minimum acceptable SNR in dB

        Returns:
            List of (source, target) tuples where SNR is below threshold
        """
        violations = []
        link_data = self._rf_metrics_cache.get('links', {})
        for (u, v), metrics in link_data.items():
            if metrics.get('output_snr', 100) < threshold_db:
                violations.append((u, v))
        return violations

    def get_interference_spikes(self, threshold: float = 0.7) -> List[tuple]:
        """
        Get list of links experiencing interference spikes.

        Args:
            threshold: Interference level considered a spike (0–1)

        Returns:
            List of (source, target) tuples with high interference
        """
        spikes = []
        link_data = self._rf_metrics_cache.get('links', {})
        for (u, v), metrics in link_data.items():
            if metrics.get('interference', 0) > threshold:
                spikes.append((u, v))
        return spikes

    # ─────────────────────────────────────────────
    # State dimension helper
    # ─────────────────────────────────────────────

    def get_state_dim(self) -> int:
        """
        Get the state vector dimensionality for current mode.
        Note: This returns the RAW env state dimension.
        main.py concatenates 3 LSTM prediction values on top of this.
        """
        # Base: 2 PHY + 3 slice_bw + 10 queue + 3 traffic = 18
        base_dim = 18
        if self.simulation_mode == 'realistic_rf':
            return base_dim + 7  # + 7 RF features = 25
        return base_dim  # 18
