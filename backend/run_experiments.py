"""
5G CROSS-LAYER DQN SIMULATION - RESEARCH-GRADE EXPERIMENTAL PLATFORM
Upgraded Version 2.0 with Baseline vs PCAN-5G Comparison

This script demonstrates how to use the new experimental framework
for controlled dual-phase experiments with IEEE-standard graph generation.
"""

import numpy as np
from parameter_manager import ParameterManager
from experiment_engine import ExperimentEngine
from agent import XDQNAgent
from environment import FiveGEnvironment
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def print_header(text):
    """Print a formatted header."""
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")


def main():
    """Main entry point for experimental framework."""

    print_header("5G X-DQN PCAN-5G RESEARCH PLATFORM - EXPERIMENTAL FRAMEWORK")

    print("Initializing components...")

    # Initialize environment and agent
    env = FiveGEnvironment()
    state_dim = 21
    action_dim = 9
    agent = XDQNAgent(state_dim, action_dim)

    # Initialize parameter manager
    param_manager = ParameterManager()

    # Initialize experiment engine
    experiment_engine = ExperimentEngine(env, agent, param_manager)

    print(
        f"✓ Environment: {len(env.topology.nodes)} nodes, {len(env.topology.edges)} links")
    print(f"✓ Agent: DQN with LSTM predictor")
    print(f"✓ Parameter Manager: Ready for control")
    print(f"✓ Experiment Engine: Ready to run dual-phase experiments\n")

    # ========================================================================
    # EXAMPLE 1: SINGLE EXPERIMENT
    # ========================================================================
    print_header("EXAMPLE 1: SINGLE CONTROLLED EXPERIMENT")

    print("Running single experiment: BASELINE_MEDIUM scenario")
    print("Configuration:")
    print("  - Traffic Scenario: Medium")
    print("  - Simulation Steps: 100 per phase")
    print("  - Optimized Episodes: 3\n")

    result = experiment_engine.run_complete_experiment(
        num_steps=100,
        optimized_episodes=3,
        scenario="single_experiment"
    )

    print(f"\nExperiment completed. Results saved.")
    print(f"Comparison data:")
    comparison = result.get('comparison', {})
    print(
        f"  Latency improvement: {comparison.get('latency_improvement_percent', 0):.1f}%")
    print(
        f"  Packet loss improvement: {comparison.get('packet_loss_improvement_percent', 0):.1f}%")
    print(
        f"  Throughput improvement: {comparison.get('throughput_improvement_percent', 0):.1f}%")

    # ========================================================================
    # EXAMPLE 2: MULTI-SCENARIO EXPERIMENT
    # ========================================================================
    print_header("EXAMPLE 2: MULTI-SCENARIO AUTOMATED EXPERIMENTS")

    print("Running automatic experiments for three traffic scenarios:")
    print("  1. Low Traffic (50-100 Mbps)")
    print("  2. Medium Traffic (100-200 Mbps)")
    print("  3. High Congestion (200-300 Mbps)\n")

    results = experiment_engine.run_multi_scenario_experiment(
        scenarios=['low_traffic', 'medium_traffic', 'high_congestion']
    )

    print("\n" + "="*80)
    print("MULTI-SCENARIO SUMMARY")
    print("="*80)

    for scenario, result in results.items():
        comparison = result.get('comparison', {})
        baseline_stats = comparison.get('baseline_stats', {})
        optimized_stats = comparison.get('optimized_stats', {})

        print(f"\n{scenario.upper()}")
        print(f"  Baseline - Latency: {baseline_stats.get('avg_latency', 0):.2f}ms, "
              f"Loss: {baseline_stats.get('avg_packet_loss', 0):.4f}, "
              f"Throughput: {baseline_stats.get('avg_throughput', 0):.2f} Mbps")
        print(f"  Optimized - Latency: {optimized_stats.get('avg_latency', 0):.2f}ms, "
              f"Loss: {optimized_stats.get('avg_packet_loss', 0):.4f}, "
              f"Throughput: {optimized_stats.get('avg_throughput', 0):.2f} Mbps")
        print(
            f"  Improvement: {comparison.get('latency_improvement_percent', 0):.1f}% latency reduction")

    # ========================================================================
    # EXAMPLE 3: PARAMETER CONTROL
    # ========================================================================
    print_header("EXAMPLE 3: MANUAL PARAMETER CONTROL")

    print("Current default parameters:")
    current_params = param_manager.get_current_params()
    print(f"  Traffic Scenario: {current_params['traffic_scenario']}")
    print(f"  Traffic Range: {current_params['traffic_range']} Mbps")
    print(
        f"  Node Density: {current_params['node_density']} ({current_params['node_count']} nodes)")
    print(
        f"  Packet Rate: {current_params['packet_rate']} ({current_params['packet_rate_pps']} packets/sec)")
    print(f"  Thresholds:")
    for key, val in current_params['thresholds'].items():
        print(f"    - {key}: {val}")

    print("\nChanging parameters to 'high' traffic scenario...")
    param_manager.set_traffic_scenario('high')
    param_manager.set_congestion_threshold(0.7)
    param_manager.set_link_failure_probability(0.01)

    print("Updated parameters:")
    updated_params = param_manager.get_current_params()
    print(f"  Traffic Scenario: {updated_params['traffic_scenario']}")
    print(f"  Traffic Range: {updated_params['traffic_range']} Mbps")
    print(
        f"  Congestion Threshold: {updated_params['thresholds']['congestion_max']}")
    print(
        f"  Link Failure Probability: {updated_params['link_failure_probability']}")

    # ========================================================================
    # EXAMPLE 4: PREDICTIONS AND CONVERGENCE
    # ========================================================================
    print_header("EXAMPLE 4: DQN CONVERGENCE ANALYSIS")

    print("Running 10-episode DQN training to show convergence...")
    state = env.reset()
    episode_rewards = []

    for ep in range(10):
        total_reward = 0
        for step in range(50):  # Shorter episodes for demo
            action = agent.act(state)
            next_state, reward, done, metrics = env.step(action)

            traffic_data = [metrics[s]['throughput']
                            for s in ['eMBB', 'URLLC', 'mMTC']]
            agent.update_prediction_module(traffic_data)

            agent.remember(state, action, reward, next_state, done)
            agent.train()

            total_reward += reward
            state = next_state

            if done:
                break

        agent.update_target_model()
        episode_rewards.append(total_reward)

        if (ep + 1) % 2 == 0:
            avg_reward = np.mean(episode_rewards[-2:])
            print(
                f"Episode {ep+1:2d} | Reward: {total_reward:7.3f} | Epsilon: {agent.epsilon:.3f}")

    print(
        f"\nReward Trend: {np.mean(episode_rewards[:5]):.2f} → {np.mean(episode_rewards[-5:]):.2f}")
    print(
        f"Convergence: {'✓ IMPROVING' if episode_rewards[-1] > episode_rewards[0] else '⚠ NEEDS MORE TRAINING'}")

    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    print_header("EXPERIMENTAL FRAMEWORK SUMMARY")

    print("The platform supports:")
    print("  ✓ Baseline Mode: Static routing, no optimization (traditional 5G)")
    print("  ✓ Optimized Mode: DQN-based PCAN-5G with LSTM prediction")
    print("  ✓ Fair Comparison: Both modes run with identical initial conditions")
    print("  ✓ Data Logging: Per-timestep logs (baseline_logs.csv, optimized_logs.csv)")
    print("  ✓ Graph Generation: IEEE-standard publication-quality graphs (PNG, PDF)")
    print("  ✓ Parameter Control: User-controlled traffic, thresholds, and failure rates")
    print("  ✓ Multi-Scenario: Automated experiments for multiple traffic patterns")

    print("\nGenerated Output Files:")
    print("  Logs:")
    print("    - ./logs/baseline_*.csv")
    print("    - ./logs/optimized_*.csv")
    print("  Graphs (IEEE-format, 300 DPI):")
    print("    - ./graphs/latency_comparison_*.{png,pdf}")
    print("    - ./graphs/packet_loss_comparison_*.{png,pdf}")
    print("    - ./graphs/throughput_comparison_*.{png,pdf}")
    print("    - ./graphs/congestion_comparison_*.{png,pdf}")
    print("    - ./graphs/reward_convergence_*.{png,pdf}")
    print("    - ./graphs/improvement_summary_*.{png,pdf}")
    print("    - ./graphs/metrics_comparison_bars_*.{png,pdf}")

    print("\nNext Steps:")
    print("  1. Start the FastAPI server: python main.py")
    print("  2. Access API & interactive docs: http://localhost:8000/docs")
    print("  3. Run experiments via REST API or command line")
    print("  4. Generate publication-ready graphs for IEEE paper")
    print("  5. Compare baseline vs PCAN-5G performance metrics")

    print("\n" + "="*80)
    print("Experimental framework ready for research!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
