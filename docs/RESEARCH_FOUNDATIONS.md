# Research Foundations

This document provides a deep dive into the theoretical pillars upon which PCAN-5G is built, referencing the core provided literature.

## 1. Software-Defined Networking (SDN)
The platform follows the architecture proposed by **Diego Kreutz et al. (2015)**. By centralizing the routing logic in a DQN agent, PCAN-5G demonstrates:
*   **Vertical Decoupling**: The control logic is separate from the forwarding elements (nodes).
*   **Logically Centralized Control**: The DQN agent maintains a global state of the network (SINR, metrics).
*   **Programmability**: Network behavior can be modified through reward function tuning without hardware reconfiguration.

## 2. Congestion Control Theory
PCAN-5G addresses the fundamental trade-offs identified by **Michael Welzl (2005)**. The environment models:
*   **Queueing Delay**: Nodes maintain queue lengths that influence end-to-end latency.
*   **Packet Loss**: Congestion-induced packet drops are simulated when traffic load exceeds allocated bandwidth.
*   **Feedback Loops**: The agent receives reward signals based on these metrics, creating a closed-loop control system.

## 3. 5G Architecture & Slicing
The heterogeneous nature of the PCAN-5G topology mirrors the definitions from **Theodore S. Rappaport et al. (2013)** and **Xiaofei Zhou et al. (2017)**:
*   **C-RAN Topology**: Modeling Core (CU), Distributed (DU), and Remote Radio Head (RRH) units.
*   **Slicing Profiles**: 
    *   **eMBB**: Focused on high throughput.
    *   **URLLC**: Focused on ultra-low latency.
    *   **mMTC**: Focused on massive scale and baseline connectivity.

## 4. Reinforcement Learning for Routing
The routing mechanism is an evolution of **Boyan & Littman's Q-Routing (1994)**. While traditional Q-Routing used a simple Q-table, PCAN-5G utilizes **Deep Reinforcement Learning (Sun et al., 2019)**:
*   **State Space**: Incorporates continuous PHY metrics like SINR.
*   **Action Space**: Jointly optimizes routing paths and slice bandwidth.
*   **Exploration-Exploitation**: Balances testing new paths with exploiting known efficient routes.

## 5. Machine Learning for Predictive Simulation
By integrating an LSTM module, the platform adopts the "ML for prediction" paradigm suggested by **H. Ye et al. (2018)**. This allows the system to transition from reactive management to predictive congestion avoidance.
