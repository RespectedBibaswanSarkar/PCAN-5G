"""
RF FILTER MODULE — Bandpass and Notch Filter Simulation
Implements frequency-domain filtering for signal processing pipeline.
"""
import numpy as np
from typing import Optional
from hardware.signal_model import Signal


class BandpassFilter:
    """
    Bandpass filter that allows signals within a specified frequency range
    and attenuates signals outside that range.

    Models a realistic RF bandpass filter with configurable passband,
    insertion loss, and out-of-band rejection.

    Attributes:
        center_freq: Center frequency of the passband (Hz)
        bandwidth: Passband width (Hz)
        insertion_loss_db: In-band insertion loss (dB), typically 0.5–3 dB
        rejection_db: Out-of-band rejection (dB), typically 20–60 dB
    """

    def __init__(
        self,
        center_freq: float = 3.5e9,
        bandwidth: float = 100e6,
        insertion_loss_db: float = 1.0,
        rejection_db: float = 40.0,
    ):
        """
        Initialize bandpass filter.

        Args:
            center_freq: Center frequency (Hz)
            bandwidth: Passband width (Hz)
            insertion_loss_db: In-band loss (dB)
            rejection_db: Out-of-band rejection (dB)
        """
        self.center_freq = center_freq
        self.bandwidth = bandwidth
        self.insertion_loss_db = max(0.0, insertion_loss_db)
        self.rejection_db = max(0.0, rejection_db)

        # Derived passband edges
        self.freq_low = center_freq - bandwidth / 2
        self.freq_high = center_freq + bandwidth / 2

    def apply(self, signal: Signal) -> Signal:
        """
        Apply bandpass filter to a signal.

        If the signal frequency is within the passband, apply minimal insertion loss.
        If outside, apply heavy rejection attenuation.
        Also reduces out-of-band noise.

        Args:
            signal: Input signal

        Returns:
            Filtered output signal
        """
        in_band = self.freq_low <= signal.frequency <= self.freq_high

        if in_band:
            # In-band: minimal insertion loss
            loss_factor = 10 ** (-self.insertion_loss_db / 20)
            new_amplitude = signal.amplitude * loss_factor

            # Filter reduces out-of-band noise (noise reduction proportional to selectivity)
            noise_reduction = 0.3  # 30% noise reduction from filtering
            new_noise = signal.noise * (1.0 - noise_reduction)
        else:
            # Out-of-band: heavy rejection
            rejection_factor = 10 ** (-self.rejection_db / 20)
            new_amplitude = signal.amplitude * rejection_factor

            # No noise benefit for rejected signals
            new_noise = signal.noise

        return Signal(
            frequency=signal.frequency,
            amplitude=max(1e-8, new_amplitude),
            phase=signal.phase,
            noise=max(1e-8, new_noise),
        )

    def is_in_band(self, frequency: float) -> bool:
        """Check if a frequency falls within the passband."""
        return self.freq_low <= frequency <= self.freq_high

    def get_attenuation_at_freq(self, frequency: float) -> float:
        """
        Get attenuation in dB at a specific frequency.

        Args:
            frequency: Frequency to query (Hz)

        Returns:
            Attenuation in dB (0 = no loss, positive = loss)
        """
        if self.is_in_band(frequency):
            return self.insertion_loss_db

        # Simple roll-off model: attenuation increases with distance from passband
        distance_from_band = min(
            abs(frequency - self.freq_low),
            abs(frequency - self.freq_high),
        )
        normalized_distance = distance_from_band / self.bandwidth
        return min(self.rejection_db, self.insertion_loss_db + normalized_distance * self.rejection_db)

    def to_dict(self) -> dict:
        """Serialize filter state for API transmission."""
        return {
            'type': 'bandpass',
            'center_freq_ghz': round(self.center_freq / 1e9, 3),
            'bandwidth_mhz': round(self.bandwidth / 1e6, 1),
            'freq_low_ghz': round(self.freq_low / 1e9, 3),
            'freq_high_ghz': round(self.freq_high / 1e9, 3),
            'insertion_loss_db': round(self.insertion_loss_db, 2),
            'rejection_db': round(self.rejection_db, 1),
        }

    def __repr__(self) -> str:
        return (
            f"BandpassFilter(center={self.center_freq/1e9:.2f}GHz, "
            f"BW={self.bandwidth/1e6:.0f}MHz, "
            f"IL={self.insertion_loss_db:.1f}dB)"
        )


class NotchFilter:
    """
    Notch (band-reject) filter that blocks signals at a specific interference frequency.

    Used to remove known interference sources without affecting the desired signal.

    Attributes:
        notch_freq: Center frequency of the rejected band (Hz)
        notch_width: Width of the rejected band (Hz)
        rejection_db: Depth of the notch (dB)
    """

    def __init__(
        self,
        notch_freq: float = 3.5e9,
        notch_width: float = 5e6,
        rejection_db: float = 30.0,
    ):
        """
        Initialize notch filter.

        Args:
            notch_freq: Interference frequency to reject (Hz)
            notch_width: Width of rejection band (Hz)
            rejection_db: Rejection depth (dB)
        """
        self.notch_freq = notch_freq
        self.notch_width = notch_width
        self.rejection_db = max(0.0, rejection_db)

        # Notch band edges
        self.notch_low = notch_freq - notch_width / 2
        self.notch_high = notch_freq + notch_width / 2

    def apply(self, signal: Signal) -> Signal:
        """
        Apply notch filter to a signal.

        If the signal frequency is in the notch band, apply heavy rejection.
        Otherwise, pass through with minimal effect.
        The notch filter always reduces interference-related noise.

        Args:
            signal: Input signal

        Returns:
            Filtered output signal
        """
        in_notch = self.notch_low <= signal.frequency <= self.notch_high

        if in_notch:
            # Signal is at the interference frequency — reject it
            rejection_factor = 10 ** (-self.rejection_db / 20)
            new_amplitude = signal.amplitude * rejection_factor
        else:
            # Signal passes through unaffected
            new_amplitude = signal.amplitude

        # Notch filter reduces interference noise regardless
        # (it removes the narrowband interference component)
        interference_noise_reduction = 0.2  # 20% noise reduction
        new_noise = signal.noise * (1.0 - interference_noise_reduction)

        return Signal(
            frequency=signal.frequency,
            amplitude=max(1e-8, new_amplitude),
            phase=signal.phase,
            noise=max(1e-8, new_noise),
        )

    def is_in_notch(self, frequency: float) -> bool:
        """Check if a frequency falls within the notch band."""
        return self.notch_low <= frequency <= self.notch_high

    def to_dict(self) -> dict:
        """Serialize filter state for API transmission."""
        return {
            'type': 'notch',
            'notch_freq_ghz': round(self.notch_freq / 1e9, 3),
            'notch_width_mhz': round(self.notch_width / 1e6, 2),
            'rejection_db': round(self.rejection_db, 1),
        }

    def __repr__(self) -> str:
        return (
            f"NotchFilter(notch={self.notch_freq/1e9:.3f}GHz, "
            f"width={self.notch_width/1e6:.1f}MHz, "
            f"depth={self.rejection_db:.0f}dB)"
        )
