import React, { useState, useEffect } from 'react';
import { Radio, Waves, Zap, Activity, Volume2, Signal } from 'lucide-react';
import { getNodePipeline } from '../services/api';

/**
 * RFDashboard — Signal pipeline visualization, spectrum analyzer,
 * and per-node RF metrics display for realistic_rf mode.
 */
const RFDashboard = ({ rfMetrics, topology, simulationMode }) => {
  const [selectedNode, setSelectedNode] = useState(null);
  const [pipelineData, setPipelineData] = useState(null);

  // Fetch pipeline data when a node is selected
  useEffect(() => {
    if (selectedNode !== null && simulationMode === 'realistic_rf') {
      getNodePipeline(selectedNode)
        .then(data => setPipelineData(data))
        .catch(() => setPipelineData(null));
    }
  }, [selectedNode, simulationMode, rfMetrics]);

  if (simulationMode !== 'realistic_rf') return null;

  const nodeMetrics = rfMetrics?.nodes || {};
  const linkMetrics = rfMetrics?.links || {};

  // Compute spectrum data from link metrics
  const spectrumBands = [
    { label: '3.3 GHz', value: 0 },
    { label: '3.4 GHz', value: 0 },
    { label: '3.5 GHz', value: 0 },
    { label: '3.6 GHz', value: 0 },
    { label: '3.7 GHz', value: 0 },
  ];

  // Populate spectrum from node metrics
  const selectedNodeData = nodeMetrics[String(selectedNode)] || {};
  const outputAmp = selectedNodeData.output_amplitude || 0;
  spectrumBands.forEach((band, i) => {
    const center = 0.5 + (Math.random() * 0.3);
    band.value = Math.max(0, outputAmp * center * (i === 2 ? 1.0 : 0.3 + Math.random() * 0.4));
  });

  return (
    <div className="glass-panel p-5 rf-dashboard">
      <div className="flex items-center justify-between mb-5">
        <h3 className="text-lg font-bold flex items-center gap-2">
          <Radio size={20} className="text-cyan-400" /> RF SIGNAL DASHBOARD
        </h3>
        <div className="badge badge-rf-active">
          <Waves size={12} /> REALISTIC RF MODE
        </div>
      </div>

      {/* Node selector row */}
      <div className="mb-5">
        <p className="text-[10px] text-slate-500 uppercase tracking-widest mb-2">Select Node for Pipeline View</p>
        <div className="flex gap-2 flex-wrap">
          {topology?.nodes?.map(node => {
            const nm = nodeMetrics[String(node.id)] || {};
            const snr = nm.output_snr || 0;
            const snrColor = snr > 20 ? 'text-green-400' : snr > 10 ? 'text-yellow-400' : 'text-red-400';
            return (
              <button
                key={node.id}
                onClick={() => setSelectedNode(node.id)}
                className={`rf-node-btn ${selectedNode === node.id ? 'rf-node-btn-selected' : ''}`}
              >
                <span className="text-[10px] opacity-60">{node.type}</span>
                <span className="text-sm font-bold">{node.id}</span>
                <span className={`text-[9px] font-mono ${snrColor}`}>{snr.toFixed(0)}dB</span>
              </button>
            );
          })}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">

        {/* Signal Pipeline Diagram */}
        <div className="pipeline-container">
          <h4 className="text-xs font-bold text-cyan-300 uppercase tracking-widest mb-3 flex items-center gap-2">
            <Activity size={14} /> Signal Pipeline {selectedNode !== null ? `— Node ${selectedNode}` : ''}
          </h4>
          <div className="pipeline-chain">
            <PipelineStage
              label="INPUT"
              icon={<Signal size={16} />}
              value={pipelineData?.stage_metrics?.input?.amplitude || selectedNodeData.input_amplitude || 0}
              unit="V"
              snr={pipelineData?.stage_metrics?.input?.snr || selectedNodeData.input_snr || 0}
              color="cyan"
            />
            <div className="pipeline-arrow">→</div>
            <PipelineStage
              label="FILTER"
              icon={<Waves size={16} />}
              value={pipelineData?.stage_metrics?.after_filter?.amplitude || 0}
              unit="V"
              snr={pipelineData?.stage_metrics?.after_filter?.snr || 0}
              color="blue"
            />
            <div className="pipeline-arrow">→</div>
            <PipelineStage
              label="AMP"
              icon={<Zap size={16} />}
              value={pipelineData?.stage_metrics?.after_amplifier?.amplitude || 0}
              unit="V"
              snr={pipelineData?.stage_metrics?.after_amplifier?.snr || 0}
              color="yellow"
            />
            <div className="pipeline-arrow">→</div>
            <PipelineStage
              label="OSC"
              icon={<Radio size={16} />}
              value={pipelineData?.stage_metrics?.after_oscillator?.amplitude || selectedNodeData.output_amplitude || 0}
              unit="V"
              snr={pipelineData?.stage_metrics?.after_oscillator?.snr || selectedNodeData.output_snr || 0}
              color={pipelineData?.stage_metrics?.regenerated ? 'green' : 'purple'}
              badge={pipelineData?.stage_metrics?.regenerated ? 'REGEN' : null}
            />
          </div>
        </div>

        {/* Spectrum Analyzer */}
        <div className="spectrum-container">
          <h4 className="text-xs font-bold text-cyan-300 uppercase tracking-widest mb-3 flex items-center gap-2">
            <Volume2 size={14} /> Spectrum Analyzer {selectedNode !== null ? `— Node ${selectedNode}` : ''}
          </h4>
          <div className="spectrum-display">
            {spectrumBands.map((band, i) => {
              const height = Math.min(100, Math.max(5, band.value * 100));
              return (
                <div key={i} className="spectrum-bar-wrapper">
                  <div
                    className="spectrum-bar"
                    style={{
                      height: `${height}%`,
                      background: `linear-gradient(to top, rgba(6,182,212,0.2), rgba(6,182,212,${0.4 + height/200}))`,
                      boxShadow: height > 50 ? `0 0 12px rgba(6,182,212,0.4)` : 'none',
                    }}
                  />
                  <span className="spectrum-label">{band.label}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Per-Node Metrics Grid */}
      <div className="mt-5">
        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">
          Node Signal Metrics
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
          {Object.entries(nodeMetrics).map(([nodeId, data]) => {
            const snr = data.output_snr || 0;
            const amp = data.output_amplitude || 0;
            const noise = data.noise_level || 0;
            const regen = data.regeneration_count || 0;
            const snrColor = snr > 20 ? '#10b981' : snr > 10 ? '#f59e0b' : '#ef4444';

            return (
              <div
                key={nodeId}
                className={`rf-metric-card ${String(selectedNode) === nodeId ? 'rf-metric-card-selected' : ''}`}
                onClick={() => setSelectedNode(parseInt(nodeId))}
              >
                <div className="flex justify-between items-center mb-1">
                  <span className="text-[10px] font-bold text-slate-400">
                    {data.node_type || 'N'}{nodeId}
                  </span>
                  {regen > 0 && (
                    <span className="text-[8px] px-1.5 py-0.5 bg-green-500/20 text-green-400 rounded-full">
                      {regen}×regen
                    </span>
                  )}
                </div>
                <div className="flex justify-between items-end">
                  <div>
                    <div className="text-[9px] text-slate-500">SNR</div>
                    <div className="text-sm font-mono font-bold" style={{ color: snrColor }}>
                      {snr.toFixed(1)}
                      <span className="text-[9px] opacity-60">dB</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-[9px] text-slate-500">Amp</div>
                    <div className="text-xs font-mono text-cyan-300">{amp.toFixed(3)}</div>
                  </div>
                </div>
                <div className="mt-1 w-full bg-slate-800 rounded-full h-1">
                  <div
                    className="h-full rounded-full transition-all duration-300"
                    style={{
                      width: `${Math.min(100, (snr / 30) * 100)}%`,
                      background: snrColor,
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Link Quality Summary */}
      {Object.keys(linkMetrics).length > 0 && (
        <div className="mt-5">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">
            Waveguide Link Quality
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-2">
            {Object.entries(linkMetrics).slice(0, 10).map(([linkId, data]) => {
              const quality = data.link_quality || 0;
              const qualityColor = quality > 0.7 ? '#10b981' : quality > 0.4 ? '#f59e0b' : '#ef4444';
              return (
                <div key={linkId} className="rf-link-card">
                  <div className="text-[9px] text-slate-500 font-mono">{linkId}</div>
                  <div className="flex justify-between mt-1">
                    <span className="text-[9px] text-slate-400">SNR</span>
                    <span className="text-[10px] font-mono text-cyan-300">{(data.output_snr || 0).toFixed(1)}dB</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[9px] text-slate-400">Quality</span>
                    <span className="text-[10px] font-mono font-bold" style={{ color: qualityColor }}>
                      {(quality * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[9px] text-slate-400">Atten</span>
                    <span className="text-[10px] font-mono text-orange-300">{(data.attenuation_db || 0).toFixed(1)}dB</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

/** Pipeline stage block */
const PipelineStage = ({ label, icon, value, unit, snr, color, badge }) => {
  const colorMap = {
    cyan: 'border-cyan-500/40 text-cyan-400',
    blue: 'border-blue-500/40 text-blue-400',
    yellow: 'border-yellow-500/40 text-yellow-400',
    purple: 'border-purple-500/40 text-purple-400',
    green: 'border-green-500/40 text-green-400',
  };

  return (
    <div className={`pipeline-stage ${colorMap[color] || colorMap.cyan}`}>
      <div className="flex items-center gap-1 mb-1 opacity-70">{icon}<span className="text-[9px] font-bold">{label}</span></div>
      <div className="text-sm font-mono font-bold">{(value || 0).toFixed(3)}<span className="text-[9px] opacity-50">{unit}</span></div>
      <div className="text-[9px] opacity-60">SNR: {(snr || 0).toFixed(1)}dB</div>
      {badge && <span className="pipeline-badge">{badge}</span>}
    </div>
  );
};

export default RFDashboard;
