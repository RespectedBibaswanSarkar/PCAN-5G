"""Quick smoke test for the PCAN-5G hardware abstraction upgrade."""
import numpy as np

print("=" * 60)
print("PCAN-5G Hardware Abstraction Upgrade — Smoke Tests")
print("=" * 60)

# Test 1: Ideal mode backward compatibility
print("\n[TEST 1] Ideal mode (backward compatibility)")
from environment import FiveGEnvironment
env = FiveGEnvironment(simulation_mode='ideal')
state = env.reset()
print(f"  State dim: {len(state)} (expected 18)")
assert len(state) == 18, f"FAIL: {len(state)} != 18"
next_state, reward, done, metrics = env.step(4)
print(f"  Step OK — reward: {reward:.3f}, latency: {metrics['eMBB']['latency']:.3f}")
assert 'eMBB' in metrics
assert 'latency' in metrics['eMBB']
print("  PASS")

# Test 2: Realistic RF mode
print("\n[TEST 2] Realistic RF mode")
env2 = FiveGEnvironment(simulation_mode='realistic_rf')
state2 = env2.reset()
print(f"  State dim: {len(state2)} (expected 25)")
assert len(state2) == 25, f"FAIL: {len(state2)} != 25"
ns, r, d, m = env2.step(4)
print(f"  Step OK — reward: {r:.3f}")
has_snr = 'avg_snr' in m['eMBB']
print(f"  RF metrics in slice data: {has_snr}")
assert has_snr, "FAIL: RF metrics missing"
print("  PASS")

# Test 3: Mode switching
print("\n[TEST 3] Mode switching")
env.set_simulation_mode('realistic_rf')
s3 = env.reset()
assert len(s3) == 25
env.set_simulation_mode('ideal')
s4 = env.reset()
assert len(s4) == 18
print("  PASS")

# Test 4: Hardware modules
print("\n[TEST 4] Hardware modules")
from hardware import Signal, WaveguideLink, BandpassFilter, NotchFilter, Amplifier, Oscillator, NodeSignalPipeline

sig = Signal.default_5g('n78')
print(f"  Signal: {sig}")

wg = WaveguideLink(0, 1, distance_km=1.0, link_type='fiber')
out = wg.propagate(sig)
print(f"  After waveguide: amp={out.amplitude:.4f}, SNR={out.snr:.1f}dB")
assert out.amplitude < sig.amplitude, "Waveguide should attenuate"

bp = BandpassFilter(center_freq=3.5e9, bandwidth=100e6)
filtered = bp.apply(sig)
print(f"  After bandpass filter: amp={filtered.amplitude:.4f}")
assert filtered.noise < sig.noise, "Filter should reduce noise"

nf = NotchFilter(notch_freq=3.55e9, notch_width=10e6)
notched = nf.apply(sig)
print(f"  After notch filter: amp={notched.amplitude:.4f}")

amp_mod = Amplifier(gain=10, max_output=5.0, noise_figure_db=3.0)
amplified = amp_mod.amplify(filtered)
print(f"  After amplifier: amp={amplified.amplitude:.4f}")
assert amplified.amplitude > filtered.amplitude, "Amplifier should boost"

osc = Oscillator(threshold=0.1, target_amplitude=1.0)
weak_sig = Signal(frequency=3.5e9, amplitude=0.05, phase=0, noise=0.01)
regen = osc.regenerate(weak_sig)
print(f"  Oscillator regenerated: {weak_sig.amplitude:.3f} -> {regen.amplitude:.3f}")
assert regen.amplitude == 1.0, "Should regenerate to target"
assert osc.was_regenerated, "Should flag as regenerated"

strong_sig = Signal(frequency=3.5e9, amplitude=0.5, phase=0, noise=0.001)
passthrough = osc.regenerate(strong_sig)
assert passthrough.amplitude == 0.5, "Should pass through strong signal"
assert not osc.was_regenerated
print("  PASS")

# Test 5: Signal pipeline
print("\n[TEST 5] Signal pipeline")
from hardware.signal_pipeline import create_pipeline_for_node
pipeline = create_pipeline_for_node(3, 'RRH')
test_sig = Signal.default_5g()
output = pipeline.process(test_sig)
print(f"  Pipeline: in={test_sig.amplitude:.4f} -> out={output.amplitude:.4f}")
stages = pipeline.stage_metrics
print(f"  Stages recorded: {list(stages.keys())}")
assert 'input' in stages
assert 'after_filter' in stages
assert 'after_amplifier' in stages
assert 'after_oscillator' in stages
quality = pipeline.get_current_signal_quality()
print(f"  Signal quality: SNR={quality['output_snr']:.1f}dB")
print("  PASS")

# Test 6: RF Agent
print("\n[TEST 6] RF-aware agent")
from rf_agent import RFAwareAgent
rf_agent = RFAwareAgent(state_dim=28, action_dim=9)
test_state = np.random.randn(28).astype(np.float32)
action = rf_agent.act_with_rf_awareness(test_state)
print(f"  RF agent action: {action}")
stats = rf_agent.get_rf_stats()
print(f"  RF stats: {stats}")
print("  PASS")

# Test 7: get_state_dim
print("\n[TEST 7] State dimension helper")
e_ideal = FiveGEnvironment('ideal')
e_rf = FiveGEnvironment('realistic_rf')
print(f"  Ideal raw dim: {e_ideal.get_state_dim()} (expected 18)")
print(f"  RF raw dim: {e_rf.get_state_dim()} (expected 25)")
print(f"  Ideal + pred: {e_ideal.get_state_dim() + 3} (expected 21)")
print(f"  RF + pred: {e_rf.get_state_dim() + 3} (expected 28)")
assert e_ideal.get_state_dim() == 18
assert e_rf.get_state_dim() == 25
print("  PASS")

# Test 8: Routing cost
print("\n[TEST 8] Routing cost (RF mode)")
env_rf = FiveGEnvironment('realistic_rf')
env_rf.reset()
env_rf.step(4)  # Run a step to populate RF cache
cost = env_rf.compute_routing_cost(0, 1)
print(f"  Routing cost (0->1): {cost:.3f}")
violations = env_rf.get_snr_threshold_violations(threshold_db=50)
print(f"  SNR violations (threshold=50dB): {len(violations)} links")
print("  PASS")

print("\n" + "=" * 60)
print("ALL 8 TESTS PASSED SUCCESSFULLY")
print("=" * 60)
