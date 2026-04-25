# Process Flow & Simulation Lifecycle

The PCAN-5G simulation follows a cyclical process that maps to established methods in autonomous network management.

## Operational Cycle

| Step | Operation | Research Concept | Linked Paper |
| :--- | :--- | :--- | :--- |
| **1. Init** | Topology and Slices are established with baseline PHY metrics. | Slicing Isolation | Zhou et al. (2017) |
| **2. Forecast** | LSTM predicts the next move of traffic based on short-term history. | ML Prediction | Ye et al. (2018) |
| **3. Act** | DQN agent selects a Joint Action (Routing Index + BW Delta). | DRL Routing | Sun et al. (2019) |
| **4. Propagate** | Traffic flows through Waveguides and Node Pipelines (Filters/Amps). | RF Propagation | Rappaport et al. (2013) |
| **5. Update** | Environment updates Queue lengths and Congestion levels. | Congestion Survey | Welzl (2005) |
| **6. Reward** | Reward is calculated based on Throughput, Latency, and QoS. | RL Rewards | Boyan (1994) |

## Key Research Interactions

### The Feedback Loop
In accordance with **Sun et al. (2019)**, the system maintains a feedback loop where the impact of an action (routing choice) is observed through changes in SINR and buffer occupancy. This "experience" is then stored and used to refine the neural network weights in the internal training step.

### Proactive Avoidance
By combining ML forecasting (**Ye et al.**) with SDN control (**Kreutz et al.**), PCAN-5G demonstrates proactive congestion avoidance. When the LSTM predicts a throughput breach, the DQN agent can shift traffic to less congested paths even before the physical queue builds up.

### RF-Aware Routing
Unlike standard ISP simulators, PCAN-5G routing Decisions consider the physical signal quality. If a path has high interference or low SNR as modeled in the `hardware` layer (**Rappaport et al.**), the routing cost significantly increases, forcing the agent to find higher-quality wireless alternatives.
