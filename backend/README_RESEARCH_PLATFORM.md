# 5G Cross-Layer DQN PCAN-5G Research Platform v2.0

## Overview

This is a **research-grade experimental platform** for simulating 5G networks with cross-layer optimization using Deep Reinforcement Learning (DQN). The system implements a **BASELINE vs OPTIMIZED comparison framework** designed for IEEE research paper publication.

## Key Features

### ✓ Dual-Phase Simulation Framework

- **Phase 1 - BASELINE MODE**: Traditional 5G network behavior without any optimization
  - Static shortest-path routing
  - Fixed bandwidth allocation
  - No predictive congestion control
  - No dynamic resource allocation
  
- **Phase 2 - OPTIMIZED MODE (PCAN-5G)**: AI-based cross-layer optimization
  - DQN-based intelligent routing decisions
  - LSTM-based congestion prediction
  - Dynamic resource allocation
  - Cross-layer optimization

### ✓ High-Fidelity RF Mode (Digital Twin)

- **Physical Signal Model**: Realistic frequency, amplitude, and phase tracking.
- **Hardware Abstraction**: Per-node signal pipelines (Filters, Amplifiers, Oscillators).
- **Physical Propagation**: Waveguide-level simulation of distance-based attenuation and interference.

### ✓ Research Documentation Layer

- **Academic Alignment**: Fully mapped to foundational papers (SDN, 5G, RL, GNN).
- **Theoretical Foundations**: Deep-dives into established networking literature.
- **Operational Lifecycle**: Process-flow linking every backend step to research concepts.

### ✓ Controlled Experiment Engine

- **Identical Initial Conditions**: Both phases run on the same topology, traffic patterns, and node configuration
- **Fair Comparison**: Ensures all differences in results come from optimization decisions, not from setup changes
- **Sequential or Parallel Execution**: Can run phases separately or in controlled sequence
- **Multi-Scenario Support**: Automated experiments for low/medium/high traffic scenarios

### ✓ Comprehensive Data Logging

**Per-timestep logging includes:**
- **Performance Metrics**: Latency (ms), Packet loss (fraction), Throughput (Mbps)
- **Physical Layer**: SINR (dB), RSRP (dBm), Link quality
- **Network State**: Congestion level, Queue lengths, Traffic load
- **Optimization Metrics** (Optimized mode only):
  - DQN rewards
  - LSTM prediction accuracy
  - Predicted vs Actual SINR

**Output Format**: CSV files for easy post-processing and analysis
- `baseline_logs_*.csv`: Baseline mode detailed metrics
- `optimized_logs_*.csv`: Optimized mode detailed metrics

### ✓ IEEE-Standard Publication Graphs

**Automatic graph generation** (300 DPI, PNG + PDF formats):

1. **Latency Comparison** - Baseline vs PCAN-5G over time
2. **Packet Loss Comparison** - Shows improvement in reliability
3. **Throughput Comparison** - Network capacity utilization
4. **Network Congestion Comparison** - Queue depth reduction
5. **DQN Reward Convergence** - Training progress (optimized only)
6. **Prediction Accuracy** - Actual vs Predicted SINR (optimized only)
7. **Metrics Bar Chart** - Side-by-side comparison of key metrics
8. **Improvement Summary** - Percentage improvements in all metrics

**Publication Quality:**
- Minimal, colorblind-friendly colors (Blue/Orange)
- Clear legends and axis labels
- Serif fonts (IEEE standard)
- Grid lines for readability
- Proper figure sizes and DPI

### ✓ Manual Parameter Control

Users can adjust experiment conditions equally for both modes:

**Traffic Control:**
- Low traffic (50-100 Mbps)
- Medium traffic (100-200 Mbps)
- High congestion (200-300 Mbps)

**Network Topology:**
- Node density: Sparse, Normal, Dense
- Packet rates: Low, Medium, High

**Quality of Service Thresholds:**
- SINR minimum threshold (dB)
- RSRP minimum threshold (dBm)
- Maximum congestion level (0-1)
- Maximum acceptable latency (ms)

**Network Faults:**
- Link failure probability
- Node failure probability

