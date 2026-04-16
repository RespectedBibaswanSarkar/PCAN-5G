# API Reference - 5G PCAN-5G Research Platform

## Base URL

```
http://localhost:8000
```

Interactive API documentation available at: `http://localhost:8000/docs`

---

## Authentication
None (open API for research purposes)

---

## Endpoints

### 1. SYSTEM INFORMATION

#### Get System Info
```
GET /info
```

**Response:**
```json
{
  "title": "5G X-DQN PCAN-5G Research Platform",
  "version": "2.0",
  "components": {
    "baseline_simulator": "Enabled",
    "dqn_agent": "Enabled",
    "lstm_predictor": "Enabled",
    "experiment_engine": "Enabled",
    "graph_generator": "IEEE-standard publication quality"
  },
  "features": [
    "Dual-phase controlled experiments",
    "Baseline vs PCAN-5G comparison",
    ...
  ],
  "output_directories": {
    "logs": "./logs",
    "graphs": "./graphs"
  }
}
```

---

### 2. EXPERIMENTS

#### Run Single Controlled Experiment
```
POST /experiment/run
```

**Request Body:**
```json
{
  "num_steps": 100,
  "optimized_episodes": 3,
  "scenario": "medium_traffic",
  "seed": 42
}
```

**Parameters:**
- `num_steps` (int): Simulation timesteps per phase (default: 100)
- `optimized_episodes` (int): Training episodes for optimized phase (default: 3)
- `scenario` (string): Scenario name for identification
- `seed` (int, optional): Random seed for reproducibility

**Response:**
```json
{
  "message": "Experiment started",
  "scenario": "medium_traffic",
  "num_steps": 100,
  "optimized_episodes": 3
}
```

**Note**: Experiment runs in background. Check status with `/experiment/status`

---

#### Run Multi-Scenario Experiments
```
POST /experiment/run-multi-scenario
```

**Request Body:**
```json
{
  "scenarios": ["low_traffic", "medium_traffic", "high_congestion"],
  "num_steps": 100
}
```

**Parameters:**
- `scenarios` (array): List of scenario names to run
- `num_steps` (int): Steps per scenario

**Response:**
```json
{
  "message": "Multi-scenario experiment started",
  "scenarios": ["low_traffic", "medium_traffic", "high_congestion"],
  "num_steps": 100
}
```

**Available Scenarios:**
- `low_traffic`: 50-100 Mbps traffic load
- `medium_traffic`: 100-200 Mbps traffic load
- `high_congestion`: 200-300 Mbps traffic load (high stress)

---

#### Get Experiment Status
```
GET /experiment/status
```

**Response:**
```json
{
  "status": "running",
  "current_scenario": "medium_traffic",
  "progress": 45,
  "result": {
    "scenario": "medium_traffic",
    "baseline": {...},
    "optimized": {...},
    "comparison": {...},
    "duration_seconds": 234.5
  }
}
```

**Status Values:**
- `idle`: No experiment running
- `running`: Experiment in progress
- `completed`: Experiment finished
- `progress`: Percentage (0-100)

---

### 3. PARAMETERS

#### Get Current Parameters
```
GET /parameters/current
```

**Response:**
```json
{
  "traffic_scenario": "medium",
  "traffic_range": [100, 200],
  "node_density": "normal",
  "node_count": 10,
  "packet_rate": "medium",
  "packet_rate_pps": 50,
  "thresholds": {
    "sinr_min": -5,
    "rsrp_min": -100,
    "congestion_max": 0.8,
    "latency_max": 50
  },
  "link_failure_probability": 0.0,
  "node_failure_probability": 0.0
}
```

---

#### Update Parameters
```
POST /parameters/update
```

**Request Body:**
```json
{
  "traffic_scenario": "high",
  "node_density": "dense",
  "packet_rate": "high",
  "sinr_threshold": -8,
  "rsrp_threshold": -95,
  "congestion_threshold": 0.7,
  "latency_threshold": 40,
  "link_failure_probability": 0.01,
  "node_failure_probability": 0.005
}
```

**Parameter Details:**

