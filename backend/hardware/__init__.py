"""
PCAN-5G Hardware Abstraction Layer
===================================
Modular RF/electronic hardware simulation components for realistic 5G signal modeling.

Components:
    - Signal: Core signal dataclass (frequency, amplitude, phase, noise, SNR)
    - WaveguideLink: Link-level propagation model (attenuation, delay, interference)
    - BandpassFilter / NotchFilter: Frequency-domain filtering
    - Amplifier: Op-amp gain model with noise figure
    - Oscillator: Signal regeneration when amplitude drops below threshold
    - NodeSignalPipeline: Per-node processing chain (Filter → Amplifier → Oscillator)
"""

from hardware.signal_model import Signal
from hardware.waveguide import WaveguideLink
from hardware.filter import BandpassFilter, NotchFilter
from hardware.amplifier import Amplifier
from hardware.oscillator import Oscillator
from hardware.signal_pipeline import NodeSignalPipeline

__all__ = [
    'Signal',
    'WaveguideLink',
    'BandpassFilter',
    'NotchFilter',
    'Amplifier',
    'Oscillator',
    'NodeSignalPipeline',
]
