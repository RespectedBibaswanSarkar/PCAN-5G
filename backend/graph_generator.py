"""
GRAPH GENERATOR - IEEE-Standard Publication-Quality Graphs
Generates comparative graphs for Baseline vs PCAN-5G OPTIMIZED mode.
"""
import os
from typing import Dict, List, Tuple
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend


class GraphGenerator:
    """
    Generates IEEE-standard publication-quality graphs.
    All graphs are publication-ready with minimal colors, clear legends, and proper formatting.
    """

    # IEEE publication style settings
    DPI = 300
    FIGURE_SIZE = (10, 6)
    FONT_SIZE = 11
    LEGEND_FONT_SIZE = 10
    LINE_WIDTH = 2
    MARKER_SIZE = 6

    # Publication colors (colorblind-friendly)
    COLOR_BASELINE = '#1f77b4'  # Blue
    COLOR_OPTIMIZED = '#ff7f0e'  # Orange

    def __init__(self, output_dir: str = './graphs'):
        """
        Initialize graph generator.

        Args:
            output_dir: Directory to save graphs
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Set matplotlib parameters for publication
        plt.rcParams.update({
            'font.size': self.FONT_SIZE,
            'font.family': 'serif',
            'axes.labelsize': self.FONT_SIZE,
            'axes.titlesize': self.FONT_SIZE + 1,
            'xtick.labelsize': self.FONT_SIZE - 1,
            'ytick.labelsize': self.FONT_SIZE - 1,
            'legend.fontsize': self.LEGEND_FONT_SIZE,
            'figure.figsize': self.FIGURE_SIZE,
            'axes.grid': True,
            'grid.alpha': 0.3,
            'lines.linewidth': self.LINE_WIDTH,
            'lines.markersize': self.MARKER_SIZE
        })

    def save_figure(self, fig, filename: str, format_list: List[str] = None):
        """
        Save figure in multiple formats (PNG @ 300 DPI and PDF).

        Args:
            fig: Matplotlib figure object
            filename: Base filename without extension
            format_list: List of formats to save ('png', 'pdf')
        """
        if format_list is None:
            format_list = ['png', 'pdf']

        for fmt in format_list:
            if fmt == 'png':
                filepath = os.path.join(self.output_dir, f'{filename}.png')
                fig.savefig(filepath, dpi=self.DPI,
                            bbox_inches='tight', format='png')
            elif fmt == 'pdf':
                filepath = os.path.join(self.output_dir, f'{filename}.pdf')
                fig.savefig(filepath, dpi=self.DPI,
                            bbox_inches='tight', format='pdf')

        plt.close(fig)

    def plot_latency_comparison(self, baseline_data: List[float], optimized_data: List[float],
                                scenario: str = 'default'):
        """
        Plot latency comparison: Baseline vs PCAN-5G.

        Args:
            baseline_data: Latency values (ms) for baseline mode
            optimized_data: Latency values (ms) for optimized mode
            scenario: Scenario name for filename
        """
        fig, ax = plt.subplots(figsize=self.FIGURE_SIZE)

        timesteps = np.arange(len(baseline_data))

        ax.plot(timesteps, baseline_data, color=self.COLOR_BASELINE, label='Baseline',
                linewidth=self.LINE_WIDTH, marker='o', markevery=10, markersize=self.MARKER_SIZE)
        ax.plot(timesteps, optimized_data, color=self.COLOR_OPTIMIZED, label='PCAN-5G',
                linewidth=self.LINE_WIDTH, marker='s', markevery=10, markersize=self.MARKER_SIZE)

        ax.set_xlabel('Time (timesteps)', fontsize=self.FONT_SIZE)
        ax.set_ylabel('Latency (ms)', fontsize=self.FONT_SIZE)
        ax.set_title('Latency Comparison: Baseline vs PCAN-5G Optimized',
                     fontsize=self.FONT_SIZE + 1)
        ax.legend(loc='best', fontsize=self.LEGEND_FONT_SIZE)
        ax.grid(True, alpha=0.3)

        self.save_figure(fig, f'latency_comparison_{scenario}')

    def plot_packet_loss_comparison(self, baseline_data: List[float], optimized_data: List[float],
                                    scenario: str = 'default'):
        """
        Plot packet loss comparison: Baseline vs PCAN-5G.

        Args:
            baseline_data: Packet loss (fraction) for baseline
            optimized_data: Packet loss (fraction) for optimized
            scenario: Scenario name for filename
        """
        fig, ax = plt.subplots(figsize=self.FIGURE_SIZE)

        timesteps = np.arange(len(baseline_data))

        # Convert to percentage for better readability
        baseline_pct = [x * 100 for x in baseline_data]
        optimized_pct = [x * 100 for x in optimized_data]

        ax.plot(timesteps, baseline_pct, color=self.COLOR_BASELINE, label='Baseline',
                linewidth=self.LINE_WIDTH, marker='o', markevery=10, markersize=self.MARKER_SIZE)
        ax.plot(timesteps, optimized_pct, color=self.COLOR_OPTIMIZED, label='PCAN-5G',
                linewidth=self.LINE_WIDTH, marker='s', markevery=10, markersize=self.MARKER_SIZE)

        ax.set_xlabel('Time (timesteps)', fontsize=self.FONT_SIZE)
        ax.set_ylabel('Packet Loss (%)', fontsize=self.FONT_SIZE)
        ax.set_title('Packet Loss Comparison: Baseline vs PCAN-5G Optimized',
                     fontsize=self.FONT_SIZE + 1)
        ax.legend(loc='best', fontsize=self.LEGEND_FONT_SIZE)
        ax.grid(True, alpha=0.3)

        self.save_figure(fig, f'packet_loss_comparison_{scenario}')

    def plot_throughput_comparison(self, baseline_data: List[float], optimized_data: List[float],
                                   scenario: str = 'default'):
        """
        Plot throughput comparison: Baseline vs PCAN-5G.

        Args:
            baseline_data: Throughput (Mbps) for baseline
            optimized_data: Throughput (Mbps) for optimized
            scenario: Scenario name for filename
        """
        fig, ax = plt.subplots(figsize=self.FIGURE_SIZE)

        timesteps = np.arange(len(baseline_data))

        ax.plot(timesteps, baseline_data, color=self.COLOR_BASELINE, label='Baseline',
                linewidth=self.LINE_WIDTH, marker='o', markevery=10, markersize=self.MARKER_SIZE)
        ax.plot(timesteps, optimized_data, color=self.COLOR_OPTIMIZED, label='PCAN-5G',
                linewidth=self.LINE_WIDTH, marker='s', markevery=10, markersize=self.MARKER_SIZE)

        ax.set_xlabel('Time (timesteps)', fontsize=self.FONT_SIZE)
        ax.set_ylabel('Throughput (Mbps)', fontsize=self.FONT_SIZE)
        ax.set_title('Throughput Comparison: Baseline vs PCAN-5G Optimized',
                     fontsize=self.FONT_SIZE + 1)
        ax.legend(loc='best', fontsize=self.LEGEND_FONT_SIZE)
        ax.grid(True, alpha=0.3)

        self.save_figure(fig, f'throughput_comparison_{scenario}')

    def plot_congestion_comparison(self, baseline_data: List[float], optimized_data: List[float],
                                   scenario: str = 'default'):
        """
        Plot network congestion comparison.

        Args:
            baseline_data: Congestion level (0-1) for baseline
            optimized_data: Congestion level (0-1) for optimized
            scenario: Scenario name for filename
        """
        fig, ax = plt.subplots(figsize=self.FIGURE_SIZE)

        timesteps = np.arange(len(baseline_data))

        ax.plot(timesteps, baseline_data, color=self.COLOR_BASELINE, label='Baseline',
                linewidth=self.LINE_WIDTH, marker='o', markevery=10, markersize=self.MARKER_SIZE)
        ax.plot(timesteps, optimized_data, color=self.COLOR_OPTIMIZED, label='PCAN-5G',
                linewidth=self.LINE_WIDTH, marker='s', markevery=10, markersize=self.MARKER_SIZE)

        ax.set_xlabel('Time (timesteps)', fontsize=self.FONT_SIZE)
        ax.set_ylabel('Congestion Level', fontsize=self.FONT_SIZE)
        ax.set_title('Network Congestion Comparison: Baseline vs PCAN-5G Optimized',
                     fontsize=self.FONT_SIZE + 1)
        ax.legend(loc='best', fontsize=self.LEGEND_FONT_SIZE)
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 1.0])

        self.save_figure(fig, f'congestion_comparison_{scenario}')

    def plot_reward_convergence(self, dqn_rewards: List[float], scenario: str = 'default'):
        """
        Plot DQN reward convergence (optimized mode only).

        Args:
            dqn_rewards: DQN rewards over time
            scenario: Scenario name for filename
        """
        fig, ax = plt.subplots(figsize=self.FIGURE_SIZE)

        timesteps = np.arange(len(dqn_rewards))

        # Calculate moving average for smoother curve
        window = max(1, len(dqn_rewards) // 10)
        moving_avg = np.convolve(
            dqn_rewards, np.ones(window)/window, mode='valid')
        moving_avg_time = np.arange(window-1, len(dqn_rewards))

        ax.plot(timesteps, dqn_rewards, color=self.COLOR_OPTIMIZED, alpha=0.5,
                linewidth=self.LINE_WIDTH - 1, label='DQN Reward (per step)')
        ax.plot(moving_avg_time, moving_avg, color=self.COLOR_OPTIMIZED,
                linewidth=self.LINE_WIDTH + 1, label=f'Moving Average (window={window})')

        ax.set_xlabel('Time (timesteps)', fontsize=self.FONT_SIZE)
        ax.set_ylabel('DQN Reward', fontsize=self.FONT_SIZE)
        ax.set_title('DQN Reward Convergence (PCAN-5G Optimized Mode)',
                     fontsize=self.FONT_SIZE + 1)
        ax.legend(loc='best', fontsize=self.LEGEND_FONT_SIZE)
        ax.grid(True, alpha=0.3)

        self.save_figure(fig, f'reward_convergence_{scenario}')

    def plot_prediction_accuracy(self, predicted_sinr: List[float], actual_sinr: List[float],
                                 scenario: str = 'default'):
        """
        Plot LSTM prediction accuracy: Predicted vs Actual SINR.

        Args:
            predicted_sinr: Predicted SINR values
            actual_sinr: Actual SINR values
            scenario: Scenario name for filename
        """
        fig, ax = plt.subplots(figsize=self.FIGURE_SIZE)

        timesteps = np.arange(len(predicted_sinr))

        ax.plot(timesteps, predicted_sinr, color=self.COLOR_OPTIMIZED, label='Predicted SINR',
                linewidth=self.LINE_WIDTH, marker='o', markevery=10, markersize=self.MARKER_SIZE)
        ax.plot(timesteps, actual_sinr, color=self.COLOR_BASELINE, label='Actual SINR',
                linewidth=self.LINE_WIDTH, marker='s', markevery=10, markersize=self.MARKER_SIZE)

        ax.set_xlabel('Time (timesteps)', fontsize=self.FONT_SIZE)
        ax.set_ylabel('SINR (dB)', fontsize=self.FONT_SIZE)
        ax.set_title('LSTM Prediction Accuracy: Predicted vs Actual SINR',
                     fontsize=self.FONT_SIZE + 1)
        ax.legend(loc='best', fontsize=self.LEGEND_FONT_SIZE)
        ax.grid(True, alpha=0.3)

        self.save_figure(fig, f'prediction_accuracy_{scenario}')

    def plot_comparison_bar_chart(self, baseline_stats: Dict, optimized_stats: Dict,
                                  scenario: str = 'default'):
        """
        Plot comparison bar chart for multiple metrics.

        Args:
            baseline_stats: Dictionary of baseline metrics
            optimized_stats: Dictionary of optimized metrics
            scenario: Scenario name for filename
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        metrics = ['avg_latency', 'avg_packet_loss',
                   'avg_throughput', 'avg_congestion']
        baseline_vals = [baseline_stats.get(m, 0) for m in metrics]
        optimized_vals = [optimized_stats.get(m, 0) for m in metrics]

        x = np.arange(len(metrics))
        width = 0.35

        bars1 = ax.bar(x - width/2, baseline_vals, width, label='Baseline',
                       color=self.COLOR_BASELINE, alpha=0.8)
        bars2 = ax.bar(x + width/2, optimized_vals, width, label='PCAN-5G',
                       color=self.COLOR_OPTIMIZED, alpha=0.8)

        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.2f}', ha='center', va='bottom', fontsize=9)

        ax.set_xlabel('Metrics', fontsize=self.FONT_SIZE)
        ax.set_ylabel('Value', fontsize=self.FONT_SIZE)
        ax.set_title('Performance Metrics Comparison: Baseline vs PCAN-5G',
                     fontsize=self.FONT_SIZE + 1)
        ax.set_xticks(x)
        ax.set_xticklabels(['Avg Latency', 'Avg Packet Loss', 'Avg Throughput', 'Avg Congestion'],
                           rotation=15, ha='right')
        ax.legend(fontsize=self.LEGEND_FONT_SIZE)
        ax.grid(True, alpha=0.3, axis='y')

        self.save_figure(fig, f'metrics_comparison_bars_{scenario}')

    def plot_improvement_summary(self, comparison_data: Dict, scenario: str = 'default'):
        """
        Plot improvement percentages compared to baseline.

        Args:
            comparison_data: Dictionary with improvement percentages
            scenario: Scenario name for filename
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        metrics = ['latency_improvement_percent', 'packet_loss_improvement_percent',
                   'throughput_improvement_percent', 'congestion_improvement_percent']
        metric_labels = ['Latency\nReduction', 'Packet Loss\nReduction',
                         'Throughput\nIncrease', 'Congestion\nReduction']
        values = [comparison_data.get(m, 0) for m in metrics]

        # Color: green for improvements, red for degradation
        colors = ['green' if v > 0 else 'red' for v in values]

        bars = ax.bar(metric_labels, values, color=colors, alpha=0.7)

        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, values)):
            ax.text(bar.get_x() + bar.get_width()/2., val,
                    f'{val:+.1f}%', ha='center', va='bottom' if val > 0 else 'top',
                    fontsize=11, fontweight='bold')

        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax.set_ylabel('Improvement (%)', fontsize=self.FONT_SIZE)
        ax.set_title('PCAN-5G Performance Improvement vs Baseline',
                     fontsize=self.FONT_SIZE + 1)
        ax.grid(True, alpha=0.3, axis='y')

        self.save_figure(fig, f'improvement_summary_{scenario}')

    def generate_all_graphs(self, baseline_episode_data: Dict, optimized_episode_data: Dict,
                            comparison_data: Dict, scenario: str = 'default'):
        """
        Generate all comparison graphs at once.

        Args:
            baseline_episode_data: Baseline episode data dictionary
            optimized_episode_data: Optimized episode data dictionary
            comparison_data: Comparison statistics and improvements
            scenario: Scenario name for grouping
        """
        print(f"Generating graphs for scenario: {scenario}...")

        # Extract data from episode dictionaries
        baseline_latencies = baseline_episode_data.get('latencies', [])
        baseline_losses = baseline_episode_data.get('packet_losses', [])
        baseline_throughputs = baseline_episode_data.get('throughputs', [])
        baseline_congestions = baseline_episode_data.get('congestions', [])

        optimized_latencies = optimized_episode_data.get('latencies', [])
        optimized_losses = optimized_episode_data.get('packet_losses', [])
        optimized_throughputs = optimized_episode_data.get('throughputs', [])
        optimized_congestions = optimized_episode_data.get('congestions', [])
        optimized_rewards = optimized_episode_data.get('rewards', [])

        # Generate comparison graphs
        if baseline_latencies and optimized_latencies:
            self.plot_latency_comparison(
                baseline_latencies, optimized_latencies, scenario)
            print(
                f"  ✓ Latency comparison: {len(baseline_latencies)} timesteps")

        if baseline_losses and optimized_losses:
            self.plot_packet_loss_comparison(
                baseline_losses, optimized_losses, scenario)
            print(f"  ✓ Packet loss comparison")

        if baseline_throughputs and optimized_throughputs:
            self.plot_throughput_comparison(
                baseline_throughputs, optimized_throughputs, scenario)
            print(f"  ✓ Throughput comparison")

        if baseline_congestions and optimized_congestions:
            self.plot_congestion_comparison(
                baseline_congestions, optimized_congestions, scenario)
            print(f"  ✓ Congestion comparison")

        if optimized_rewards:
            self.plot_reward_convergence(optimized_rewards, scenario)
            print(f"  ✓ Reward convergence")

        # Bar chart comparison
        baseline_stats = comparison_data.get('baseline_stats', {})
        optimized_stats = comparison_data.get('optimized_stats', {})
        if baseline_stats and optimized_stats:
            self.plot_comparison_bar_chart(
                baseline_stats, optimized_stats, scenario)
            print(f"  ✓ Metrics comparison bars")

        # Improvement summary
        self.plot_improvement_summary(comparison_data, scenario)
        print(f"  ✓ Improvement summary")

        print(f"All graphs saved to: {self.output_dir}\n")
