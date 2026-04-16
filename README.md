# 5G X-DQN Orchestrator

> **A Cross-Layer Deep Q-Network (X-DQN) for Autonomous 5G Network Management**  
> Real-time slice resource allocation and traffic routing using Reinforcement Learning + LSTM prediction.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://reactjs.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

This project implements an original **Cross-Layer Deep Q-Network (X-DQN)** that jointly optimizes:

- **Traffic Routing** — across a 10-node C-RAN topology (CU → DU → RRH → UE)
- **Network Slicing** — dynamic bandwidth allocation for eMBB, URLLC, and mMTC slices
- **Physical Layer Awareness** — RSRP and SINR metrics feed directly into the DRL state
- **Predictive Control** — an LSTM module forecasts future congestion before it occurs

The system is deployed as an interactive **real-time web dashboard** where you can watch the agent train, toggle network nodes on/off, and observe live metrics streaming over WebSocket.

---

## Key Features

| Feature | Description |
|---|---|
| **Cross-Layer State** | PHY (RSRP/SINR) + Network (queue lengths) + Resource (BW alloc) + Traffic load fused into a single 21-dim state vector |
| **Joint Action Space** | Single discrete action controls both routing topology AND slice bandwidth delta simultaneously |
| **LSTM Predictor** | Auxiliary LSTM trained alongside DQN — predicts next-step traffic, appended to state for proactive decisions |
| **Custom Reward** | Composite: `2×Throughput − 1×Latency − 5×PacketLoss + 3×Fairness` across all slices |
| **Live Dashboard** | React + Recharts frontend with WebSocket streaming — see rewards, latency, and topology in real time |
| **Node Fault Simulation** | Toggle any network node active/inactive from the UI or API to simulate failure scenarios |

---

## Algorithm: X-DQN

### Architecture

```
State (21-dim)
  ├── PHY Layer:      avg RSRP, avg SINR            (2)
  ├── Resource Layer: BW alloc per slice             (3)
  ├── Network Layer:  queue length per node          (10)
  ├── App Layer:      traffic load per slice          (3)
  └── LSTM Output:    predicted traffic (3 slices)   (3)
          │
          ▼
    ┌─────────────────┐        ┌──────────────────┐
    │   QNetwork      │        │ CongestionPredictor│
    │  (Online)       │        │   (LSTM)          │
    │  21→128→64→9   │        │   seq(3)→32→3     │
    └────────┬────────┘        └──────────────────┘
             │ ε-greedy                 ▲
             ▼                         │
         Action (9)            traffic_history[-5:]
    (routing × BW delta)
             │
             ▼
    ┌─────────────────┐
    │  Target Network │  ← soft-updated every episode
    │  (Frozen copy)  │
    └─────────────────┘
```

### Action Decoding
```
action_idx (0–8):
  routing_choice = action_idx // 3   → 0, 1, or 2
  bandwidth_delta = (action_idx % 3) - 1  → −10, 0, or +10 Mbps
```

### Reward Function
```python
reward = (2.0 × throughput/500)
       − (1.0 × sum_latency/100)
       − (5.0 × sum_packet_loss×10)
       + (3.0 × (1 − std(satisfaction_scores)))
```

### Hyperparameters

| Parameter | Value |
|---|---|
| Discount factor γ | 0.95 |
| Learning rate | 0.001 (Adam) |
| Batch size | 32 |
| Replay buffer | 2000 |
| ε start / end / decay | 1.0 / 0.01 / 0.995 |
| LSTM hidden dim | 32 |
| LSTM sequence length | 5 |

---

## Network Topology

```
        [CU] (Node 0)
        /          \
    [DU1]          [DU2]
    /    \            \
[RRH1] [RRH2]       [RRH3]
  / \     / \         /   \
[UE6][UE7][UE7][UE8][UE8][UE9]
```

- **CU** (Central Unit) — Core orchestration, RL agent hosted here
- **DU** (Distributed Units) — Fronthaul aggregation
- **RRH** (Remote Radio Heads / gNodeBs) — Radio access, PHY metrics computed per link
- **UE Hotspots** — Dynamic traffic source (50–300 Mbps per step, spike injection every 30 steps)