### ✓ Automated Experiment Pipeline

Run complete experiment suites with one command:

```python
# Example: Run all three traffic scenarios
results = experiment_engine.run_multi_scenario_experiment(
    scenarios=['low_traffic', 'medium_traffic', 'high_congestion']
)
```

This automatically:
1. Generates appropriate traffic patterns for each scenario
2. Runs baseline mode
3. Runs optimized mode with DQN training
4. Logs all metrics to CSV
5. Generates all comparison graphs
6. Produces summary statistics and improvement percentages

### ✓ Real-Time Visualization (FastAPI)

Web-based dashboard accessible at `http://localhost:8000/docs`:

- Real-time topology visualization
- Current network metrics display
- Experiment status tracking
- Parameter adjustment interface
- Download generated graphs

---

## File Structure

```
backend/
├── environment.py          # 5G network simulation environment
├── agent.py                # DQN agent with LSTM predictor
├── baseline_simulator.py    # Baseline mode (no optimization)
├── experiment_engine.py     # Orchestrates dual-phase experiments
├── data_logger.py           # Comprehensive CSV logging
├── graph_generator.py       # IEEE-standard graph generation
├── parameter_manager.py     # User parameter control
├── main.py                  # FastAPI server with REST endpoints
├── run_experiments.py       # Standalone experiment runner
├── requirements.txt         # Python dependencies
└── README.md                # This file

logs/
├── baseline_*.csv           # Baseline phase detailed logs
└── optimized_*.csv          # Optimized phase detailed logs

graphs/
├── latency_comparison_*.png
├── packet_loss_comparison_*.pdf
├── throughput_comparison_*.png
├── congestion_comparison_*.png
├── reward_convergence_*.png
├── improvement_summary_*.pdf
└── ...                      # (All in PNG and PDF formats)
```

---

## Usage

### Option 1: Command-Line Experiments

```python
python run_experiments.py
```

This demonstrates:
- Single controlled experiment
- Multi-scenario automated experiments
- Parameter control examples
- DQN convergence analysis

### Option 2: FastAPI Server with REST API

```bash
# Start server
python main.py

# Server runs at http://localhost:8000
# Interactive docs: http://localhost:8000/docs
```

**Key API Endpoints:**

```
# Run a controlled experiment
POST /experiment/run
{
  "num_steps": 100,
  "optimized_episodes": 3,
  "scenario": "medium_traffic",
  "seed": 42
}

# Run multiple scenarios automatically
POST /experiment/run-multi-scenario
{
  "scenarios": ["low_traffic", "medium_traffic", "high_congestion"],
  "num_steps": 100
}

# Get experiment status
GET /experiment/status

# Update parameters
POST /parameters/update
{
  "traffic_scenario": "high",
  "congestion_threshold": 0.7
}

# Get comparison table
GET /data/comparison-table

# List generated graphs
GET /graphs/list
```

### Option 3: Python Script Integration

```python
from environment import FiveGEnvironment
from agent import XDQNAgent
from experiment_engine import ExperimentEngine
from parameter_manager import ParameterManager

# Initialize
env = FiveGEnvironment()
agent = XDQNAgent(state_dim=21, action_dim=9)
param_manager = ParameterManager()
engine = ExperimentEngine(env, agent, param_manager)

# Run experiment
result = engine.run_complete_experiment(
    num_steps=100,
    optimized_episodes=5,
    scenario="my_scenario"
)

# Access results
print(result['comparison']['latency_improvement_percent'])
```

---

## Comparison Summary Table (Example Output)

Generated automatically after each experiment:

```
Metric                 Baseline      PCAN-5G      Improvement (%)
─────────────────────────────────────────────────────────────────
Average Latency        45.3 ms       28.7 ms      -36.6%
Packet Loss Rate       0.0451        0.0162       -64.1%
Average Throughput    245.6 Mbps    312.4 Mbps    +27.2%
Network Congestion     0.682         0.421        -38.3%
```

**Interpretation:**
- Negative percentages for Latency and Loss = **IMPROVEMENT** (lower is better)
- Positive percentage for Throughput = **IMPROVEMENT** (higher is better)
- Negative percentage for Congestion = **IMPROVEMENT** (lower is better)

