"""
AMPLIFIER MODULE — Op-Amp Gain Model with Noise Figure
Simulates signal amplification with realistic gain limits and noise amplification.
"""
import numpy as np
from hardware.signal_model import Signal


class Amplifier:
    """
    Operational amplifier model for signal boosting in the processing pipeline.

    Models key real-world amplifier behaviors:
    - Linear gain up to saturation point
    - Noise figure (amplifier adds its own noise)
    - Gain compression at high input levels

    Attributes:
        gain: Linear gain factor (e.g., 10 = 20dB gain)
        max_output: Maximum output amplitude (saturation limit)
        noise_figure_db: Noise figure in dB (noise added by amplifier)
        enabled: Whether the amplifier is active
    """

    def __init__(
        self,
        gain: float = 10.0,
        max_output: float = 5.0,
        noise_figure_db: float = 3.0,
        enabled: bool = True,
    ):
        """
        Initialize amplifier.

        Args:
            gain: Linear voltage gain (e.g., 10 = 20dB)
            max_output: Saturation output amplitude
            noise_figure_db: Noise contributed by amplifier (dB)
            enabled: Whether amplifier is active
        """
        self.gain = max(1.0, gain)
        self.max_output = max(0.1, max_output)
        self.noise_figure_db = max(0.0, noise_figure_db)
        self.enabled = enabled

        # Derived: noise factor (linear)
        self.noise_factor = 10 ** (self.noise_figure_db / 10)

    def amplify(self, signal: Signal) -> Signal:
        """
        Amplify a signal.

        output_amplitude = min(input_amplitude × gain, max_output)
        output_noise = input_noise × gain² + amplifier_noise

        Args:
            signal: Input signal

        Returns:
            Amplified output signal
        """
        if not self.enabled:
            return signal

        # Apply gain with saturation
        raw_output = signal.amplitude * self.gain
        output_amplitude = min(raw_output, self.max_output)

        # Gain compression indicator (for metrics)
        is_saturated = raw_output > self.max_output

        # Noise amplification: noise power scales with gain²
        # Plus amplifier's own noise contribution
        amplified_noise = signal.noise * (self.gain ** 2)
        amplifier_self_noise = signal.noise * (self.noise_factor - 1)
        output_noise = amplified_noise + amplifier_self_noise

        return Signal(
            frequency=signal.frequency,
            amplitude=max(1e-8, output_amplitude),
            phase=signal.phase,
            noise=max(1e-8, output_noise),
        )

    def get_gain_db(self) -> float:
        """Get gain in dB."""
        return 20 * np.log10(self.gain)

    def set_gain(self, gain: float):
        """Update gain value."""
        self.gain = max(1.0, gain)

    def set_enabled(self, enabled: bool):
        """Enable or disable the amplifier."""
        self.enabled = enabled

    def to_dict(self) -> dict:
        """Serialize amplifier state for API transmission."""
        return {
            'gain_linear': round(self.gain, 2),
            'gain_db': round(self.get_gain_db(), 1),
            'max_output': round(self.max_output, 2),
            'noise_figure_db': round(self.noise_figure_db, 1),
            'noise_factor': round(self.noise_factor, 3),
            'enabled': self.enabled,
        }

    def __repr__(self) -> str:
        return (
            f"Amplifier(gain={self.gain:.1f}x/{self.get_gain_db():.0f}dB, "
            f"max={self.max_output:.1f}, NF={self.noise_figure_db:.1f}dB, "
            f"{'ON' if self.enabled else 'OFF'})"
        )
