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

## 🔬 Research Documentation Layer [NEW]

PCAN-5G is now augmented with a comprehensive, research-backed documentation layer that maps every core module to established academic literature.

### 📚 Core Academic Papers (Simulated Foundations)
The platform's architecture and logic are grounded in the following provided foundational works:

1.  **SDN Architecture**: Kreutz et al., *“A Survey on Software-Defined Networking”* (2015)
2.  **Congestion Control**: Michael Welzl, *“Network Congestion Control: A Survey”* (2005)
3.  **Wireless ML**: H. Ye et al., *“The Role of Machine Learning in Future Wireless Networks”* (2018)
4.  **RL Routing**: Boyan & Littman, *“Q-Routing: A Reinforcement Learning Approach to Routing”* (1994)
5.  **5G Systems**: Theodore S. Rappaport et al., *“5G Wireless Communication Systems”* (2013)
6.  **Network Slicing**: Xiaofei Zhou et al., *“Network Slicing for 5G”* (2017)
7.  **Graph Modeling**: Albert Mestres et al., *“RouteNet: Leveraging Graph Neural Networks”* (2019)
8.  **DRL Survey**: Y. Sun et al., *“Deep Reinforcement Learning for Networking: A Survey”* (2019)
9.  **6G Vision**: IEEE, *“AI-Native 6G Networks”* (2023–2024)

### 📂 High-Fidelity Documentation
| Document | Description |
| :--- | :--- |
| **[System Overview](docs/SYSTEM_OVERVIEW.md)** | High-level research context and system objectives. |
| **[Module Mapping](docs/MODULE_TO_RESEARCH_MAP.md)** | File-by-file link between code and academic concepts. |
| **[Foundations](docs/RESEARCH_FOUNDATIONS.md)** | Deep-dive into SDN, DRL, and 5G Slicing theory. |
| **[Architecture](docs/ARCHITECTURE.md)** | Layered system design (Simulation, Logic, Control). |
| **[Process Flow](docs/PROCESS_FLOW.md)** | Operational lifecycle research link (Init → Act → Reward). |
| **[Future Roadmap](docs/FUTURE_EXTENSIONS.md)** | Literature-backed theoretical extensions (GNNs, 6G). |

---

## Key Features

| Feature | Description |
| :--- | :--- |
| **Research Layer** | **Fully mapped documentation layer linking code to 9 specific academic papers.** |
| **Cross-Layer State** | PHY (RSRP/SINR) + Network (queue lengths) + Resource (BW alloc) + Traffic load fused into a single state vector |
| **Joint Action Space** | Single discrete action controls both routing topology AND slice bandwidth delta simultaneously |
| **LSTM Predictor** | Auxiliary LSTM predicts next-step traffic for proactive congestion avoidance (Ye et al., 2018) |
| **RF Digital Twin** | Realistic RF signal layer (Hardware/Filter/Amp/Oscillator) based on 5G PHY constraints |
| **Live Dashboard** | React + WebSocket streaming for real-time training and metric visualization |

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
├── docs/                     # NEW: Research Documentation Layer
│   ├── SYSTEM_OVERVIEW.md    # High-level architecture mapping
│   ├── MODULE_TO_RESEARCH_MAP.md # Module-to-Paper mapping
│   ├── RESEARCH_FOUNDATIONS.md # Theoretical deep-dive
│   ├── FUTURE_EXTENSIONS.md  # Academic roadmap
│   ├── ARCHITECTURE.md       # Layered system design
│   └── PROCESS_FLOW.md       # Lifecycle research link
│
├── backend/
│   ├── hardware/             # Physical Layer abstraction (Signal, Filter, Amp...)
│   ├── main.py               # FastAPI app — SDN Controller
│   ├── agent.py              # XDQNAgent: RL + LSTM Prediction
│   ├── environment.py        # FiveGEnvironment: Data Plane Simulation
│   ├── requirements.txt
│   └── ...
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── RFDashboard.jsx      # RF Signal pipeline visualization
│   │   │   ├── NetworkTopology.jsx  # Waveguide pipe rendering
│   │   │   └── ...
│   └── ...
│
├── start_all.py              # One-click launcher
└── ...
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
B.Tech, IIIT Manipur 
[GitHub: @RespectedBibaswanSarkar](https://github.com/RespectedBibaswanSarkar)

---

## License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.
