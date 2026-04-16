"""
EXPERIMENT ENGINE - Controlled Dual-Phase Simulation Framework
Orchestrates baseline and optimized simulations with identical initial conditions.
"""
import numpy as np
import asyncio
from typing import Dict, List, Tuple, Any
import time
from baseline_simulator import BaselineSimulator
from data_logger import DataLogger
from graph_generator import GraphGenerator
from parameter_manager import ParameterManager


class ExperimentEngine:
    """
    Manages controlled experiments comparing baseline vs optimized (PCAN-5G) modes.
    Ensures identical initial conditions for fair comparison.
    """

    def __init__(self, environment, agent, param_manager: ParameterManager = None):
        """
        Initialize experiment engine.

        Args:
            environment: FiveGEnvironment instance
            agent: XDQNAgent instance
            param_manager: ParameterManager for experiment parameters
        """
        self.environment = environment
        self.agent = agent
        self.param_manager = param_manager or ParameterManager()

        self.data_logger = DataLogger()
        self.graph_generator = GraphGenerator()

        # Store seed for reproducibility
        self.random_seed = None

        # Results tracking
        self.experiments_run = []

    def set_random_seed(self, seed: int):
        """Set random seed for reproducible experiments."""
        self.random_seed = seed
        np.random.seed(seed)

    def run_baseline_phase(self, num_steps: int = 100, log_file_prefix: str = 'baseline'):
        """
        Run baseline simulation (no optimization).

        Args:
            num_steps: Number of simulation steps
            log_file_prefix: Prefix for log files

        Returns:
            Dictionary with baseline results and metrics
        """
        print(f"\n{'='*60}")
        print("PHASE 1: BASELINE SIMULATION (NO OPTIMIZATION)")
        print(f"{'='*60}")

        # Create baseline simulator with same topology used in environment
        baseline_sim = BaselineSimulator(
            self.environment.topology,
            self.environment.slices,
            self.environment.positions
        )

        # Create log file for baseline
        log_file = self.data_logger.create_baseline_log(log_file_prefix)
        print(f"Logging to: {log_file}")

        baseline_sim.reset()
        print(f"Running {num_steps} simulation steps...")

        episode_data = {
            'latencies': [],
            'packet_losses': [],
            'throughputs': [],
            'congestions': [],
            'rewards': []
        }

        for step in range(num_steps):
            state, reward, done, metrics = baseline_sim.step()

            # Extract PHY metrics
            phy_metrics = baseline_sim._get_phy_metrics()
            phy_avg = {
                'avg_rsrp': np.mean([m['rsrp'] for m in phy_metrics.values()]),
                'avg_sinr': np.mean([m['sinr'] for m in phy_metrics.values()])
            }

            # Log per-timestep data
            self.data_logger.log_baseline_timestep(step, metrics, phy_avg)

            # Track for episode statistics
            episode_data['latencies'].append(
                np.mean([m['latency'] for m in metrics.values()]))
            episode_data['packet_losses'].append(
                np.mean([m['packet_loss'] for m in metrics.values()]))
            episode_data['throughputs'].append(
                np.mean([m['throughput'] for m in metrics.values()]))
            episode_data['congestions'].append(
                np.mean([m['congestion_level'] for m in metrics.values()]))
            episode_data['rewards'].append(reward)

            if (step + 1) % 20 == 0:
                print(f"  Step {step + 1}/{num_steps} - Latency: {episode_data['latencies'][-1]:.3f}ms, "
                      f"Loss: {episode_data['packet_losses'][-1]:.4f}, Throughput: {episode_data['throughputs'][-1]:.2f} Mbps")

            if done:
                break

        baseline_stats = self.data_logger.get_baseline_stats()
        print(f"\nBaseline Phase Complete:")
        print(f"  Avg Latency: {baseline_stats.get('avg_latency', 0):.3f} ms")
        print(
            f"  Avg Packet Loss: {baseline_stats.get('avg_packet_loss', 0):.4f}")
        print(
            f"  Avg Throughput: {baseline_stats.get('avg_throughput', 0):.2f} Mbps")
        print(
            f"  Avg Congestion: {baseline_stats.get('avg_congestion', 0):.3f}")

        return {
            'phase': 'baseline',
            'stats': baseline_stats,
            'episode_data': episode_data,
            'num_steps': step + 1
        }

    def run_optimized_phase(self, num_steps: int = 100, num_episodes: int = 5,
                            log_file_prefix: str = 'optimized'):
        """
        Run optimized simulation (PCAN-5G with DQN).

        Args:
            num_steps: Steps per episode
            num_episodes: Number of training episodes
            log_file_prefix: Prefix for log files

        Returns:
            Dictionary with optimized results and metrics
        """
        print(f"\n{'='*60}")
        print("PHASE 2: OPTIMIZED SIMULATION (PCAN-5G)")
        print(f"{'='*60}")

        # Create log file for optimized
        log_file = self.data_logger.create_optimized_log(log_file_prefix)
        print(f"Logging to: {log_file}")

        print(
            f"Training {num_episodes} episodes × {num_steps} steps per episode...")

        all_episode_data = {
            'latencies': [],
            'packet_losses': [],
            'throughputs': [],
            'congestions': [],
            'rewards': []
        }

        for episode in range(num_episodes):
            print(f"\nEpisode {episode + 1}/{num_episodes}")

            state = self.environment.reset()
            episode_reward = 0

            for step in range(num_steps):
                # DQN decision
                action = self.agent.act(state)
                next_state, reward, done, metrics = self.environment.step(
                    action)

                # Update prediction module
                import torch
                traffic_data = [self.environment.traffic_load[s]
                                for s in ['eMBB', 'URLLC', 'mMTC']]
                self.agent.update_prediction_module(traffic_data)

                # Get prediction metrics
                prediction_metrics = {}
                if len(self.agent.traffic_history) >= 5:
                    history = np.array(list(self.agent.traffic_history))
                    with torch.no_grad():
                        pred_tensor = self.agent.predictor(
                            torch.FloatTensor(
                                history[-5:]).unsqueeze(0).to(self.agent.device)
                        )
                        prediction = pred_tensor.cpu().numpy().flatten()
                    # Use first slice
                    prediction_metrics['predicted_sinr'] = prediction[0]
                    prediction_metrics['actual_sinr'] = traffic_data[0]
                    prediction_metrics['error'] = abs(prediction_metrics['predicted_sinr'] -
                                                      prediction_metrics['actual_sinr'])

                # Extract PHY metrics
                phy_metrics = self.environment._get_phy_metrics()
                phy_avg = {
                    'avg_rsrp': np.mean([m['rsrp'] for m in phy_metrics.values()]),
                    'avg_sinr': np.mean([m['sinr'] for m in phy_metrics.values()])
                }

                # Log per-timestep data
                self.data_logger.log_optimized_timestep(
                    episode * num_steps + step, metrics, phy_avg, reward, prediction_metrics
                )

                # Remember for learning
                next_state_pred = next_state.copy() if len(
                    self.agent.traffic_history) < 5 else next_state
                self.agent.remember(state, action, reward,
                                    next_state_pred, done)
                self.agent.train()

                # Track for statistics
                all_episode_data['latencies'].append(
                    np.mean([m['latency'] for m in metrics.values()]))
                all_episode_data['packet_losses'].append(
                    np.mean([m['packet_loss'] for m in metrics.values()]))
                all_episode_data['throughputs'].append(
                    np.mean([m['throughput'] for m in metrics.values()]))
                all_episode_data['congestions'].append(
                    np.mean([m['congestion_level'] for m in metrics.values()]))
                all_episode_data['rewards'].append(reward)

                episode_reward += reward
                state = next_state

                if done:
                    break

            self.agent.update_target_model()

            print(f"  Episode Reward: {episode_reward:.3f}")
            print(
                f"  Avg Latency: {np.mean(all_episode_data['latencies'][-num_steps:]):.3f} ms")
            print(f"  Epsilon: {self.agent.epsilon:.3f}")

        self.data_logger.flush()
        optimized_stats = self.data_logger.get_optimized_stats()

        print(f"\nOptimized Phase Complete:")
        print(f"  Avg Latency: {optimized_stats.get('avg_latency', 0):.3f} ms")
        print(
            f"  Avg Packet Loss: {optimized_stats.get('avg_packet_loss', 0):.4f}")
        print(
            f"  Avg Throughput: {optimized_stats.get('avg_throughput', 0):.2f} Mbps")
        print(
            f"  Avg Congestion: {optimized_stats.get('avg_congestion', 0):.3f}")
        print(
            f"  Avg DQN Reward: {optimized_stats.get('avg_dqn_reward', 0):.3f}")

        return {
            'phase': 'optimized',
            'stats': optimized_stats,
            'episode_data': all_episode_data,
            'num_steps': len(all_episode_data['latencies'])
        }

    def run_complete_experiment(self, num_steps: int = 100, optimized_episodes: int = 5,
                                scenario: str = 'default'):
        """
        Run complete dual-phase experiment with comparison.

        Args:
            num_steps: Steps for each phase
            optimized_episodes: Episodes for optimized phase
            scenario: Scenario name for naming and grouping

        Returns:
            Dictionary with complete experiment results
        """
        print(f"\n{'='*80}")
        print(f"CONTROLLED EXPERIMENT: {scenario.upper()}")
        print(f"{'='*80}")

        experiment_start = time.time()

        # Phase 1: Baseline
        baseline_results = self.run_baseline_phase(
            num_steps=num_steps,
            log_file_prefix=scenario
        )

        # Phase 2: Optimized
        optimized_results = self.run_optimized_phase(
            num_steps=num_steps,
            num_episodes=optimized_episodes,
            log_file_prefix=scenario
        )

        # Generate comparison
        comparison_data = self.data_logger.generate_comparison_table()

        # Generate all graphs
        self.graph_generator.generate_all_graphs(
            baseline_results['episode_data'],
            optimized_results['episode_data'],
            comparison_data,
            scenario
        )

        # Print comparison summary
        print(f"\n{'='*80}")
        print("EXPERIMENT COMPARISON SUMMARY")
        print(f"{'='*80}")
        print(
            f"\n{'Metric':<20} {'Baseline':<15} {'PCAN-5G':<15} {'Improvement':<15}")
        print("-" * 65)

        if 'baseline_stats' in comparison_data and 'optimized_stats' in comparison_data:
            baseline_st = comparison_data['baseline_stats']
            optimized_st = comparison_data['optimized_stats']

            print(f"{'Latency (ms)':<20} {baseline_st.get('avg_latency', 0):>13.3f}ms {optimized_st.get('avg_latency', 0):>13.3f}ms "
                  f"{comparison_data.get('latency_improvement_percent', 0):>13.1f}%")
            print(f"{'Packet Loss':<20} {baseline_st.get('avg_packet_loss', 0):>13.4f} {optimized_st.get('avg_packet_loss', 0):>13.4f} "
                  f"{comparison_data.get('packet_loss_improvement_percent', 0):>13.1f}%")
            print(f"{'Throughput (Mbps)':<20} {baseline_st.get('avg_throughput', 0):>13.2f} {optimized_st.get('avg_throughput', 0):>13.2f} "
                  f"{comparison_data.get('throughput_improvement_percent', 0):>13.1f}%")
            print(f"{'Congestion Level':<20} {baseline_st.get('avg_congestion', 0):>13.3f} {optimized_st.get('avg_congestion', 0):>13.3f} "
                  f"{comparison_data.get('congestion_improvement_percent', 0):>13.1f}%")

        experiment_time = time.time() - experiment_start
        print(f"\n{'='*80}")
        print(f"Experiment completed in {experiment_time/60:.2f} minutes")
        print(f"Graphs saved to: {self.graph_generator.output_dir}")
        print(f"{'='*80}\n")

        return {
            'scenario': scenario,
            'baseline': baseline_results,
            'optimized': optimized_results,
            'comparison': comparison_data,
            'duration_seconds': experiment_time
        }

    def run_multi_scenario_experiment(self, scenarios: List[str] = None):
        """
        Run multiple scenarios (low/medium/high traffic) with automated experiments.

        Args:
            scenarios: List of scenario names or None for default

        Returns:
            Dictionary with results for all scenarios
        """
        if scenarios is None:
            scenarios = ['low_traffic', 'medium_traffic', 'high_congestion']

        all_results = {}

        for scenario in scenarios:
            print(f"\n\n{'#'*80}")
            print(f"# SCENARIO: {scenario.upper()}")
            print(f"{'#'*80}")

            # Set parameters for scenario
            if 'low' in scenario:
                self.param_manager.set_traffic_scenario('low')
                num_steps = 100
            elif 'high' in scenario or 'congestion' in scenario:
                self.param_manager.set_traffic_scenario('high')
                num_steps = 150
            else:
                self.param_manager.set_traffic_scenario('medium')
                num_steps = 100

            print(f"Parameters: {self.param_manager.get_current_params()}\n")

            # Run experiment
            result = self.run_complete_experiment(
                num_steps=num_steps,
                optimized_episodes=3,
                scenario=scenario
            )

            all_results[scenario] = result

        return all_results
