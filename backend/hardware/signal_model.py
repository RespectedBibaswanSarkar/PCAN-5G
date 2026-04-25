"""
SIGNAL MODEL — Core Signal Dataclass for Physical Layer Simulation
Represents an RF signal with frequency, amplitude, phase, noise, and SNR.
"""
import numpy as np
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Signal:
    """
    Represents a physical RF signal in the PCAN-5G simulation.

    Attributes:
        frequency: Carrier frequency in Hz (e.g., 3.5e9 for 5G n78 band)
        amplitude: Signal amplitude in Volts (linear scale)
        phase: Signal phase in radians [0, 2π)
        noise: Noise power in Watts
        snr: Signal-to-noise ratio in dB (derived from amplitude and noise)
    """
    frequency: float = 3.5e9       # Default: 5G NR n78 band (3.5 GHz)
    amplitude: float = 1.0         # Volts (normalized)
    phase: float = 0.0             # Radians
    noise: float = 0.001           # Noise power (Watts)
    snr: float = field(init=False) # Computed from amplitude/noise

    def __post_init__(self):
        """Compute SNR after initialization."""
        self.snr = self._compute_snr()

    def _compute_snr(self) -> float:
        """
        Compute Signal-to-Noise Ratio in dB.
        SNR(dB) = 10 * log10(signal_power / noise_power)
        """
        signal_power = self.amplitude ** 2
        if self.noise <= 0:
            return 100.0  # Effectively infinite SNR
        return float(10.0 * np.log10(signal_power / (self.noise + 1e-15)))

    def recalculate_snr(self):
        """Recalculate SNR from current amplitude and noise values."""
        self.snr = self._compute_snr()

    def attenuate(self, factor: float) -> 'Signal':
        """
        Apply attenuation to the signal.

        Args:
            factor: Attenuation factor (0–1). 1 = no attenuation, 0 = full loss.

        Returns:
            New Signal with attenuated amplitude.
        """
        new_amplitude = self.amplitude * max(0.0, min(1.0, factor))
        return Signal(
            frequency=self.frequency,
            amplitude=new_amplitude,
            phase=self.phase,
            noise=self.noise,
        )

    def add_noise(self, additional_noise: float) -> 'Signal':
        """
        Add noise to the signal.

        Args:
            additional_noise: Additional noise power to add.

        Returns:
            New Signal with increased noise.
        """
        return Signal(
            frequency=self.frequency,
            amplitude=self.amplitude,
            phase=self.phase,
            noise=self.noise + max(0.0, additional_noise),
        )

    def shift_phase(self, delta_radians: float) -> 'Signal':
        """
        Apply phase shift.

        Args:
            delta_radians: Phase shift in radians.

        Returns:
            New Signal with shifted phase.
        """
        new_phase = (self.phase + delta_radians) % (2 * np.pi)
        return Signal(
            frequency=self.frequency,
            amplitude=self.amplitude,
            phase=new_phase,
            noise=self.noise,
        )

    def to_dict(self) -> dict:
        """Serialize signal to dictionary for API/WebSocket transmission."""
        return {
            'frequency': self.frequency,
            'frequency_ghz': self.frequency / 1e9,
            'amplitude': round(self.amplitude, 6),
            'phase': round(self.phase, 4),
            'noise': round(self.noise, 6),
            'snr': round(self.snr, 2),
        }

    @staticmethod
    def default_5g(band: str = 'n78') -> 'Signal':
        """
        Create a default 5G NR signal for a given band.

        Args:
            band: 5G NR band identifier ('n78', 'n258', 'n41')

        Returns:
            Signal configured for the specified band.
        """
        bands = {
            'n78':  {'freq': 3.5e9,  'amp': 1.0,  'noise': 0.001},   # Sub-6 GHz
            'n258': {'freq': 26.5e9, 'amp': 0.5,  'noise': 0.005},   # mmWave
            'n41':  {'freq': 2.5e9,  'amp': 1.2,  'noise': 0.0008},  # Mid-band
        }
        cfg = bands.get(band, bands['n78'])
        return Signal(
            frequency=cfg['freq'],
            amplitude=cfg['amp'],
            phase=0.0,
            noise=cfg['noise'],
        )

    @staticmethod
    def from_phy_metrics(rsrp: float, sinr: float, frequency: float = 3.5e9) -> 'Signal':
        """
        Create a Signal from existing PHY layer metrics.

        Args:
            rsrp: Reference Signal Received Power (dBm)
            sinr: Signal-to-Interference-plus-Noise Ratio (dB)
            frequency: Carrier frequency in Hz

        Returns:
            Signal approximated from PHY metrics.
        """
        # Convert RSRP (dBm) to amplitude (normalized, 0–1 range)
        # RSRP typically ranges from -140 to -40 dBm
        amplitude = max(0.01, min(1.5, 10 ** ((rsrp + 90) / 40)))

        # Derive noise from SINR: noise = signal_power / 10^(SINR/10)
        signal_power = amplitude ** 2
        noise = signal_power / (10 ** (sinr / 10) + 1e-15)

        return Signal(
            frequency=frequency,
            amplitude=amplitude,
            phase=np.random.uniform(0, 2 * np.pi),
            noise=max(1e-6, noise),
        )

    def __repr__(self) -> str:
        return (
            f"Signal(freq={self.frequency/1e9:.2f}GHz, "
            f"amp={self.amplitude:.4f}V, "
            f"SNR={self.snr:.1f}dB, "
            f"noise={self.noise:.6f})"
        )
