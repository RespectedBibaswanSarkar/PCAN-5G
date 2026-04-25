"""
SIGNAL PIPELINE — Per-Node Signal Processing Chain
Orchestrates: Input → Filter → Amplifier → Oscillator → Output
"""
import numpy as np
from typing import Dict, Optional, List
from hardware.signal_model import Signal
from hardware.filter import BandpassFilter, NotchFilter
from hardware.amplifier import Amplifier
from hardware.oscillator import Oscillator


class NodeSignalPipeline:
    """
    Per-node signal processing pipeline.

    Each node in the network has a configurable processing chain:
        Input Signal → BandpassFilter → NotchFilter → Amplifier → Oscillator → Output Signal

    The pipeline tracks per-stage metrics for visualization and analysis.

    Attributes:
        node_id: Network node identifier
        node_type: Type of node (CU, DU, RRH, UE)
        bandpass_filter: Bandpass filter instance
        notch_filter: Notch filter instance (optional)
        amplifier: Amplifier instance
        oscillator: Oscillator instance
    """

    # Default configurations per node type
    NODE_CONFIGS = {
        'CU': {
            'bandpass': {'center_freq': 3.5e9, 'bandwidth': 400e6, 'insertion_loss_db': 0.5},
            'amplifier': {'gain': 5.0, 'max_output': 3.0, 'noise_figure_db': 2.0},
            'oscillator': {'threshold': 0.05, 'target_amplitude': 1.0},
        },
        'DU': {
            'bandpass': {'center_freq': 3.5e9, 'bandwidth': 200e6, 'insertion_loss_db': 1.0},
            'amplifier': {'gain': 8.0, 'max_output': 4.0, 'noise_figure_db': 2.5},
            'oscillator': {'threshold': 0.08, 'target_amplitude': 0.9},
        },
        'RRH': {
            'bandpass': {'center_freq': 3.5e9, 'bandwidth': 100e6, 'insertion_loss_db': 1.5},
            'amplifier': {'gain': 15.0, 'max_output': 5.0, 'noise_figure_db': 3.0},
            'oscillator': {'threshold': 0.1, 'target_amplitude': 1.0},
        },
        'UE': {
            'bandpass': {'center_freq': 3.5e9, 'bandwidth': 100e6, 'insertion_loss_db': 2.0},
            'amplifier': {'gain': 10.0, 'max_output': 3.0, 'noise_figure_db': 4.0},
            'oscillator': {'threshold': 0.12, 'target_amplitude': 0.8},
        },
    }

    def __init__(
        self,
        node_id: int,
        node_type: str = 'UE',
        bandpass_filter: Optional[BandpassFilter] = None,
        notch_filter: Optional[NotchFilter] = None,
        amplifier: Optional[Amplifier] = None,
        oscillator: Optional[Oscillator] = None,
    ):
        """
        Initialize the signal processing pipeline for a node.

        Args:
            node_id: Node identifier
            node_type: Node type ('CU', 'DU', 'RRH', 'UE')
            bandpass_filter: Custom bandpass filter (None = use default for node type)
            notch_filter: Custom notch filter (None = no notch filter)
            amplifier: Custom amplifier (None = use default for node type)
            oscillator: Custom oscillator (None = use default for node type)
        """
        self.node_id = node_id
        self.node_type = node_type

        # Load defaults for this node type
        config = self.NODE_CONFIGS.get(node_type, self.NODE_CONFIGS['UE'])

        # Initialize components
        self.bandpass_filter = bandpass_filter or BandpassFilter(**config['bandpass'])
        self.notch_filter = notch_filter  # Optional, can be None
        self.amplifier = amplifier or Amplifier(**config['amplifier'])
        self.oscillator = oscillator or Oscillator(**config['oscillator'])

        # Pipeline stage metrics (updated after each process() call)
        self._stage_metrics: Dict[str, dict] = {}
        self._process_count = 0

    def process(self, signal: Signal) -> Signal:
        """
        Run a signal through the full processing pipeline.

        Pipeline stages:
            1. Input signal recorded
            2. Bandpass filter applied
            3. Notch filter applied (if configured)
            4. Amplifier applied
            5. Oscillator applied (regeneration if needed)
            6. Output signal recorded

        Args:
            signal: Input RF signal

        Returns:
            Processed output signal
        """
        self._process_count += 1
        stages = {}

        # Stage 0: Record input
        stages['input'] = signal.to_dict()

        # Stage 1: Bandpass filter
        signal = self.bandpass_filter.apply(signal)
        stages['after_filter'] = signal.to_dict()

        # Stage 2: Notch filter (optional)
        if self.notch_filter is not None:
            signal = self.notch_filter.apply(signal)
            stages['after_notch'] = signal.to_dict()

        # Stage 3: Amplifier
        signal = self.amplifier.amplify(signal)
        stages['after_amplifier'] = signal.to_dict()

        # Stage 4: Oscillator (conditional regeneration)
        signal = self.oscillator.regenerate(signal)
        stages['after_oscillator'] = signal.to_dict()
        stages['regenerated'] = self.oscillator.was_regenerated

        # Store stage metrics
        self._stage_metrics = stages

        return signal

    def inject_noise(self, signal: Signal, noise_power: float = 0.001) -> Signal:
        """
        Inject noise at this node (simulates local interference).

        Args:
            signal: Input signal
            noise_power: Additional noise power to inject

        Returns:
            Signal with added noise
        """
        return signal.add_noise(noise_power)

    @property
    def stage_metrics(self) -> Dict[str, dict]:
        """Get the per-stage metrics from the last process() call."""
        return self._stage_metrics

    @property
    def process_count(self) -> int:
        """Get total number of signals processed."""
        return self._process_count

    def get_current_signal_quality(self) -> dict:
        """
        Get a summary of current signal quality from the last processed signal.

        Returns:
            Dictionary with input/output SNR, amplitude, noise, and regeneration status
        """
        if not self._stage_metrics:
            return {
                'input_snr': 0, 'output_snr': 0,
                'input_amplitude': 0, 'output_amplitude': 0,
                'noise_level': 0, 'regenerated': False,
            }

        input_data = self._stage_metrics.get('input', {})
        output_data = self._stage_metrics.get('after_oscillator', {})

        return {
            'input_snr': input_data.get('snr', 0),
            'output_snr': output_data.get('snr', 0),
            'input_amplitude': input_data.get('amplitude', 0),
            'output_amplitude': output_data.get('amplitude', 0),
            'noise_level': output_data.get('noise', 0),
            'regenerated': self._stage_metrics.get('regenerated', False),
            'frequency_ghz': output_data.get('frequency_ghz', 3.5),
        }

    def to_dict(self) -> dict:
        """Serialize full pipeline state for API transmission."""
        result = {
            'node_id': self.node_id,
            'node_type': self.node_type,
            'process_count': self._process_count,
            'components': {
                'bandpass_filter': self.bandpass_filter.to_dict(),
                'notch_filter': self.notch_filter.to_dict() if self.notch_filter else None,
                'amplifier': self.amplifier.to_dict(),
                'oscillator': self.oscillator.to_dict(),
            },
            'stage_metrics': self._stage_metrics,
            'signal_quality': self.get_current_signal_quality(),
        }
        return result

    def __repr__(self) -> str:
        return (
            f"NodeSignalPipeline(node={self.node_id}, type={self.node_type}, "
            f"processed={self._process_count})"
        )


def create_pipeline_for_node(node_id: int, node_type: str) -> NodeSignalPipeline:
    """
    Factory function: create a default signal pipeline for a given node type.

    Args:
        node_id: Node identifier
        node_type: Node type ('CU', 'DU', 'RRH', 'UE')

    Returns:
        Configured NodeSignalPipeline
    """
    # RRH nodes get a notch filter to combat common interference
    notch = None
    if node_type == 'RRH':
        # Notch at a common interference frequency
        notch = NotchFilter(
            notch_freq=3.5e9 + 50e6,  # Slight offset from center
            notch_width=10e6,
            rejection_db=25.0,
        )

    return NodeSignalPipeline(
        node_id=node_id,
        node_type=node_type,
        notch_filter=notch,
    )
