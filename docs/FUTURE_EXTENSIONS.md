# Future Extensions (Theoretical)

The current implementation of PCAN-5G provides a robust base for several research extensions as suggested by advanced literature.

## ⚠️ No Code Changes Required
These extensions are documented here for research continuity and follow the academic trends in the provided papers.

| Potential Research Extension | Core Paper | Relation to PCAN-5G |
| :--- | :--- | :--- |
| **GNN Topology Generalization** | Mestres et al. (RouteNet) | Transition from the current `DiGraph` representation to Graph Neural Networks (GNN) to allow the agent to generalize to unseen topologies. |
| **AI-Native 6G Control** | IEEE 6G (2023-2024) | Moving from an "augmentative" AI approach to one where the entire control plane is natively managed by a distributed AI fabric. |
| **Cross-Silo Slice Optimization** | Zhou et al. (2017) | Implementing inter-slice resource sharing logic where under-utilized mMTC bandwidth can be dynamically harvested by eMBB slices. |
| **mmWave Signal Modeling** | Rappaport et al. (2013) | Extending the `hardware` module to specifically model the narrow-beamforming and high-attenuation properties of 28GHz bands. |
| **DRL Multi-Agent Systems** | Sun et al. (2019) | Replacing the centralized orchestrator with Multi-Agent Reinforcement Learning (MARL) for edge-based decision making. |

## Research Roadmap

1.  **Topological Awareness**: Leveraging graph embeddings (RouteNet) to improve the reward feedback from the environment.
2.  **Predictive Accuracy**: Enhancing the `CongestionPredictor` with Attention mechanisms or Transformers as hinted by modern wireless systems research (Ye et al., 2018).
3.  **Proactive Resilience**: Implementing proactive rerouting based on early signal degradation markers in the hardware layer, aligning with AI-Native 6G reliability standards.
