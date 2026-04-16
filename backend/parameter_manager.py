"""
PARAMETER MANAGER - User Control Interface
Allows manual control of traffic patterns, node density, packet rates, and thresholds.
"""
from typing import Dict, Any
import numpy as np


class ParameterManager:
    """
    Manages simulation parameters that can be controlled by users.
    Ensures parameters are applied equally to both baseline and optimized modes.
    """

    # Default parameter ranges
    DEFAULT_TRAFFIC_LOAD = {
        'low': (50, 100),
        'medium': (100, 200),
        'high': (200, 300)
    }

    DEFAULT_NODE_DENSITY = {
        'sparse': 6,
        'normal': 10,
        'dense': 15
    }

    DEFAULT_PACKET_RATES = {
        'low': 10,     # packets/sec
        'medium': 50,
        'high': 100
    }

    DEFAULT_THRESHOLDS = {
        'sinr_min': -5,        # dB
        'rsrp_min': -100,      # dBm
        'congestion_max': 0.8,  # 0-1
        'latency_max': 50       # ms
    }

    def __init__(self):
        """Initialize parameter manager with default values."""
        # Current active parameters
        self.traffic_scenario = 'medium'
        self.node_density = 'normal'
        self.packet_rate = 'medium'
        self.sinr_threshold = self.DEFAULT_THRESHOLDS['sinr_min']
        self.rsrp_threshold = self.DEFAULT_THRESHOLDS['rsrp_min']
        self.congestion_threshold = self.DEFAULT_THRESHOLDS['congestion_max']
        self.latency_threshold = self.DEFAULT_THRESHOLDS['latency_max']

        # Failure probability (network faults)
        self.link_failure_probability = 0.0
        self.node_failure_probability = 0.0

    def set_traffic_scenario(self, scenario: str):
        """
        Set traffic load scenario.

        Args:
            scenario: 'low', 'medium', or 'high'
        """
        if scenario not in self.DEFAULT_TRAFFIC_LOAD:
            raise ValueError(f"Invalid traffic scenario: {scenario}")
        self.traffic_scenario = scenario

    def set_node_density(self, density: str):
        """
        Set network node density.

        Args:
            density: 'sparse', 'normal', or 'dense'
        """
        if density not in self.DEFAULT_NODE_DENSITY:
            raise ValueError(f"Invalid node density: {density}")
        self.node_density = density

    def set_packet_rate(self, rate: str):
        """
        Set packet transmission rate.

        Args:
            rate: 'low', 'medium', or 'high'
        """
        if rate not in self.DEFAULT_PACKET_RATES:
            raise ValueError(f"Invalid packet rate: {rate}")
        self.packet_rate = rate

    def set_sinr_threshold(self, value: float):
        """Set SINR minimum threshold in dB."""
        self.sinr_threshold = float(value)

    def set_rsrp_threshold(self, value: float):
        """Set RSRP minimum threshold in dBm."""
        self.rsrp_threshold = float(value)

    def set_congestion_threshold(self, value: float):
        """Set maximum congestion level (0-1)."""
        if not 0 <= value <= 1:
            raise ValueError("Congestion threshold must be between 0 and 1")
        self.congestion_threshold = float(value)

    def set_latency_threshold(self, value: float):
        """Set maximum acceptable latency in ms."""
        if value <= 0:
            raise ValueError("Latency threshold must be positive")
        self.latency_threshold = float(value)

    def set_failure_probability(self, link_prob: float = None, node_prob: float = None):
        """
        Set network failure probabilities.

        Args:
            link_prob: Probability of link failure (0-1)
            node_prob: Probability of node failure (0-1)
        """
        if link_prob is not None:
            if not 0 <= link_prob <= 1:
                raise ValueError(
                    "Link failure probability must be between 0 and 1")
            self.link_failure_probability = float(link_prob)

        if node_prob is not None:
            if not 0 <= node_prob <= 1:
                raise ValueError(
                    "Node failure probability must be between 0 and 1")
            self.node_failure_probability = float(node_prob)

    def get_traffic_range(self):
        """Get current traffic load range."""
        return self.DEFAULT_TRAFFIC_LOAD[self.traffic_scenario]

    def get_node_count(self):
        """Get number of nodes for current density."""
        return self.DEFAULT_NODE_DENSITY[self.node_density]

    def get_packet_rate(self):
        """Get current packet rate (packets/sec)."""
        return self.DEFAULT_PACKET_RATES[self.packet_rate]

    def get_all_thresholds(self):
        """Get all active threshold values."""
        return {
            'sinr_min': self.sinr_threshold,
            'rsrp_min': self.rsrp_threshold,
            'congestion_max': self.congestion_threshold,
            'latency_max': self.latency_threshold
        }

    def get_current_params(self):
        """Get all current parameter settings."""
        return {
            'traffic_scenario': self.traffic_scenario,
            'traffic_range': self.get_traffic_range(),
            'node_density': self.node_density,
            'node_count': self.get_node_count(),
            'packet_rate': self.packet_rate,
            'packet_rate_pps': self.get_packet_rate(),
            'thresholds': self.get_all_thresholds(),
            'link_failure_probability': self.link_failure_probability,
            'node_failure_probability': self.node_failure_probability
        }

    def apply_to_traffic_load(self, base_load_dict: Dict[str, int]):
        """
        Apply current traffic scenario to traffic load dictionary.

        Args:
            base_load_dict: Dictionary mapping slice names to traffic loads

        Returns:
            Modified traffic load dictionary
        """
        min_load, max_load = self.get_traffic_range()
        modified_load = {}

        for slice_name, _ in base_load_dict.items():
            modified_load[slice_name] = np.random.randint(min_load, max_load)

        return modified_load

    def validate_metrics(self, metrics: Dict[str, Any]) -> Dict[str, bool]:
        """
        Check if metrics violate thresholds.

        Args:
            metrics: Metrics dictionary

        Returns:
            Dictionary of violations
        """
        violations = {
            'sinr_violation': metrics.get('sinr', 0) < self.sinr_threshold,
            'rsrp_violation': metrics.get('rsrp', 0) < self.rsrp_threshold,
            'congestion_violation': metrics.get('congestion', 0) > self.congestion_threshold,
            'latency_violation': metrics.get('latency', 0) > self.latency_threshold
        }
        return violations

    def should_trigger_link_failure(self):
        """Determine if a link failure should occur."""
        return np.random.rand() < self.link_failure_probability

    def should_trigger_node_failure(self):
        """Determine if a node failure should occur."""
        return np.random.rand() < self.node_failure_probability

    def reset_to_defaults(self):
        """Reset all parameters to default values."""
        self.traffic_scenario = 'medium'
        self.node_density = 'normal'
        self.packet_rate = 'medium'
        self.sinr_threshold = self.DEFAULT_THRESHOLDS['sinr_min']
        self.rsrp_threshold = self.DEFAULT_THRESHOLDS['rsrp_min']
        self.congestion_threshold = self.DEFAULT_THRESHOLDS['congestion_max']
        self.latency_threshold = self.DEFAULT_THRESHOLDS['latency_max']
        self.link_failure_probability = 0.0
        self.node_failure_probability = 0.0
