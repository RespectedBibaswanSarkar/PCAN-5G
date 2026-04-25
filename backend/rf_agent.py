"""
RF-AWARE AGENT — Extended DQN Agent with Signal Quality Awareness
Wraps XDQNAgent to handle the extended state vector in realistic_rf mode.
"""
import torch
import numpy as np
from agent import XDQNAgent


class RFAwareAgent(XDQNAgent):
    """
    Extended DQN agent that handles the larger state vector from realistic_rf mode.

    In ideal mode: state_dim = 21 (original)
    In realistic_rf mode: state_dim = 28 (21 base + 7 RF features)

    Same action space (9 actions) and same training logic.
    The additional RF features (SNR, interference, link quality, noise, etc.)
    give the agent richer information for routing and resource allocation decisions.
    """

    def __init__(self, state_dim: int = 28, action_dim: int = 9):
        """
        Initialize RF-aware agent.

        Args:
            state_dim: State vector dimension (28 for RF mode)
            action_dim: Number of actions (9, same as base agent)
        """
        super().__init__(state_dim, action_dim)

        # RF-specific tracking
        self.snr_history = []
        self.interference_history = []

    def act_with_rf_awareness(self, state: np.ndarray, snr_threshold: float = 5.0) -> int:
        """
        Act with optional RF-aware override.

        If the average SNR in the state is critically low, bias toward
        conservative actions (middle action = maintain current allocation).

        Args:
            state: Current state vector (includes RF features at the end)
            snr_threshold: SNR level below which conservative action is preferred

        Returns:
            Selected action index
        """
        # Extract RF features from extended state (last 7 features)
        if len(state) > 21:
            avg_link_snr = state[21]    # Average link SNR
            min_snr = state[25]         # Minimum SNR across links
            max_interference = state[26] # Maximum interference

            # Track for analysis
            self.snr_history.append(float(avg_link_snr))
            self.interference_history.append(float(max_interference))

            # Emergency override: if SNR critically low, choose safe action
            if min_snr < snr_threshold and np.random.rand() < 0.3:
                # Action 4 = no routing change, no BW change (safe)
                return 4

        # Default: use standard epsilon-greedy DQN action selection
        return self.act(state)

    def get_rf_stats(self) -> dict:
        """
        Get RF-related statistics from the agent's tracking.

        Returns:
            Dictionary with SNR and interference statistics
        """
        if not self.snr_history:
            return {
                'avg_snr': 0, 'min_snr': 0, 'max_snr': 0,
                'avg_interference': 0, 'max_interference': 0,
                'samples': 0,
            }

        return {
            'avg_snr': float(np.mean(self.snr_history[-100:])),
            'min_snr': float(np.min(self.snr_history[-100:])),
            'max_snr': float(np.max(self.snr_history[-100:])),
            'avg_interference': float(np.mean(self.interference_history[-100:])),
            'max_interference': float(np.max(self.interference_history[-100:])),
            'samples': len(self.snr_history),
        }

    def reset_rf_stats(self):
        """Reset RF tracking data."""
        self.snr_history.clear()
        self.interference_history.clear()
