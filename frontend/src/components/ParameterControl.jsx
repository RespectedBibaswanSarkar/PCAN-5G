import React from 'react';
import { updateParameters } from '../services/api';

const ParameterControl = ({ parameters, onUpdate }) => {
  if (!parameters) return <div className="text-slate-500 text-xs animate-pulse">Loading parameters...</div>;

  const handleChange = async (field, value) => {
    try {
      const resp = await updateParameters({ [field]: value });
      onUpdate(resp.new_params);
    } catch (err) {
      console.error("Failed to update parameter", err);
    }
  };

  const scenarios = ['low', 'medium', 'high'];

  return (
    <div className="space-y-4">
      <div>
        <label className="text-[10px] text-slate-500 uppercase tracking-widest block mb-2">Traffic Scenario</label>
        <div className="flex gap-2">
          {scenarios.map(s => (
            <button
              key={s}
              onClick={() => handleChange('traffic_scenario', s)}
              className={`flex-1 py-1 px-2 text-[10px] font-bold rounded capitalize transition-all ${
                parameters.traffic_scenario === s 
                ? 'bg-red-500 text-white shadow-[0_0_10px_rgba(239,68,68,0.3)]' 
                : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-3">
        <SliderItem 
          label="Congestion Threshold" 
          value={parameters.thresholds.congestion_max} 
          min={0.1} max={0.9} step={0.1}
          onChange={(v) => handleChange('congestion_threshold', v)}
        />
        <SliderItem 
          label="Latency Cutoff (ms)" 
          value={parameters.thresholds.latency_max} 
          min={10} max={200} step={10}
          onChange={(v) => handleChange('latency_threshold', v)}
        />
        <SliderItem 
          label="Fault Probability" 
          value={parameters.link_failure_probability} 
          min={0} max={0.2} step={0.01}
          onChange={(v) => handleChange('link_failure_probability', v)}
        />
      </div>
    </div>
  );
};

const SliderItem = ({ label, value, min, max, step, onChange }) => (
  <div>
    <div className="flex justify-between items-center mb-1">
      <span className="text-[10px] text-slate-500 uppercase">{label}</span>
      <span className="text-[10px] font-mono text-red-500">{typeof value === 'number' ? value.toFixed(2) : value}</span>
    </div>
    <input 
      type="range" 
      min={min} max={max} step={step} 
      value={value}
      onChange={(e) => onChange(parseFloat(e.target.value))}
      className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-red-500"
    />
  </div>
);

export default ParameterControl;
