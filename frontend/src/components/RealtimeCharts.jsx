import React, { useState, useEffect, useRef } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
  ComposedChart, Area, AreaChart
} from 'recharts';
import { Zap, TrendingUp, AlertCircle, Signal } from 'lucide-react';

const RealtimeCharts = ({ metricsHistory = [] }) => {
  const [displayData, setDisplayData] = useState([]);
  const [windowSize] = useState(30); // Keep last 30 data points
  const dataRef = useRef([]);

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

        dataRef.current.push(newPoint);
        if (dataRef.current.length > windowSize) {
          dataRef.current.shift();
        }
        setDisplayData([...dataRef.current]);
      }
    }
  }, [metricsHistory, windowSize]);

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
            <XAxis
              dataKey="step"
              tick={{ fontSize: 12, fill: '#888' }}
              stroke="#444"
            />
            <YAxis tick={{ fontSize: 12, fill: '#888' }} stroke="#444" width={40} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1a1a1a',
                border: '1px solid #555',
                borderRadius: '4px'
              }}
              formatter={(value) => value.toFixed(2)}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="latency_embb"
              stroke="#3b82f6"
              dot={false}
              strokeWidth={2}
              name="eMBB"
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="latency_urllc"
              stroke="#ef4444"
              dot={false}
              strokeWidth={2}
              name="URLLC"
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="latency_mmtc"
              stroke="#10b981"
              dot={false}
              strokeWidth={2}
              name="mMTC"
              isAnimationActive={false}
            />
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
            <XAxis
              dataKey="step"
              tick={{ fontSize: 12, fill: '#888' }}
              stroke="#444"
            />
            <YAxis tick={{ fontSize: 12, fill: '#888' }} stroke="#444" width={40} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1a1a1a',
                border: '1px solid #555',
                borderRadius: '4px'
              }}
              formatter={(value) => value.toFixed(2)}
            />
            <Legend />
            <Area
              type="monotone"
              dataKey="throughput_embb"
              stroke="#3b82f6"
              fill="url(#colorTh1)"
              name="eMBB"
              isAnimationActive={false}
            />
            <Area
              type="monotone"
              dataKey="throughput_mmtc"
              stroke="#10b981"
              fill="url(#colorTh2)"
              name="mMTC"
              isAnimationActive={false}
            />
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
            <XAxis
              dataKey="step"
              tick={{ fontSize: 12, fill: '#888' }}
              stroke="#444"
            />
            <YAxis tick={{ fontSize: 12, fill: '#888' }} stroke="#444" width={40} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1a1a1a',
                border: '1px solid #555',
                borderRadius: '4px'
              }}
              formatter={(value) => (value * 100).toFixed(2) + '%'}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="loss_embb"
              stroke="#3b82f6"
              dot={false}
              strokeWidth={2}
              name="eMBB"
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="loss_urllc"
              stroke="#ef4444"
              dot={false}
              strokeWidth={2}
              name="URLLC (Critical)"
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="loss_mmtc"
              stroke="#10b981"
              dot={false}
              strokeWidth={2}
              name="mMTC"
              isAnimationActive={false}
            />
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
            <XAxis
              dataKey="step"
              tick={{ fontSize: 12, fill: '#888' }}
              stroke="#444"
            />
            <YAxis tick={{ fontSize: 12, fill: '#888' }} stroke="#444" width={40} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1a1a1a',
                border: '1px solid #555',
                borderRadius: '4px'
              }}
              formatter={(value) => value.toFixed(3)}
            />
            <Legend />
            <Area
              type="monotone"
              dataKey="congestion_urllc"
              stroke="#f59e0b"
              fill="url(#colorCong)"
              name="URLLC Congestion"
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="phy_factor"
              stroke="#a78bfa"
              dot={false}
              strokeWidth={2}
              name="PHY Factor"
              isAnimationActive={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default RealtimeCharts;
