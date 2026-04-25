import React, { useState, useEffect, useRef } from 'react';
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend
} from 'recharts';
import { Activity, Shield, Cpu, RefreshCw, Zap, Layers, AlertTriangle, Wifi, Radio, Waves } from 'lucide-react';
import { getTopology, getStatus, startTraining, getParameters, toggleNode, WebSocketManager, getCurrentMetrics, getRFMode, setRFMode } from './services/api';
import NetworkTopology from './components/NetworkTopology';
import ParameterControl from './components/ParameterControl';
import RealtimeCharts from './components/RealtimeCharts';
import RFDashboard from './components/RFDashboard';

const FALLBACK_TOPOLOGY = {
  nodes: [
    { id: 0, pos: [0, 0], type: 'CU', active: true },
    { id: 1, pos: [-2, 2], type: 'DU', active: true },
    { id: 2, pos: [2, 2], type: 'DU', active: true },
    { id: 3, pos: [-4, 4], type: 'RRH', active: true },
    { id: 4, pos: [-2, 4], type: 'RRH', active: true },
    { id: 5, pos: [4, 4], type: 'RRH', active: true },
    { id: 6, pos: [-5, 6], type: 'UE', active: true },
    { id: 7, pos: [-3, 6], type: 'UE', active: true },
    { id: 8, pos: [3, 6], type: 'UE', active: true },
    { id: 9, pos: [5, 6], type: 'UE', active: true }
  ],
  links: [
    { source: 0, target: 1, cap: 1000, lat: 1, active: true },
    { source: 1, target: 0, cap: 1000, lat: 1, active: true },
    { source: 0, target: 2, cap: 1000, lat: 1, active: true },
    { source: 2, target: 0, cap: 1000, lat: 1, active: true },
    { source: 1, target: 3, cap: 500, lat: 2, active: true },
    { source: 3, target: 1, cap: 500, lat: 2, active: true },
    { source: 1, target: 4, cap: 500, lat: 2, active: true },
    { source: 4, target: 1, cap: 500, lat: 2, active: true },
    { source: 2, target: 5, cap: 500, lat: 2, active: true },
    { source: 5, target: 2, cap: 500, lat: 2, active: true },
    { source: 3, target: 6, cap: 200, lat: 5, active: true },
    { source: 6, target: 3, cap: 200, lat: 5, active: true },
    { source: 3, target: 7, cap: 200, lat: 5, active: true },
    { source: 7, target: 3, cap: 200, lat: 5, active: true },
    { source: 4, target: 7, cap: 200, lat: 5, active: true },
    { source: 7, target: 4, cap: 200, lat: 5, active: true },
    { source: 5, target: 8, cap: 200, lat: 5, active: true },
    { source: 8, target: 5, cap: 200, lat: 5, active: true },
    { source: 5, target: 9, cap: 200, lat: 5, active: true },
    { source: 9, target: 5, cap: 200, lat: 5, active: true }
  ]
};

