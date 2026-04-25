"""
WAVEGUIDE / LINK MODEL — Physical Link Propagation Simulation
Extends network edges with attenuation, bandwidth, propagation delay, and interference.
"""
import numpy as np
from typing import Dict, Optional, Tuple
from hardware.signal_model import Signal


class WaveguideLink:
    """
    Models a physical RF link (waveguide) between two network nodes.
    Applies signal degradation based on distance, frequency, and environmental factors.

    Attributes:
        source: Source node ID
        target: Target node ID
        distance_km: Physical distance between nodes (km)
        attenuation_db_per_km: Signal attenuation rate (dB/km)
        bandwidth_hz: Available channel bandwidth (Hz)
        propagation_delay_ms: Signal propagation delay (ms)
        interference_factor: External interference level (0–1)
    """

    # Default attenuation rates for different link types (dB/km)
    ATTENUATION_PROFILES = {
        'fiber':     0.2,    # Fiber optic (CU-DU links)
        'microwave': 2.0,    # Microwave backhaul (DU-RRH)
        'mmwave':    10.0,   # mmWave air interface
        'sub6ghz':   5.0,    # Sub-6 GHz air interface (RRH-UE)
    }

    def __init__(
        self,
        source: int,
        target: int,
        distance_km: float = 1.0,
        link_type: str = 'sub6ghz',
        attenuation_db_per_km: Optional[float] = None,
        bandwidth_hz: float = 100e6,
        interference_factor: float = 0.0,
    ):
        """
        Initialize a waveguide link.

        Args:
            source: Source node ID
            target: Target node ID
            distance_km: Physical distance (km)
            link_type: Link type preset ('fiber', 'microwave', 'mmwave', 'sub6ghz')
            attenuation_db_per_km: Custom attenuation rate (overrides link_type default)
            bandwidth_hz: Channel bandwidth in Hz
            interference_factor: External interference (0 = none, 1 = severe)
        """
        self.source = source
        self.target = target
        self.distance_km = max(0.001, distance_km)
        self.link_type = link_type
        self.bandwidth_hz = bandwidth_hz
        self.interference_factor = max(0.0, min(1.0, interference_factor))

        # Use custom attenuation or default from profile
        if attenuation_db_per_km is not None:
            self.attenuation_db_per_km = attenuation_db_per_km
        else:
            self.attenuation_db_per_km = self.ATTENUATION_PROFILES.get(
                link_type, self.ATTENUATION_PROFILES['sub6ghz']
            )

        # Propagation delay: distance / speed_of_light (+ processing overhead)
        speed_of_light_km_per_ms = 299.792  # km/ms
        self.propagation_delay_ms = (self.distance_km / speed_of_light_km_per_ms) + 0.1

        # Dynamic state
        self._current_load = 0.0  # 0–1

    def propagate(self, signal: Signal) -> Signal:
        """
        Propagate a signal through this waveguide link.
        Applies attenuation, noise from interference, and phase shift from delay.

        Args:
            signal: Input signal

        Returns:
            Degraded output signal after propagation
        """
        # 1. Distance-based attenuation
        total_attenuation_db = self.attenuation_db_per_km * self.distance_km
        attenuation_factor = 10 ** (-total_attenuation_db / 20)  # Convert dB to linear (amplitude)
        new_amplitude = signal.amplitude * attenuation_factor

        # 2. Frequency-dependent loss (higher freq = more loss)
        freq_factor = 1.0 - min(0.3, (signal.frequency / 100e9))  # mmWave loses more
        new_amplitude *= freq_factor

        # 3. Interference-induced noise
        interference_noise = self.interference_factor * 0.01 * (signal.amplitude ** 2)

        # 4. Thermal noise (distance-dependent)
        thermal_noise = 1e-4 * self.distance_km

        new_noise = signal.noise + interference_noise + thermal_noise

        # 5. Phase shift from propagation delay
        wavelength = 3e8 / signal.frequency  # meters
        distance_m = self.distance_km * 1000
        phase_shift = (2 * np.pi * distance_m / wavelength) % (2 * np.pi)

        return Signal(
            frequency=signal.frequency,
            amplitude=max(1e-6, new_amplitude),
            phase=(signal.phase + phase_shift) % (2 * np.pi),
            noise=new_noise,
        )

    def get_total_attenuation_db(self) -> float:
        """Get total attenuation in dB for this link."""
        return self.attenuation_db_per_km * self.distance_km

    def set_interference(self, factor: float):
        """
        Dynamically update interference factor.

        Args:
            factor: Interference level (0–1)
        """
        self.interference_factor = max(0.0, min(1.0, factor))

    def set_load(self, load: float):
        """
        Update current link load (for congestion-aware metrics).

        Args:
            load: Load fraction (0–1)
        """
        self._current_load = max(0.0, min(1.0, load))

    def get_quality_score(self) -> float:
        """
        Compute a normalized link quality score (0–1).
        Higher is better. Considers attenuation, interference, and load.
        """
        attenuation_score = max(0.0, 1.0 - self.get_total_attenuation_db() / 30.0)
        interference_score = 1.0 - self.interference_factor
        load_score = 1.0 - self._current_load
        return (attenuation_score * 0.4 + interference_score * 0.3 + load_score * 0.3)

    def to_dict(self) -> dict:
        """Serialize waveguide state for API/WebSocket transmission."""
        return {
            'source': self.source,
            'target': self.target,
            'distance_km': round(self.distance_km, 3),
            'link_type': self.link_type,
            'attenuation_db_per_km': round(self.attenuation_db_per_km, 2),
            'total_attenuation_db': round(self.get_total_attenuation_db(), 2),
            'bandwidth_hz': self.bandwidth_hz,
            'bandwidth_mhz': self.bandwidth_hz / 1e6,
            'propagation_delay_ms': round(self.propagation_delay_ms, 4),
            'interference_factor': round(self.interference_factor, 3),
            'quality_score': round(self.get_quality_score(), 3),
        }

    def __repr__(self) -> str:
        return (
            f"WaveguideLink({self.source}→{self.target}, "
            f"type={self.link_type}, "
            f"dist={self.distance_km:.2f}km, "
            f"atten={self.get_total_attenuation_db():.1f}dB, "
            f"intf={self.interference_factor:.2f})"
        )


