# System Overview: PCAN-5G Research Platform

PCAN-5G (Predictive Congestion-Aware Network) is a research-oriented simulation framework designed to evaluate autonomous network management in 5G and beyond. The system integrates Software-Defined Networking (SDN) principles with Deep Reinforcement Learning (DRL) to solve the joint optimization challenge of dynamic routing and network slicing.

## 1. Research Context

The architecture of PCAN-5G is grounded in the evolution of programmable and intelligent networks:

### Software-Defined Networking (SDN)
Following the framework established by **Diego Kreutz et al.** in *“A Survey on Software-Defined Networking” (2015)*, PCAN-5G strictly decouples the **Control Plane** (implemented in `main.py` and `agent.py`) from the **Data Plane** (simulated in `environment.py`). This separation allows for centralized, AI-driven decision-making over a distributed infrastructure.

### Congestion Control
Managing network bottlenecks is a core objective of the platform. PCAN-5G incorporates fundamental trade-offs in throughput and latency as categorized by **Michael Welzl** in *“Network Congestion Control: A Survey” (2005)*. The reward function is specifically engineered to balance these competing metrics in real-time.

### Machine Learning in Wireless Systems
The high-fidelity nature of the simulation, including traffic forecasting, aligns with the visions of **H. Ye et al.** in *“The Role of Machine Learning in Future Wireless Networks” (2018)*. PCAN-5G uses ML not just as a lookup table, but as a predictive engine for proactive congestion avoidance.

## 2. Core System Objectives

The platform is designed to research three primary domains:

1.  **Adaptive Routing**: Navigating complex topologies to minimize end-to-end delay.
2.  **Network Slicing isolation**: Ensuring varied QoS requirements for eMBB, URLLC, and mMTC slices are met under varying loads.
3.  **Physical Layer Realism**: Accounting for RF impairments (SNR, interference, attenuation) through a digital twin approach.

## 3. Implementation Philosophy

PCAN-5G serves as a bridge between abstract mathematical models and practical network engineering. By implementing hardware abstractions (Filters, Amplifiers, Waveguides), the simulation moves beyond idealized "black-box" models to reflect the physical constraints defined in foundational 5G literature (Rappaport et al., 2013).
