import React, { useState, useEffect, useRef } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
  ComposedChart, Area, AreaChart
} from 'recharts';
import { Zap, TrendingUp, AlertCircle, Signal, Radio, Waves } from 'lucide-react';

const RealtimeCharts = ({ metricsHistory = [], simulationMode = 'ideal' }) => {
  const [displayData, setDisplayData] = useState([]);
  const [windowSize] = useState(30); // Keep last 30 data points
  const dataRef = useRef([]);
  const isRF = simulationMode === 'realistic_rf';

  useEffect(() => {
    if (metricsHistory && metricsHistory.length > 0) {
      const latestMetrics = metricsHistory[metricsHistory.length - 1];

      if (latestMetrics.metrics) {
        const newPoint = {
          timestamp: latestMetrics.timestamp || Date.now(),
          step: latestMetrics.step || 0,
          reward: latestMetrics.reward || 0,
          // Calculate slice averages
          latency_embb: latestMetrics.metrics.eMBB?.latency || 0,
          latency_urllc: latestMetrics.metrics.URLLC?.latency || 0,
          latency_mmtc: latestMetrics.metrics.mMTC?.latency || 0,
          throughput_embb: latestMetrics.metrics.eMBB?.throughput || 0,
          throughput_urllc: latestMetrics.metrics.URLLC?.throughput || 0,
          throughput_mmtc: latestMetrics.metrics.mMTC?.throughput || 0,
          loss_embb: latestMetrics.metrics.eMBB?.packet_loss || 0,
          loss_urllc: latestMetrics.metrics.URLLC?.packet_loss || 0,
          loss_mmtc: latestMetrics.metrics.mMTC?.packet_loss || 0,
          congestion_embb: latestMetrics.metrics.eMBB?.congestion || 0,
          congestion_urllc: latestMetrics.metrics.URLLC?.congestion || 0,
          congestion_mmtc: latestMetrics.metrics.mMTC?.congestion || 0,
          phy_factor: latestMetrics.metrics.eMBB?.phy_factor || 1,
        };

        // RF-specific metrics
        if (isRF && latestMetrics.rf_metrics) {
          const linkValues = Object.values(latestMetrics.rf_metrics.links || {});
          const nodeValues = Object.values(latestMetrics.rf_metrics.nodes || {});

          newPoint.avg_snr = linkValues.length > 0
            ? linkValues.reduce((sum, l) => sum + (l.output_snr || 0), 0) / linkValues.length : 0;
          newPoint.min_snr = linkValues.length > 0
            ? Math.min(...linkValues.map(l => l.output_snr || 0)) : 0;
          newPoint.avg_interference = linkValues.length > 0
            ? linkValues.reduce((sum, l) => sum + (l.interference || 0), 0) / linkValues.length : 0;
          newPoint.avg_amplitude = nodeValues.length > 0
            ? nodeValues.reduce((sum, n) => sum + (n.output_amplitude || 0), 0) / nodeValues.length : 0;
          newPoint.avg_noise = nodeValues.length > 0
            ? nodeValues.reduce((sum, n) => sum + (n.noise_level || 0), 0) / nodeValues.length : 0;
          newPoint.avg_quality = linkValues.length > 0
            ? linkValues.reduce((sum, l) => sum + (l.link_quality || 0), 0) / linkValues.length : 0;
          newPoint.rf_factor = latestMetrics.metrics.eMBB?.rf_factor || 1;
        }

        dataRef.current.push(newPoint);
        if (dataRef.current.length > windowSize) {
          dataRef.current.shift();
        }
        setDisplayData([...dataRef.current]);
      }
    }
  }, [metricsHistory, windowSize, isRF]);

  return (
    <div className="w-full grid grid-cols-1 lg:grid-cols-2 gap-4">
      {/* Latency Chart */}
      <div className="glass-panel p-4 col-span-1 lg:col-span-1">
        <h4 className="text-sm font-bold mb-3 flex items-center gap-2 text-white">
          <TrendingUp size={16} className="text-blue-500" /> LATENCY (ms)
        </h4>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={displayData} margin={{ top: 5, right: 20, left: -20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
            <XAxis dataKey="step" tick={{ fontSize: 12, fill: '#888' }} stroke="#444" />
            <YAxis tick={{ fontSize: 12, fill: '#888' }} stroke="#444" width={40} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #555', borderRadius: '4px' }}
              formatter={(value) => value.toFixed(2)}
            />
            <Legend />
            <Line type="monotone" dataKey="latency_embb" stroke="#3b82f6" dot={false} strokeWidth={2} name="eMBB" isAnimationActive={false} />
            <Line type="monotone" dataKey="latency_urllc" stroke="#ef4444" dot={false} strokeWidth={2} name="URLLC" isAnimationActive={false} />
            <Line type="monotone" dataKey="latency_mmtc" stroke="#10b981" dot={false} strokeWidth={2} name="mMTC" isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Throughput Chart */}
      <div className="glass-panel p-4 col-span-1 lg:col-span-1">
        <h4 className="text-sm font-bold mb-3 flex items-center gap-2 text-white">
          <Zap size={16} className="text-green-500" /> THROUGHPUT (Mbps)
        </h4>
        <ResponsiveContainer width="100%" height={250}>
          <AreaChart data={displayData} margin={{ top: 5, right: 20, left: -20, bottom: 5 }}>
            <defs>
              <linearGradient id="colorTh1" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorTh2" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
            <XAxis dataKey="step" tick={{ fontSize: 12, fill: '#888' }} stroke="#444" />
            <YAxis tick={{ fontSize: 12, fill: '#888' }} stroke="#444" width={40} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #555', borderRadius: '4px' }}
              formatter={(value) => value.toFixed(2)}
            />
            <Legend />
            <Area type="monotone" dataKey="throughput_embb" stroke="#3b82f6" fill="url(#colorTh1)" name="eMBB" isAnimationActive={false} />
            <Area type="monotone" dataKey="throughput_mmtc" stroke="#10b981" fill="url(#colorTh2)" name="mMTC" isAnimationActive={false} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Packet Loss Chart */}
      <div className="glass-panel p-4 col-span-1 lg:col-span-1">
        <h4 className="text-sm font-bold mb-3 flex items-center gap-2 text-white">
          <AlertCircle size={16} className="text-red-500" /> PACKET LOSS
        </h4>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={displayData} margin={{ top: 5, right: 20, left: -20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
            <XAxis dataKey="step" tick={{ fontSize: 12, fill: '#888' }} stroke="#444" />
            <YAxis tick={{ fontSize: 12, fill: '#888' }} stroke="#444" width={40} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #555', borderRadius: '4px' }}
              formatter={(value) => (value * 100).toFixed(2) + '%'}
            />
            <Legend />
            <Line type="monotone" dataKey="loss_embb" stroke="#3b82f6" dot={false} strokeWidth={2} name="eMBB" isAnimationActive={false} />
            <Line type="monotone" dataKey="loss_urllc" stroke="#ef4444" dot={false} strokeWidth={2} name="URLLC (Critical)" isAnimationActive={false} />
            <Line type="monotone" dataKey="loss_mmtc" stroke="#10b981" dot={false} strokeWidth={2} name="mMTC" isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Congestion & PHY Factor Chart */}
      <div className="glass-panel p-4 col-span-1 lg:col-span-1">
        <h4 className="text-sm font-bold mb-3 flex items-center gap-2 text-white">
          <Signal size={16} className="text-purple-500" /> CONGESTION & PHY
        </h4>
        <ResponsiveContainer width="100%" height={250}>
          <ComposedChart data={displayData} margin={{ top: 5, right: 20, left: -20, bottom: 5 }}>
            <defs>
              <linearGradient id="colorCong" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
            <XAxis dataKey="step" tick={{ fontSize: 12, fill: '#888' }} stroke="#444" />
            <YAxis tick={{ fontSize: 12, fill: '#888' }} stroke="#444" width={40} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #555', borderRadius: '4px' }}
              formatter={(value) => value.toFixed(3)}
            />
            <Legend />
            <Area type="monotone" dataKey="congestion_urllc" stroke="#f59e0b" fill="url(#colorCong)" name="URLLC Congestion" isAnimationActive={false} />
            <Line type="monotone" dataKey="phy_factor" stroke="#a78bfa" dot={false} strokeWidth={2} name="PHY Factor" isAnimationActive={false} />
            {isRF && <Line type="monotone" dataKey="rf_factor" stroke="#06b6d4" dot={false} strokeWidth={2} name="RF Factor" isAnimationActive={false} strokeDasharray="4 2" />}
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* SNR Over Time (RF mode only) */}
      {isRF && (
        <div className="glass-panel p-4 col-span-1 lg:col-span-1 rf-chart-panel">
          <h4 className="text-sm font-bold mb-3 flex items-center gap-2 text-white">
            <Radio size={16} className="text-cyan-400" /> SNR OVER TIME (dB)
          </h4>
          <ResponsiveContainer width="100%" height={250}>
            <ComposedChart data={displayData} margin={{ top: 5, right: 20, left: -20, bottom: 5 }}>
              <defs>
                <linearGradient id="colorSNR" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e3a3a" vertical={false} />
              <XAxis dataKey="step" tick={{ fontSize: 12, fill: '#888' }} stroke="#444" />
              <YAxis tick={{ fontSize: 12, fill: '#888' }} stroke="#444" width={40} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0a1a1a', border: '1px solid #06b6d4', borderRadius: '4px' }}
                formatter={(value) => value.toFixed(2) + ' dB'}
              />
              <Legend />
              <Area type="monotone" dataKey="avg_snr" stroke="#06b6d4" fill="url(#colorSNR)" name="Avg SNR" isAnimationActive={false} />
              <Line type="monotone" dataKey="min_snr" stroke="#ef4444" dot={false} strokeWidth={1.5} name="Min SNR" isAnimationActive={false} strokeDasharray="3 3" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Signal Amplitude & Noise (RF mode only) */}
      {isRF && (
        <div className="glass-panel p-4 col-span-1 lg:col-span-1 rf-chart-panel">
          <h4 className="text-sm font-bold mb-3 flex items-center gap-2 text-white">
            <Waves size={16} className="text-cyan-400" /> SIGNAL & NOISE
          </h4>
          <ResponsiveContainer width="100%" height={250}>
            <ComposedChart data={displayData} margin={{ top: 5, right: 20, left: -20, bottom: 5 }}>
              <defs>
                <linearGradient id="colorAmp" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorNoise" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e3a3a" vertical={false} />
              <XAxis dataKey="step" tick={{ fontSize: 12, fill: '#888' }} stroke="#444" />
              <YAxis tick={{ fontSize: 12, fill: '#888' }} stroke="#444" width={40} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0a1a1a', border: '1px solid #06b6d4', borderRadius: '4px' }}
                formatter={(value) => value.toFixed(4)}
              />
              <Legend />
              <Area type="monotone" dataKey="avg_amplitude" stroke="#10b981" fill="url(#colorAmp)" name="Avg Amplitude" isAnimationActive={false} />
              <Area type="monotone" dataKey="avg_noise" stroke="#ef4444" fill="url(#colorNoise)" name="Avg Noise" isAnimationActive={false} />
              <Line type="monotone" dataKey="avg_quality" stroke="#06b6d4" dot={false} strokeWidth={2} name="Link Quality" isAnimationActive={false} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default RealtimeCharts;