| Parameter | Valid Values | Default | Unit |
|-----------|-------------|---------|------|
| traffic_scenario | low, medium, high | medium | - |
| node_density | sparse, normal, dense | normal | - |
| packet_rate | low, medium, high | medium | - |
| sinr_threshold | -20 to 10 | -5 | dB |
| rsrp_threshold | -150 to -50 | -100 | dBm |
| congestion_threshold | 0.0 to 1.0 | 0.8 | ratio |
| latency_threshold | 1 to 100 | 50 | ms |
| link_failure_probability | 0.0 to 1.0 | 0.0 | ratio |
| node_failure_probability | 0.0 to 1.0 | 0.0 | ratio |

**Response:**
```json
{
  "message": "Parameters updated",
  "current_params": { ... }
}
```

---

#### Reset Parameters to Defaults
```
POST /parameters/reset
```

**Response:**
```json
{
  "message": "Parameters reset to defaults",
  "current_params": { ... }
}
```

---

### 4. DATA & RESULTS

#### Get Comparison Table
```
GET /data/comparison-table
```

**Response:**
```json
{
  "latency_improvement_percent": -36.6,
  "packet_loss_improvement_percent": -64.1,
  "throughput_improvement_percent": 27.2,
  "congestion_improvement_percent": -38.3,
  "baseline_stats": {
    "avg_latency": 45.3,
    "max_latency": 89.5,
    "min_latency": 12.1,
    "avg_packet_loss": 0.0451,
    "avg_throughput": 245.6,
    "avg_congestion": 0.682,
    "total_logs": 300
  },
  "optimized_stats": {
    "avg_latency": 28.7,
    "max_latency": 56.2,
    "min_latency": 8.4,
    "avg_packet_loss": 0.0162,
    "avg_throughput": 312.4,
    "avg_congestion": 0.421,
    "avg_dqn_reward": 2.34,
    "avg_prediction_error": 0.156,
    "total_logs": 300
  }
}
```

**Improvement Interpretation:**
- Negative values for Latency/Loss/Congestion = **BETTER** (lower is better)
- Positive values for Throughput = **BETTER** (higher is better)

---

#### Get Baseline Statistics
```
GET /data/baseline-stats
```

**Response:**
```json
{
  "avg_latency": 45.3,
  "max_latency": 89.5,
  "min_latency": 12.1,
  "avg_packet_loss": 0.0451,
  "avg_throughput": 245.6,
  "avg_congestion": 0.682,
  "total_logs": 300
}
```

---

#### Get Optimized Statistics
```
GET /data/optimized-stats
```

**Response:** (includes additional DQN-specific metrics)
```json
{
  "avg_latency": 28.7,
  "max_latency": 56.2,
  "min_latency": 8.4,
  "avg_packet_loss": 0.0162,
  "avg_throughput": 312.4,
  "avg_congestion": 0.421,
  "avg_dqn_reward": 2.34,
  "avg_prediction_error": 0.156,
  "total_logs": 300
}
```

---

### 5. GRAPHS

#### List Generated Graphs
```
GET /graphs/list
```

**Response:**
```json
{
  "graph_directory": "./graphs",
  "total_graphs": 21,
  "graphs": [
    "latency_comparison_low_traffic.png",
    "latency_comparison_medium_traffic.png",
    "packet_loss_comparison_low_traffic.png",
    "throughput_comparison_low_traffic.png",
    "congestion_comparison_low_traffic.png",
    "reward_convergence_low_traffic.png",
    "improvement_summary_low_traffic.pdf",
    ...
  ]
}
```

---

#### Download Graph
```
GET /graphs/download/{filename}
```

**Parameters:**
- `filename` (string): Name of the graph file

**Response:** (File download)
```json
{
  "file_path": "./graphs/latency_comparison_medium_traffic.png",
  "exists": true
}
```

**Supported Formats:**
- All graphs in PNG (300 DPI) for screen viewing
- All graphs in PDF for publication inclusion

**Available Graphs:**
- `latency_comparison_*.png/pdf`
- `packet_loss_comparison_*.png/pdf`
- `throughput_comparison_*.png/pdf`
- `congestion_comparison_*.png/pdf`
- `reward_convergence_*.png/pdf` (optimized mode only)
- `prediction_accuracy_*.png/pdf` (optimized mode only)
- `metrics_comparison_bars_*.png/pdf`
- `improvement_summary_*.png/pdf`

---

### 6. NETWORK TOPOLOGY

#### Get Topology
```
GET /topology
```

