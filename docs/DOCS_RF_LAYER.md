# Documentation: Physical RF Signal Layer & Hardware Abstraction

This document provides a technical deep-dive into the high-fidelity Physical Layer (PHY) simulation implemented in PCAN-5G. It explains the Signal model, the hardware processing pipeline, and the waveguide propagation logic.

## 1. Core Signal Model (`hardware/signal_model.py`)

Every packet transmission in the "Realistic RF" mode is wrapped in a `Signal` object. Unlike logical packets, the Signal object tracks continuous wave properties:

- **Frequency**: Center frequency in Hz (e.g., 3.5 GHz for n78 band).
- **Amplitude**: Voltage level, used to calculate power and attenuation.
- **Phase**: Tracking phase shifts for future MIMO/interference modeling.
- **Noise Layer**: Spectral noise density applied across stages.
- **SNR**: Real-time Signal-to-Noise Ratio computed per hop.

## 2. Hardware Processing Pipeline (`hardware/signal_pipeline.py`)

Each node in the 5G topology (DU, RRH, UE) can be configured with a custom signal processing chain. The default pipeline for an RRH node follows this sequence:

### A. Bandpass Filter (`filter.py`)
Attenuates frequencies outside the allocated bandwidth. Reduces out-of-band noise but introduces insertion loss.

### B. Amplifier (`amplifier.py`)
Simulates an Operational Amplifier with:
- **Gain**: Configurable boost (e.g., 20dB).
- **Noise Figure**: Internal noise added by the amplification process.
- **Saturation**: Realistic clipping when output power exceeds hardware limits.

### C. Oscillator / Regenerator (`oscillator.py`)
A critical component that regenerates the signal if the amplitude falls below a specific threshold, simulating active repeaters or C-RAN signal conditioning.

## 3. Waveguide Propagation Model (`hardware/waveguide.py`)

Links between nodes are modeled as `WaveguideLink` objects. They simulate realistic medium impairments:

- **Distance-based Attenuation**: Loss scales with the distance between nodes.
- **Interference**: Cross-talk and background RF interference derived from network-wide activity.
- **Propagation Delay**: Calculated based on the speed of light in the medium (Fiber vs. Wireless).

## 4. Integration with FiveGEnvironment

When `simulation_mode='realistic_rf'`, the environment:
1.  Converts the destination into a physical signal.
2.  Propagates it through the graph links (Waveguides).
3.  Processes it at each intermediate node (Pipelines).
4.  Calculates the **Final SNR** at the destination.
5.  If the SNR is too low, the effective capacity of the link is dropped, potentially leading to packet loss or increased latency.

## 5. Visualizing the Signal

The frontend dashboard provides a live view of this process through:
- **Waveguide Pipe Animation**: Showing signal flow through links.
- **Circuit Block Nodes**: Representing physical nodes with internal metrics.
- **Signal Pipeline Graph**: A stage-by-stage diagram of the signal's properties (Amplitude/SNR) as it moves through a node.
