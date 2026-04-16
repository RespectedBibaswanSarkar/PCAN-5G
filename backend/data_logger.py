"""
DATA LOGGER - Comprehensive Logging System
Logs per-timestep metrics for both baseline and optimized modes.
"""
import csv
import os
from datetime import datetime
from typing import Dict, List, Any
import numpy as np


class DataLogger:
    """
    Logs simulation metrics to CSV files for post-analysis.
    Tracks latency, packet loss, throughput, SINR/RSRP, congestion, routing, and rewards.
    """

    def __init__(self, log_dir: str = './logs'):
        """
        Initialize data logger.

        Args:
            log_dir: Directory to store log files
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

        # CSV files for each mode
        self.baseline_file = None
        self.optimized_file = None
        self.baseline_writer = None
        self.optimized_writer = None

        # Metrics accumulation for statistics
        self.metrics_baseline = []
        self.metrics_optimized = []

    def create_baseline_log(self, experiment_name: str = 'baseline'):
        """Create and initialize baseline mode log file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(
            self.log_dir, f'{experiment_name}_baseline_{timestamp}.csv')

        self.baseline_file = open(filename, 'w', newline='')
        self.baseline_writer = csv.DictWriter(self.baseline_file, fieldnames=[
            'timestep',
            'slice_name',
            'latency_ms',
            'packet_loss_fraction',
            'throughput_mbps',
            'congestion_level',
            'queue_length',
            'allocated_bw',
            'traffic_load',
            'avg_rsrp',
            'avg_sinr',
            'phy_factor'
        ])
        self.baseline_writer.writeheader()
        return filename

    def create_optimized_log(self, experiment_name: str = 'optimized'):
        """Create and initialize optimized mode log file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(
            self.log_dir, f'{experiment_name}_optimized_{timestamp}.csv')

        self.optimized_file = open(filename, 'w', newline='')
        self.optimized_writer = csv.DictWriter(self.optimized_file, fieldnames=[
            'timestep',
            'slice_name',
            'latency_ms',
            'packet_loss_fraction',
            'throughput_mbps',
            'congestion_level',
            'queue_length',
            'allocated_bw',
            'traffic_load',
            'avg_rsrp',
            'avg_sinr',
            'phy_factor',
            'dqn_reward',
            'predicted_sinr',
            'actual_sinr',
            'prediction_error'
        ])
        self.optimized_writer.writeheader()
        return filename

    def log_baseline_timestep(self, timestep: int, metrics: Dict[str, Dict],
                              phy_metrics: Dict = None):
        """
        Log one timestep of baseline mode metrics.

        Args:
            timestep: Current simulation step
            metrics: Dictionary of metrics for each slice
            phy_metrics: Physical layer metrics (RSRP, SINR)
        """
        if self.baseline_writer is None:
            return

        if phy_metrics is None:
            phy_metrics = {}

        for slice_name, slice_metrics in metrics.items():
            row = {
                'timestep': timestep,
                'slice_name': slice_name,
                'latency_ms': round(slice_metrics.get('latency', 0), 3),
                'packet_loss_fraction': round(slice_metrics.get('packet_loss', 0), 4),
                'throughput_mbps': round(slice_metrics.get('throughput', 0), 2),
                'congestion_level': round(slice_metrics.get('congestion_level', 0), 3),
                'queue_length': slice_metrics.get('queue_length', 0),
                'allocated_bw': round(slice_metrics.get('allocated_bw', 0), 2),
                'traffic_load': slice_metrics.get('traffic_load', 0),
                'avg_rsrp': round(phy_metrics.get('avg_rsrp', 0), 2),
                'avg_sinr': round(phy_metrics.get('avg_sinr', 0), 2),
                'phy_factor': round(slice_metrics.get('phy_factor', 0), 3)
            }
            self.baseline_writer.writerow(row)
            self.metrics_baseline.append(row)

    def log_optimized_timestep(self, timestep: int, metrics: Dict[str, Dict],
                               phy_metrics: Dict = None, dqn_reward: float = 0,
                               prediction_metrics: Dict = None):
        """
        Log one timestep of optimized mode metrics.

        Args:
            timestep: Current simulation step
            metrics: Dictionary of metrics for each slice
            phy_metrics: Physical layer metrics (RSRP, SINR)
            dqn_reward: Current DQN reward value
            prediction_metrics: Dict with predicted_sinr, actual_sinr, error
        """
        if self.optimized_writer is None:
            return

        if phy_metrics is None:
            phy_metrics = {}
        if prediction_metrics is None:
            prediction_metrics = {}

        for slice_name, slice_metrics in metrics.items():
            row = {
                'timestep': timestep,
                'slice_name': slice_name,
                'latency_ms': round(slice_metrics.get('latency', 0), 3),
                'packet_loss_fraction': round(slice_metrics.get('packet_loss', 0), 4),
                'throughput_mbps': round(slice_metrics.get('throughput', 0), 2),
                'congestion_level': round(slice_metrics.get('congestion_level', 0), 3),
                'queue_length': slice_metrics.get('queue_length', 0),
                'allocated_bw': round(slice_metrics.get('allocated_bw', 0), 2),
                'traffic_load': slice_metrics.get('traffic_load', 0),
                'avg_rsrp': round(phy_metrics.get('avg_rsrp', 0), 2),
                'avg_sinr': round(phy_metrics.get('avg_sinr', 0), 2),
                'phy_factor': round(slice_metrics.get('phy_factor', 0), 3),
                'dqn_reward': round(dqn_reward, 4),
                'predicted_sinr': round(prediction_metrics.get('predicted_sinr', 0), 2),
                'actual_sinr': round(prediction_metrics.get('actual_sinr', 0), 2),
                'prediction_error': round(prediction_metrics.get('error', 0), 3)
            }
            self.optimized_writer.writerow(row)
            self.metrics_optimized.append(row)

    def flush(self):
        """Flush buffers to disk."""
        if self.baseline_file:
            self.baseline_file.flush()
        if self.optimized_file:
            self.optimized_file.flush()

    def close(self):
        """Close all log files."""
        if self.baseline_file:
            self.baseline_file.close()
        if self.optimized_file:
            self.optimized_file.close()

    def get_baseline_stats(self):
        """Get aggregated baseline statistics."""
        if not self.metrics_baseline:
            return {}

        df_data = self.metrics_baseline
        return {
            'avg_latency': np.mean([d['latency_ms'] for d in df_data]),
            'max_latency': np.max([d['latency_ms'] for d in df_data]),
            'min_latency': np.min([d['latency_ms'] for d in df_data]),
            'avg_packet_loss': np.mean([d['packet_loss_fraction'] for d in df_data]),
            'avg_throughput': np.mean([d['throughput_mbps'] for d in df_data]),
            'avg_congestion': np.mean([d['congestion_level'] for d in df_data]),
            'total_logs': len(df_data)
        }

    def get_optimized_stats(self):
        """Get aggregated optimized statistics."""
        if not self.metrics_optimized:
            return {}

        df_data = self.metrics_optimized
        return {
            'avg_latency': np.mean([d['latency_ms'] for d in df_data]),
            'max_latency': np.max([d['latency_ms'] for d in df_data]),
            'min_latency': np.min([d['latency_ms'] for d in df_data]),
            'avg_packet_loss': np.mean([d['packet_loss_fraction'] for d in df_data]),
            'avg_throughput': np.mean([d['throughput_mbps'] for d in df_data]),
            'avg_congestion': np.mean([d['congestion_level'] for d in df_data]),
            'avg_dqn_reward': np.mean([d['dqn_reward'] for d in df_data]),
            'avg_prediction_error': np.mean([d['prediction_error'] for d in df_data]),
            'total_logs': len(df_data)
        }

    def generate_comparison_table(self):
        """
        Generate comparison table for IEEE paper.
        Returns: Dictionary with improvement percentages
        """
        baseline_stats = self.get_baseline_stats()
        optimized_stats = self.get_optimized_stats()

        if not baseline_stats or not optimized_stats:
            return {}

        # Calculate improvements (negative is better for latency/loss)
        latency_improvement = ((baseline_stats['avg_latency'] - optimized_stats['avg_latency'])
                               / baseline_stats['avg_latency'] * 100) if baseline_stats['avg_latency'] > 0 else 0

        loss_improvement = ((baseline_stats['avg_packet_loss'] - optimized_stats['avg_packet_loss'])
                            / (baseline_stats['avg_packet_loss'] + 1e-6) * 100) if baseline_stats['avg_packet_loss'] > 0 else 0

        throughput_improvement = ((optimized_stats['avg_throughput'] - baseline_stats['avg_throughput'])
                                  / baseline_stats['avg_throughput'] * 100) if baseline_stats['avg_throughput'] > 0 else 0

        congestion_improvement = ((baseline_stats['avg_congestion'] - optimized_stats['avg_congestion'])
                                  / baseline_stats['avg_congestion'] * 100) if baseline_stats['avg_congestion'] > 0 else 0

        return {
            'latency_improvement_percent': round(latency_improvement, 2),
            'packet_loss_improvement_percent': round(loss_improvement, 2),
            'throughput_improvement_percent': round(throughput_improvement, 2),
            'congestion_improvement_percent': round(congestion_improvement, 2),
            'baseline_stats': baseline_stats,
            'optimized_stats': optimized_stats
        }
