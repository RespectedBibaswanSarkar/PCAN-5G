"""
OSCILLATOR MODULE — Signal Regeneration and Frequency Resynchronization
Regenerates signals when amplitude drops below threshold.
"""
import numpy as np
from hardware.signal_model import Signal


class Oscillator:
    """
    Oscillator / signal regenerator module.

    When the incoming signal amplitude drops below a configurable threshold,
    the oscillator regenerates it to a target amplitude with clean noise floor.
    Optionally resynchronizes the carrier frequency.

    This models real-world repeaters and signal regenerators in 5G networks.

    Attributes:
        threshold: Minimum amplitude before regeneration triggers
        target_amplitude: Regenerated signal amplitude
        target_frequency: Optional frequency to resync to (None = keep original)
        regeneration_noise: Residual noise floor after regeneration
        enabled: Whether the oscillator is active
    """

    def __init__(
        self,
        threshold: float = 0.1,
        target_amplitude: float = 1.0,
        target_frequency: float = None,
        regeneration_noise: float = 0.0005,
        enabled: bool = True,
    ):
        """
        Initialize oscillator.

        Args:
            threshold: Amplitude threshold for triggering regeneration
            target_amplitude: Output amplitude after regeneration
            target_frequency: Frequency to sync to (None = preserve input frequency)
            regeneration_noise: Noise floor of regenerated signal
            enabled: Whether oscillator is active
        """
        self.threshold = max(0.0, threshold)
        self.target_amplitude = max(0.01, target_amplitude)
        self.target_frequency = target_frequency
        self.regeneration_noise = max(1e-6, regeneration_noise)
        self.enabled = enabled

        # Tracking
        self._regeneration_count = 0
        self._last_regenerated = False

    def regenerate(self, signal: Signal) -> Signal:
        """
        Process signal through the oscillator.

        If amplitude < threshold, regenerate the signal with target amplitude
        and clean noise floor. Otherwise, pass through unchanged.

        Args:
            signal: Input signal

        Returns:
            Output signal (regenerated or passed through)
        """
        if not self.enabled:
            self._last_regenerated = False
            return signal

        if signal.amplitude < self.threshold:
            # Regenerate: restore amplitude, reset noise, optionally resync frequency
            self._regeneration_count += 1
            self._last_regenerated = True

            output_freq = (
                self.target_frequency if self.target_frequency is not None
                else signal.frequency
            )

            return Signal(
                frequency=output_freq,
                amplitude=self.target_amplitude,
                phase=0.0,  # Phase reset on regeneration
                noise=self.regeneration_noise,
            )
        else:
            # Pass through — signal is strong enough
            self._last_regenerated = False
            return signal

    @property
    def was_regenerated(self) -> bool:
        """Check if the last signal processed was regenerated."""
        return self._last_regenerated

    @property
    def total_regenerations(self) -> int:
        """Get total count of regenerations performed."""
        return self._regeneration_count

    def reset_counter(self):
        """Reset regeneration counter."""
        self._regeneration_count = 0

    def set_enabled(self, enabled: bool):
        """Enable or disable the oscillator."""
        self.enabled = enabled

    def to_dict(self) -> dict:
        """Serialize oscillator state for API transmission."""
        return {
            'threshold': round(self.threshold, 4),
            'target_amplitude': round(self.target_amplitude, 4),
            'target_frequency_ghz': (
                round(self.target_frequency / 1e9, 3)
                if self.target_frequency else None
            ),
            'regeneration_noise': round(self.regeneration_noise, 6),
            'enabled': self.enabled,
            'regeneration_count': self._regeneration_count,
            'last_regenerated': self._last_regenerated,
        }

    def __repr__(self) -> str:
        return (
            f"Oscillator(threshold={self.threshold:.3f}, "
            f"target_amp={self.target_amplitude:.2f}, "
            f"regens={self._regeneration_count}, "
            f"{'ON' if self.enabled else 'OFF'})"
        )
