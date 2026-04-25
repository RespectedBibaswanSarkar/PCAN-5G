# Module to Research Mapping

This document maps specific source code modules in the PCAN-5G repository to their corresponding academic domains and foundational research papers.

## Backend Modules

### 1. Agent Logic (`backend/agent.py`)
*   **Purpose**: Implements the Deep Q-Network (DQN) and LSTM components for routing and congestion prediction.
*   **Mapped Research**: Reinforcement Learning (RL) & Deep Reinforcement Learning (DRL).
*   **Linked Papers**:
    *   *“Q-Routing: A Reinforcement Learning Approach to Routing”* (Boyan & Littman, 1994)
    *   *“Deep Reinforcement Learning for Networking: A Survey”* (Sun et al., 2019)
*   **Connection**: The `XDQNAgent` extends the original concept of Q-Routing by using deep neural networks to handle large state spaces (SINR, queue lengths, slice requirements).

### 2. Network Environment (`backend/environment.py`)
*   **Purpose**: Manages the C-RAN topology, network slicing configuration, and core simulation loop.
*   **Mapped Research**: Network Slicing & Graph Modeling.
*   **Linked Papers**:
    *   *“Network Slicing for 5G”* (Zhou et al., 2017)
    *   *“RouteNet: Leveraging Graph Neural Networks for Network Modeling”* (Mestres et al., 2019)
*   **Connection**: The slice definitions (`eMBB`, `URLLC`, `mMTC`) and the graph-based traffic propagation directly reflect the slicing and graph-native modeling architectures discussed in these works.

### 3. Hardware Abstraction (`backend/hardware/`)
*   **Purpose**: Simulates Physical Layer (PHY) components including filters, amplifiers, oscillators, and waveguides.
*   **Mapped Research**: 5G Wireless Communication Architecture.
*   **Linked Papers**:
    *   *“5G Wireless Communication Systems: Prospects and Challenges”* (Rappaport et al., 2013)
*   **Connection**: This module transforms a logical network into a physical one by implementing the signal degradation models (attenuation, interference) necessary for realistic 5G simulation.

### 4. Control Plane API (`backend/main.py`)
*   **Purpose**: Provides the REST/WebSocket interface for managing the simulation and broadcasting metrics.
*   **Mapped Research**: Software-Defined Networking (SDN).
*   **Linked Papers**:
    *   *“A Survey on Software-Defined Networking”* (Kreutz et al., 2015)
*   **Connection**: Acts as the SDN controller, orchestrating the interaction between the user (UI), the management agent, and the underlying data plane environment.

## Logic Components

### Traffic Prediction (`CongestionPredictor` in `agent.py`)
*   **Mapped Research**: ML for Congestion Prediction.
*   **Linked Papers**:
    *   *“The Role of Machine Learning in Future Wireless Networks”* (Ye et al., 2018)
*   **Connection**: Implements a time-series forecasting model to anticipate traffic spikes, a key requirement for future "AI-native" networks.