**Response:**
```json
{
  "nodes": [
    {"id": 0, "pos": [0, 0]},
    {"id": 1, "pos": [-2, 2]},
    ...
  ],
  "links": [
    {"source": 0, "target": 1},
    ...
  ]
}
```

---

#### Get Current Metrics
```
GET /metrics/current
```

**Response:**
```json
{
  "topology": [...],
  "metrics": {
    "avg_latency": 28.5,
    "avg_throughput": 310.2,
    "avg_congestion": 0.42,
    "avg_packet_loss": 0.016
  }
}
```

---

### 7. TRAINING (Legacy)

#### Start DQN Training
```
POST /train
```

**Request Body:**
```json
{
  "episodes": 100
}
```

**Response:**
```json
{
  "message": "Training started",
  "episodes": 100
}
```

---

#### Get Training Status
```
GET /status
```

**Response:**
```json
{
  "status": "training",
  "episode": 45,
  "total_episodes": 100,
  "history": [
    {
      "episode": 0,
      "reward": 2.34,
      "latency": 45.3,
      "baseline_latency": 50.2
    },
    ...
  ]
}
```

---

## Example Workflows

### Workflow 1: Quick Comparison Test

```bash
# 1. Run single experiment (low traffic)
curl -X POST http://localhost:8000/experiment/run \
  -H "Content-Type: application/json" \
  -d '{"scenario": "test", "num_steps": 50, "optimized_episodes": 2}'

# 2. Check status
curl http://localhost:8000/experiment/status

# 3. Get comparison results
curl http://localhost:8000/data/comparison-table

# 4. List graphs
curl http://localhost:8000/graphs/list
```

### Workflow 2: Full Research Suite

```bash
# 1. Set high-stress parameters
curl -X POST http://localhost:8000/parameters/update \
  -H "Content-Type: application/json" \
  -d '{
    "traffic_scenario": "high",
    "link_failure_probability": 0.02,
    "sinr_threshold": -10
  }'

# 2. Run multi-scenario experiments
curl -X POST http://localhost:8000/experiment/run-multi-scenario \
  -H "Content-Type: application/json" \
  -d '{
    "scenarios": ["low_traffic", "medium_traffic", "high_congestion"],
    "num_steps": 150
  }'

# 3. Monitor progress
watch 'curl http://localhost:8000/experiment/status | python -m json.tool'

# 4. Download results
curl http://localhost:8000/graphs/list | jq '.graphs[]' | \
  xargs -I {} curl -O http://localhost:8000/graphs/download/{}
```

### Workflow 3: Python Client

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Run experiment
response = requests.post(
    f"{BASE_URL}/experiment/run",
    json={
        "scenario": "my_scenario",
        "num_steps": 100,
        "optimized_episodes": 5,
        "seed": 42
    }
)
print(response.json())

# Poll status
import time
while True:
    status = requests.get(f"{BASE_URL}/experiment/status").json()
    print(f"Progress: {status['progress']}%")
    if status['status'] == 'completed':
        break
    time.sleep(10)

# Get comparison
comparison = requests.get(f"{BASE_URL}/data/comparison-table").json()
print(f"Latency improvement: {comparison['latency_improvement_percent']:.1f}%")

# List graphs
graphs = requests.get(f"{BASE_URL}/graphs/list").json()
print(f"Generated {graphs['total_graphs']} graphs")
```

---

## Error Handling

### Common Errors

**400 - Invalid Parameter**
```json
{
  "detail": "Invalid traffic_scenario: invalid_value"
}
```

**404 - Graph Not Found**
```json
{
  "exists": false,
  "error": "Graph not found"
}
```

**500 - Server Error**
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

No rate limiting for research purposes. However, long-running experiments blocks other operations.

**Recommendation:** Run experiments asynchronously and check status periodically.

---

## Data Export Formats

### CSV Logs
- Timestep-by-timestep metrics
- Compatible with Pandas/Excel
- Suitable for custom analysis

### JSON Responses
- All API responses in JSON
- Easy integration with analysis tools
- Suitable for programmatic access

### PNG/PDF Graphs
- Publication-ready quality (300 DPI)
- Transparent background
- IEEE-standard formatting

---

## Reproducibility

To ensure reproducible research:

```json
{
  "num_steps": 100,
  "optimized_episodes": 5,
  "scenario": "reproducible_exp",
  "seed": 12345
}
```

**Same seed → Same results** across runs