---

## Tech Stack

### Backend
- **FastAPI** — REST + WebSocket API server
- **Uvicorn** — ASGI runtime
- **PyTorch** — DQN + LSTM neural networks
- **NetworkX** — C-RAN graph topology
- **NumPy / Pandas / SciPy** — numerics and data processing
- **Matplotlib** — graph visualization (research mode)

### Frontend
- **React 18** — component-based UI
- **Vite 5** — fast build and dev server
- **Recharts** — real-time metric charts
- **Lucide React** — icon set
- **Axios** — HTTP client
- **Native WebSocket** — live metric streaming from FastAPI

---

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+

### One-Command Launch
```bash
python start_all.py
```

This will automatically:
1. Install backend Python dependencies (`requirements.txt`)
2. Install frontend Node dependencies (`package.json`)
3. Start the FastAPI server on **port 8000**
4. Start the Vite dev server on **port 5173**
5. Open the dashboard in your browser

### Manual Launch (if preferred)

**Terminal 1 — Backend:**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Then open: **http://localhost:5173**

---

## Project Structure

```
.
├── backend/
│   ├── main.py               # FastAPI app — REST + WebSocket endpoints
│   ├── agent.py              # XDQNAgent: QNetwork + LSTM CongestionPredictor
│   ├── environment.py        # FiveGEnvironment: C-RAN simulation + reward
│   ├── experiment_engine.py  # Controlled baseline vs. optimized experiments
│   ├── baseline_simulator.py # Static routing baseline (no AI)
│   ├── graph_generator.py    # IEEE-standard publication-quality graph output
│   ├── data_logger.py        # Per-timestep CSV logging (latency, loss, SINR...)
│   ├── parameter_manager.py  # Runtime experiment parameter control
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # Main dashboard layout
│   │   ├── components/
│   │   │   ├── NetworkTopology.jsx   # Interactive D3-style topology renderer
│   │   │   ├── RealtimeCharts.jsx    # Live metric charts (Recharts)
│   │   │   └── ParameterControl.jsx  # Runtime parameter sliders
│   │   └── services/
│   │       └── api.js        # Axios + WebSocketManager
│   ├── package.json
│   └── vite.config.js
│
├── start_all.py              # One-click launcher (Python)
├── start_all.bat             # One-click launcher (Windows Batch)
├── start_all.ps1             # One-click launcher (PowerShell)
└── LICENSE
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/train` | Start DQN training (background) |
| `GET` | `/status` | Training status + episode history |
| `GET` | `/topology` | Network graph nodes and links |
| `GET` | `/metrics/current` | Current per-slice metrics |
| `POST` | `/node/toggle` | Activate or deactivate a node |
| `WS` | `/ws` | WebSocket for live metric streaming |
| `GET` | `/info` | System metadata |

---

## Research Mode

The platform includes an experiment engine for controlled **Baseline vs. Optimized** comparisons:

```bash
# Run a single scenario
curl -X POST http://localhost:8000/experiment/run \
  -H "Content-Type: application/json" \
  -d '{"num_steps": 100, "optimized_episodes": 5, "scenario": "high_congestion", "seed": 42}'

# Run all 3 scenarios (low / medium / high traffic)
curl -X POST http://localhost:8000/experiment/run-multi-scenario
```

Generated graphs (PNG + PDF, 300 DPI) are saved to `backend/graphs/` — suitable for IEEE paper figures.

---

## Results (Typical — High Congestion Scenario)

| Metric | Baseline (Static) | X-DQN Optimized | Improvement |
|---|---|---|---|
| Avg Latency | ~507 ms | ~320 ms | **−36%** |
| Packet Loss | ~0.63 | ~0.22 | **−65%** |
| Throughput | ~42 Mbps | ~58 Mbps | **+38%** |
| Congestion Index | ~0.84 | ~0.52 | **−38%** |

---

## Author

**Bibaswan Sarkar**  
M.Tech, IIIT Manipur — Semester II  
[GitHub: @RespectedBibaswanSarkar](https://github.com/RespectedBibaswanSarkar)

---

## License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.