---

## Customizing Experiments

### Example 1: High-Stress Scenario

```python
param_manager.set_traffic_scenario('high')
param_manager.set_link_failure_probability(0.02)
param_manager.set_sinr_threshold(-10)

result = engine.run_complete_experiment(
    num_steps=200,
    optimized_episodes=10,
    scenario="high_stress_scenario"
)
```

### Example 2: Dense Network

```python
param_manager.set_node_density('dense')
param_manager.set_packet_rate('high')
param_manager.set_congestion_threshold(0.6)

result = engine.run_complete_experiment(
    num_steps=150,
    scenario="dense_network_scenario"
)
```

### Example 3: Reproducible Research

```python
# Same seed = same randomness = reproducible results
engine.set_random_seed(42)

result = engine.run_complete_experiment(
    num_steps=100,
    scenario="reproducible_experiment"
)
```

---

## Data Analysis

### Loading and Analyzing Results

```python
import pandas as pd

# Load baseline logs
baseline_df = pd.read_csv('logs/baseline_*.csv')

# Load optimized logs
optimized_df = pd.read_csv('logs/optimized_*.csv')

# Compare metrics
print("Baseline avg latency:", baseline_df['latency_ms'].mean())
print("Optimized avg latency:", optimized_df['latency_ms'].mean())

# Slice-specific analysis
embb_baseline = baseline_df[baseline_df['slice_name'] == 'eMBB']
embb_optimized = optimized_df[optimized_df['slice_name'] == 'eMBB']

# Time-series analysis
import matplotlib.pyplot as plt
plt.plot(baseline_df['latency_ms'], label='Baseline')
plt.plot(optimized_df['latency_ms'], label='Optimized')
plt.legend()
plt.show()
```

---

## System Requirements

**Minimal Hardware:**
- CPU: Quad-core or better
- RAM: 4GB minimum (8GB+ recommended)
- Storage: 500MB for complete experimental run

**Python Dependencies:**
- PyTorch (GPU acceleration optional but recommended)
- NetworkX (network topology)
- Pandas (data analysis)
- Matplotlib (graph generation)
- FastAPI + Uvicorn (REST API)

**Installation:**
```bash
pip install -r requirements.txt
```

---

## Research Paper Integration

### How to Use for IEEE Paper

**Section: Methodology**
- Cite the baseline vs optimized comparison framework
- Reference the controlled experiment engine
- Explain identical initial conditions
- Describe parameter variations

**Section: Experiments**
- Show comparison graphs (use `*.pdf` files)
- Include comparison summary table
- Report improvement percentages
- Cite traffic scenarios used

**Section: Results**
- Include latency/throughput graphs
- Show DQN convergence
- Present prediction accuracy
- Demonstrate fairness across slices

**Appendix: Reproducibility**
- Provide random seed used
- Document parameter settings
- List traffic scenarios
- Share logs if requested

---

## Troubleshooting

### Q: Graphs not generated?
A: Check that `./graphs/` directory exists and has write permissions.

### Q: ImportError when running?
A: Ensure all dependencies are installed: `pip install -r requirements.txt`

### Q: OutOfMemory errors?
A: Reduce `num_steps` or `optimized_episodes`, or upgrade RAM.

### Q: Results not reproducible?
A: Set random seed: `engine.set_random_seed(YOUR_SEED)`

---

## Future Enhancements

- Multi-agent scenarios
- Network slicing with different SLAs
- Modular graph generation options
- Integration with real network traces
- WebSocket support for real-time monitoring
- Database backend for long-term tracking

---

## Citation

If you use this platform in research, please cite:

```
5G Cross-Layer DQN PCAN-5G Research Platform v2.0
A Research-Grade Experimental Platform for Baseline vs 
Optimized 5G Network Simulation with IEEE-Standard Graph Generation
```

---

## Contact & Support

For issues, suggestions, or custom modifications, please refer to the development team.

---

**Last Updated**: 2024
**Version**: 2.0
**Status**: Production-Ready for Research