function App() {
  const [topology, setTopology] = useState(null);
  const [status, setStatus] = useState({ status: 'idle', episode: 0, total_episodes: 100, history: [] });
  const [episodes, setEpisodes] = useState(20);
  const [isTraining, setIsTraining] = useState(false);
  const [parameters, setParameters] = useState(null);
  const [currentMetrics, setCurrentMetrics] = useState(null);
  const [metricsHistory, setMetricsHistory] = useState([]);
  const [inactiveNodes, setInactiveNodes] = useState([]);
  const [showParameters, setShowParameters] = useState(true);
  const [wsConnected, setWsConnected] = useState(false);

  // RF Mode state
  const [simulationMode, setSimulationMode] = useState('ideal');
  const [rfMetrics, setRFMetrics] = useState(null);
  const [isTogglingMode, setIsTogglingMode] = useState(false);

  const wsRef = useRef(null);
  const pollIntervalRef = useRef(null);

  // Initialize WebSocket connection and load initial data
  useEffect(() => {
    const init = async () => {
      // Load static data first so topology doesn't depend on WebSocket success
      const [topologyResult, paramResult, rfModeResult] = await Promise.allSettled([
        getTopology(),
        getParameters(),
        getRFMode(),
      ]);

      if (topologyResult.status === 'fulfilled' && topologyResult.value?.nodes?.length) {
        setTopology(topologyResult.value);
      } else {
        console.warn('Failed to load topology from API. Using fallback topology.');
        setTopology(FALLBACK_TOPOLOGY);
      }

      if (paramResult.status === 'fulfilled') {
        setParameters(paramResult.value);
      } else {
        console.error('Failed to load parameters:', paramResult.reason);
      }

      if (rfModeResult.status === 'fulfilled') {
        setSimulationMode(rfModeResult.value.mode || 'ideal');
      }

      try {
        // Create WebSocket manager
        wsRef.current = new WebSocketManager();

        // Subscribe to WebSocket messages
        wsRef.current.subscribe((message) => {
          if (message.type === 'metrics_update') {
            setCurrentMetrics(message.data);
            setMetricsHistory(prev => {
              const newHistory = [...prev, message.data];
              return newHistory.slice(-100); // Keep last 100 points
            });
            setWsConnected(true);

            // Extract RF metrics if present
            if (message.data.rf_metrics) {
              setRFMetrics(message.data.rf_metrics);
            }
            if (message.data.simulation_mode) {
              setSimulationMode(message.data.simulation_mode);
            }
          } else if (message.type === 'node_status_change') {
            setInactiveNodes(message.data.inactive_nodes);
          } else if (message.type === 'episode_complete') {
            setStatus(prev => ({
              ...prev,
              episode: message.data.episode + 1,
              history: [...prev.history, message.data]
            }));
          } else if (message.type === 'training_complete') {
            setStatus(message.data);
            setIsTraining(false);
          } else if (message.type === 'snapshot') {
            setStatus(message.data.status);
            setCurrentMetrics(message.data.metrics);
            setInactiveNodes(message.data.inactive_nodes);
            if (message.data.simulation_mode) {
              setSimulationMode(message.data.simulation_mode);
            }
            if (message.data.status.status === 'training') setIsTraining(true);
            setWsConnected(true);
          } else if (message.type === 'rf_mode_change') {
            setSimulationMode(message.data.mode);
            // Reload topology with RF attributes
            getTopology().then(t => setTopology(t)).catch(() => {});
          }
        });

        // Connect and get snapshot
        await wsRef.current.connect();
        wsRef.current.getSnapshot();
      } catch (err) {
        setWsConnected(false);
        console.warn("WebSocket unavailable, using polling fallback.", err);
      }
    };

    init();

    // Polling fallback for status updates (in case WebSocket is not available)
    pollIntervalRef.current = setInterval(async () => {
      try {
        if (!wsRef.current || !wsRef.current.isConnected()) {
          const [statusData, metricsData] = await Promise.all([
            getStatus(),
            getCurrentMetrics()
          ]);

          setStatus(statusData);
          if (statusData.simulation_mode) {
            setSimulationMode(statusData.simulation_mode);
          }
          if (metricsData && metricsData.metrics) {
            setCurrentMetrics(metricsData.metrics);
            setMetricsHistory(prev => {
              const newHistory = [...prev, metricsData.metrics];
              return newHistory.slice(-100);
            });
          }

          if (statusData.status === 'training') setIsTraining(true);
          else if (statusData.status === 'completed' || statusData.status === 'failed') {
            setIsTraining(false);
          }
        }
      } catch (err) {
        console.error("Failed to poll status", err);
      }
    }, 500);

    return () => {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
      if (wsRef.current) wsRef.current.disconnect();
    };
  }, []);

  const handleStartTraining = async () => {
    try {
      setIsTraining(true);
      setMetricsHistory([]);
      await startTraining(episodes);
    } catch (err) {
      alert("Error starting training: " + err.message);
      setIsTraining(false);
    }
  };

  const handleNodeToggle = async (nodeId, isCurrentlyActive) => {
    try {
      // Send to backend via WebSocket if available, otherwise via REST
      if (wsRef.current && wsRef.current.isConnected()) {
        wsRef.current.toggleNode(nodeId, isCurrentlyActive);
      } else {
        await toggleNode(nodeId, !isCurrentlyActive);
      }

      // Update local state
      setInactiveNodes(prev =>
        isCurrentlyActive
          ? [...prev, nodeId]
          : prev.filter(n => n !== nodeId)
      );
    } catch (err) {
      console.error("Error toggling node:", err);
    }
  };

  const handleRFModeToggle = async () => {
    if (isTraining || isTogglingMode) return;
    setIsTogglingMode(true);
    try {
      const newMode = simulationMode === 'ideal' ? 'realistic_rf' : 'ideal';
      const result = await setRFMode(newMode);
      setSimulationMode(result.mode);
      // Reload topology with RF attributes
      const newTopology = await getTopology();
      setTopology(newTopology);
      setMetricsHistory([]);
      setRFMetrics(null);
    } catch (err) {
      console.error("Error switching RF mode:", err);
    } finally {
      setIsTogglingMode(false);
    }
  };

  const isRF = simulationMode === 'realistic_rf';
  const currentStats = status.history.length > 0 ? status.history[status.history.length - 1] : null;
  const avgLatency = currentMetrics && currentMetrics.metrics
    ? Object.values(currentMetrics.metrics).reduce((sum, m) => sum + (m.latency || 0), 0) / 3
    : 0;

  // RF-specific stats
  const avgSnr = currentMetrics?.rf_metrics
    ? Object.values(currentMetrics.rf_metrics.links || {}).reduce((sum, l) => sum + (l.output_snr || 0), 0) / Math.max(1, Object.keys(currentMetrics.rf_metrics.links || {}).length)
    : 0;

  return (
    <div className={`min-h-screen grid-bg p-6 lg:p-8 ${isRF ? 'rf-mode-active' : ''}`}>
      {/* Header with Status */}
      <header className="flex justify-between items-center mb-8 w-full max-w-7xl mx-auto">
        <div>
          <h1 className="text-3xl lg:text-4xl font-bold neon-text tracking-tighter flex items-center gap-3">
            <Shield className="w-8 lg:w-10 h-8 lg:h-10" /> 5G X-DQN <span className="text-white font-light">ORCHESTRATOR</span>
          </h1>
          <p className="text-slate-400 mt-2 font-mono text-xs lg:text-sm">
            {isRF ? 'HYBRID RF SIGNAL + NETWORK INTELLIGENCE SIMULATION' : 'REAL-TIME CROSS-LAYER SLICE MANAGEMENT & VISUALIZATION'}
          </p>
        </div>

        <div className="flex flex-col gap-2">
          {/* RF Mode Toggle */}
          <button
            onClick={handleRFModeToggle}
            disabled={isTraining || isTogglingMode}
            className={`rf-mode-toggle ${isRF ? 'rf-mode-toggle-active' : ''} ${(isTraining || isTogglingMode) ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <Radio size={14} className={isRF ? 'text-cyan-400' : 'text-slate-400'} />
            <span>{isRF ? 'RF MODE' : 'IDEAL MODE'}</span>
            <div className={`rf-toggle-indicator ${isRF ? 'rf-toggle-on' : ''}`}>
              <div className="rf-toggle-dot" />
            </div>
          </button>

          <div className="glass-panel px-4 lg:px-6 py-2 lg:py-3 flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${isTraining ? 'bg-red-500 animate-pulse shadow-[0_0_10px_#ef4444]' : 'bg-slate-600'}`}></div>
            <span className="text-xs lg:text-sm font-medium uppercase tracking-widest text-slate-300">
              {status.status}
            </span>
          </div>
          <div className="glass-panel px-4 lg:px-6 py-2 flex items-center gap-2 text-xs text-slate-300">
            <Wifi size={14} className={wsConnected ? 'text-green-500' : 'text-red-500'} />
            <span>{wsConnected ? 'WebSocket' : 'Polling'}</span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto grid grid-cols-12 gap-4 lg:gap-6">

        {/* Left Column: Controls */}
        <div className="col-span-12 lg:col-span-3 flex flex-col gap-4 lg:gap-6">

          {/* System Control */}
          <div className="glass-panel p-4 lg:p-6">
            <h3 className="text-base lg:text-lg font-bold mb-5 flex items-center gap-2">
              <Zap size={18} className="text-red-500" /> SYSTEM CONTROL
            </h3>
            <div className="flex flex-col gap-5">
              <div className="flex gap-3">
                <button
                  onClick={() => setShowParameters(true)}
                  className={`modern-toggle-btn ${showParameters ? 'modern-toggle-btn-active' : ''}`}
                >
                  PARAMETERS
                </button>
                <button
                  onClick={() => setShowParameters(false)}
                  className={`modern-toggle-btn ${!showParameters ? 'modern-toggle-btn-active' : ''}`}
                >
                  EXPERIMENTS
                </button>
              </div>

              {showParameters ? (
                <div className="space-y-4 animate-in fade-in slide-in-from-left-2 duration-300">
                  {parameters && <ParameterControl parameters={parameters} onUpdate={setParameters} />}
                </div>
              ) : (
                <div className="space-y-4 animate-in fade-in slide-in-from-right-2 duration-300">
                  <div>
                    <label className="text-xs text-slate-400 uppercase block mb-1">Target Episodes</label>
                    <input
                      type="number"
                      value={episodes}
                      onChange={(e) => setEpisodes(parseInt(e.target.value))}
                      disabled={isTraining}
                      className="w-full bg-black/40 border border-red-900/40 rounded p-2 text-white focus:outline-none focus:border-red-500 text-sm"
                    />
                  </div>
                  <button
                    onClick={handleStartTraining}
                    disabled={isTraining}
                    className={`modern-primary-btn w-full flex justify-center items-center gap-2 ${isTraining ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    {isTraining ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Activity className="w-4 h-4" />}
                    {isTraining ? 'Optimizing...' : 'Start Training'}
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Real-time Metrics Panel */}
          <div className="glass-panel p-4 lg:p-6">
            <h3 className="text-base lg:text-lg font-bold mb-4 flex items-center gap-2">
              <Cpu size={18} className="text-red-500" /> LIVE METRICS
            </h3>
            <div className="space-y-4">
              <StatItem label="Avg Latency (ms)" value={avgLatency.toFixed(2)} color="text-blue-400" />
              <StatItem label="Reward" value={currentStats ? currentStats.reward.toFixed(2) : '0.00'} color="text-red-500" />
              <StatItem label="Episode" value={`${status.episode}/${status.total_episodes}`} color="text-green-400" />

              {/* RF-specific live metrics */}
              {isRF && (
                <>
                  <div className="border-t border-cyan-900/30 pt-3 mt-3">
                    <div className="text-[10px] text-cyan-500 uppercase tracking-widest mb-2 flex items-center gap-1">
                      <Radio size={10} /> RF SIGNAL
                    </div>
                    <StatItem label="Avg SNR" value={`${avgSnr.toFixed(1)} dB`} color="text-cyan-400" />
                  </div>
                </>
              )}

              {inactiveNodes.length > 0 && (
                <div className="p-3 bg-red-500/10 border border-red-500/30 rounded text-xs">
                  <div className="flex items-center gap-2 mb-2 text-red-400 font-bold">
                    <AlertTriangle size={14} />
                    INACTIVE NODES
                  </div>
                  <div className="text-slate-300">{inactiveNodes.join(', ')}</div>
                </div>
              )}

              <div className="mt-6">
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-400 uppercase">Progress</span>
                  <span className="text-white">{status.episode}%</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                  <div
                    className={`h-full transition-all duration-500 ${isRF ? 'bg-cyan-500' : 'bg-red-500'}`}
                    style={{ width: `${Math.min((status.episode / status.total_episodes) * 100, 100)}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>

          {/* Node Control Panel */}
          <div className="glass-panel p-4 lg:p-6">
            <h3 className="text-base lg:text-lg font-bold mb-4 flex items-center gap-2 text-yellow-400">
              <AlertTriangle size={18} /> NODE CONTROL
            </h3>
            <p className="text-xs text-slate-400 mb-4">Click network nodes to toggle on/off</p>
            {topology && topology.nodes && (
              <div className="grid grid-cols-2 gap-3">
                {topology.nodes.map(node => (
                  <button
                    key={node.id}
                    onClick={() => handleNodeToggle(node.id, !inactiveNodes.includes(node.id))}
                    className={`modern-node-btn ${inactiveNodes.includes(node.id)
                        ? 'modern-node-btn-offline'
                        : 'modern-node-btn-online'
                      }`}
                  >
                    Node {node.id}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Visualizations */}
        <div className="col-span-12 lg:col-span-9 flex flex-col gap-4 lg:gap-6">

          {/* Network Topology */}
          <NetworkTopology
            topology={topology}
            metrics={currentMetrics}
            inactiveNodes={inactiveNodes}
            onNodeToggle={handleNodeToggle}
            simulationMode={simulationMode}
            rfMetrics={rfMetrics}
          />

          {/* RF Dashboard (only visible in RF mode) */}
          {isRF && (
            <RFDashboard
              rfMetrics={rfMetrics}
              topology={topology}
              simulationMode={simulationMode}
            />
          )}

          {/* Real-time Charts */}
          <div className="w-full">
            <RealtimeCharts
              metricsHistory={metricsHistory}
              simulationMode={simulationMode}
            />
          </div>

          {/* Performance Trends */}
          <div className="glass-panel p-4 lg:p-6 h-[280px] lg:h-[350px]">
            <h3 className="text-base lg:text-lg font-bold mb-3 flex items-center gap-2">
              <Layers size={18} className="text-red-500" /> TRAINING PROGRESS
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={status.history} margin={{ top: 5, right: 20, left: -20, bottom: 5 }}>
                <defs>
                  <linearGradient id="colorReward" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={isRF ? '#06b6d4' : '#ff3131'} stopOpacity={0.3} />
                    <stop offset="95%" stopColor={isRF ? '#06b6d4' : '#ff3131'} stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorLatency" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#222" vertical={false} />
                <XAxis dataKey="episode" tick={{ fontSize: 11, fill: '#888' }} stroke="#444" />
                <YAxis tick={{ fontSize: 11, fill: '#888' }} stroke="#444" width={35} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #555' }}
                  formatter={(value) => value.toFixed(3)}
                />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                <Area type="monotone" dataKey="reward" stroke={isRF ? '#06b6d4' : '#ff3131'} fill="url(#colorReward)" name="Reward" isAnimationActive={false} />
                <Area type="monotone" dataKey="latency" stroke="#3b82f6" fill="url(#colorLatency)" name="Latency (ms)" isAnimationActive={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-8 lg:mt-12 max-w-7xl mx-auto border-t border-slate-800 pt-4 text-xs text-slate-500 text-center">
        <p>5G X-DQN Orchestrator | {isRF ? 'Hybrid RF Signal + Network Intelligence' : 'Real-Time Network Simulation'} | v2.0 PCAN-5G</p>
      </footer>
    </div>
  );
}

function StatItem({ label, value, color }) {
  return (
    <div className="flex justify-between items-end">
      <span className="text-xs lg:text-sm text-slate-400">{label}</span>
      <span className={`text-lg lg:text-2xl font-bold font-mono ${color}`}>{value}</span>
    </div>
  );
}

export default App;
