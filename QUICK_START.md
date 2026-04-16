# Quick Start Guide - 5G PCAN-5G Research Platform

## 🚀 One-Minute Start

### Option 1: Full Platform (API + Frontend)
```bash
python start_all.py
```
- Opens API at: http://localhost:8000
- Opens Frontend at: http://localhost:5173

### Option 2: Experiments Only (No Frontend)
```bash
cd backend
python main.py
```
- API + Interactive docs at: http://localhost:8000/docs

### Option 3: Standalone Scripts (No Server)
```bash
cd backend
python run_experiments.py
```
- Runs all examples automatically
- Creates output files in `./logs` and `./graphs`

---

## 📊 Example Experiments

### Run Single Experiment
```bash
curl -X POST http://localhost:8000/experiment/run \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "medium_traffic",
    "num_steps": 100,
    "optimized_episodes": 3
  }'
```

### Run Multi-Scenario (Automated)
```bash
curl -X POST http://localhost:8000/experiment/run-multi-scenario \
  -H "Content-Type: application/json" \
  -d '{
    "scenarios": ["low_traffic", "medium_traffic", "high_congestion"],
    "num_steps": 100
  }'
```

### Check Status
```bash
curl http://localhost:8000/experiment/status | python -m json.tool
```

### Get Results
```bash
curl http://localhost:8000/data/comparison-table | python -m json.tool
```

---

## 🎛️ Parameter Control

### View Current Parameters
```bash
curl http://localhost:8000/parameters/current
```

### Update Parameters (High Stress Scenario)
```bash
curl -X POST http://localhost:8000/parameters/update \
  -H "Content-Type: application/json" \
  -d '{
    "traffic_scenario": "high",
    "link_failure_probability": 0.02,
    "node_failure_probability": 0.01,
    "congestion_threshold": 0.7
  }'
```

---

## 📈 Generate Graphs

### See Available Graphs
```bash
curl http://localhost:8000/graphs/list
```

### Download Graphs
```bash
# Download single graph
curl -O http://localhost:8000/graphs/download/latency_comparison_medium_traffic.pdf

# Or check local filesystem
ls -la ./graphs/
```

---

## 💻 Python Integration

```python
from environment import FiveGEnvironment
from agent import XDQNAgent
from experiment_engine import ExperimentEngine
from parameter_manager import ParameterManager

# Initialize
env = FiveGEnvironment()
agent = XDQNAgent(state_dim=21, action_dim=9)
params = ParameterManager()
engine = ExperimentEngine(env, agent, params)

# Configure
params.set_traffic_scenario('high')
params.set_congestion_threshold(0.75)

# Run
result = engine.run_complete_experiment(
    num_steps=100,
    optimized_episodes=5,
    scenario="my_test"
)

# Analyze
improvement = result['comparison']['latency_improvement_percent']
print(f"Latency improved by {improvement:.1f}%")
```

---

## 📁 Output Files

### Logs (Timestep-by-timestep)
```
logs/
  ├── baseline_my_test_*.csv
  └── optimized_my_test_*.csv
```

### Graphs (Publication-ready)
```
graphs/
  ├── latency_comparison_my_test.png
  ├── latency_comparison_my_test.pdf
  ├── packet_loss_comparison_my_test.png
  ├── throughput_comparison_my_test.png
  ├── congestion_comparison_my_test.png
  ├── reward_convergence_my_test.png
  ├── improvement_summary_my_test.pdf
  └── metrics_comparison_bars_my_test.png
```

---

## 📋 Comparison Summary

After experiment completes:

```
Metric              Baseline      PCAN-5G      Improvement
─────────────────────────────────────────────────────────
Latency (ms)        45.3          28.7         -36.6%
Packet Loss         0.0451        0.0162       -64.1%
Throughput (Mbps)   245.6         312.4        +27.2%
Congestion          0.682         0.421        -38.3%
```

---

## 🔑 Key Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/experiment/run` | Single dual-phase experiment |
| POST | `/experiment/run-multi-scenario` | Automated multi-scenario |
| GET | `/experiment/status` | Check progress |
| POST | `/parameters/update` | Control experiment parameters |
| GET | `/parameters/current` | View active parameters |
| GET | `/data/comparison-table` | Summary statistics |
| GET | `/graphs/list` | List generated graphs |
| GET | `/graphs/download/{file}` | Download PNG/PDF |
| GET | `/info` | System information |

---

## 🎯 Common Workflows

### Workflow 1: Validate System (5 min)
```bash
# 1. Start platform
python start_all.py

# 2. Run quick test
curl -X POST http://localhost:8000/experiment/run \
  -d '{"scenario":"test","num_steps":50,"optimized_episodes":2}'

# 3. Check results
curl http://localhost:8000/data/comparison-table

# 4. Download graph
curl -O http://localhost:8000/graphs/download/latency_comparison_test.pdf
```

### Workflow 2: Publication Suite (15 min)
```bash
cd backend

# Run all three scenarios with IEEE graphs
python run_experiments.py

# Results automatically in ./logs and ./graphs
# Ready for inclusion in research paper
```

### Workflow 3: Custom High-Stress Test (10 min)
```bash
# REST call or Python:
curl -X POST http://localhost:8000/parameters/update \
  -d '{"traffic_scenario":"high","link_failure_probability":0.05}'

curl -X POST http://localhost:8000/experiment/run \
  -d '{"scenario":"stress_test","num_steps":200,"optimized_episodes":10}'

# Monitor with status endpoint
# Download results when complete
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8000 in use | `netstat -an \| grep 8000` to find process, kill it |
| ImportError | `pip install -r requirements.txt` |
| Graphs not found | `mkdir graphs` if needed |
| No logs | Check write permissions in `./logs` directory |
| API not responding | Verify `python main.py` running with no errors |

---

## 📖 Learn More

- **Full Guide:** `README_RESEARCH_PLATFORM.md`
- **API Docs:** `API_REFERENCE.md`
- **Examples:** `run_experiments.py`
- **Interactive:** http://localhost:8000/docs (when running)

---

## ✅ Verify Installation

```bash
cd backend

# Check imports
python -c "from baseline_simulator import BaselineSimulator; print('✓')"
python -c "from experiment_engine import ExperimentEngine; print('✓')"
python -c "from graph_generator import GraphGenerator; print('✓')"
python -c "from data_logger import DataLogger; print('✓')"
python -c "from parameter_manager import ParameterManager; print('✓')"

# All should print ✓
```

---

## 🎓 For Your Research Paper

### Include in Paper:
1. Comparison graphs (PDF format)
2. Comparison summary table
3. Improvement percentages
4. Random seed used (for reproducibility)
5. Traffic scenarios tested

### Example Citation:
> "Experiments conducted using the 5G PCAN-5G Research Platform v2.0 comparing
> baseline (non-optimized) vs PCAN-5G (DQN-optimized) 5G network simulations
> under low, medium, and high traffic scenarios."

---

**Ready to start?** → `python start_all.py` ✨