def create_waveguide_from_edge(
    source: int,
    target: int,
    positions: Dict[int, Tuple[float, float]],
    source_type: str = 'UE',
    target_type: str = 'UE',
    scale_km: float = 0.5,
) -> WaveguideLink:
    """
    Factory function: create a WaveguideLink from topology edge data.

    Args:
        source: Source node ID
        target: Target node ID
        positions: Node positions dict
        source_type: Source node type (CU, DU, RRH, UE)
        target_type: Target node type
        scale_km: Distance scaling factor (topology units → km)

    Returns:
        Configured WaveguideLink
    """
    # Calculate distance from positions
    p1 = positions.get(source, (0, 0))
    p2 = positions.get(target, (0, 0))
    distance = np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) * scale_km

    # Determine link type from node types
    if 'CU' in (source_type, target_type) and 'DU' in (source_type, target_type):
        link_type = 'fiber'
        bandwidth = 10e9   # 10 Gbps fiber
    elif 'DU' in (source_type, target_type) and 'RRH' in (source_type, target_type):
        link_type = 'microwave'
        bandwidth = 1e9    # 1 Gbps microwave
    elif 'RRH' in (source_type, target_type) and 'UE' in (source_type, target_type):
        link_type = 'sub6ghz'
        bandwidth = 100e6  # 100 MHz 5G NR
    else:
        link_type = 'sub6ghz'
        bandwidth = 100e6

    # Base interference (wireless links have more)
    interference = 0.0
    if link_type in ('sub6ghz', 'mmwave'):
        interference = np.random.uniform(0.05, 0.15)

    return WaveguideLink(
        source=source,
        target=target,
        distance_km=max(0.01, distance),
        link_type=link_type,
        bandwidth_hz=bandwidth,
        interference_factor=interference,
    )
