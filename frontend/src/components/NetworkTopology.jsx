import { useState } from 'react';
import { Zap, AlertTriangle, Radio } from 'lucide-react';

export default function NetworkTopology({ topology, metrics, inactiveNodes = [], onNodeToggle = () => {}, simulationMode = 'ideal', rfMetrics = null }) {
  if (!topology || !topology.nodes) {
    return <div className="p-4 text-slate-400">Loading topology...</div>;
  }

  const [hoveredNode, setHoveredNode] = useState(null);
  const [hoveredLink, setHoveredLink] = useState(null);
  const isRF = simulationMode === 'realistic_rf';
  const scale = 60;
  const offsetX = 350;
  const offsetY = 80;

  const getPos = (pos = [0, 0]) => [pos[0] * scale + offsetX, pos[1] * scale + offsetY];

  const getNodeType = (node) => {
    if (node.type) return node.type;
    if (node.id === 0) return 'CU';
    if (node.id < 3) return 'DU';
    if (node.id < 6) return 'RRH';
    return 'UE';
  };

  const getNodeColor = (node) => {
    const isInactive = inactiveNodes.includes(node.id);
    if (isInactive) return '#666666';
    const nodeType = getNodeType(node);
    switch (nodeType) {
      case 'CU': return '#ff3131';
      case 'DU': return '#fbbf24';
      case 'RRH': return '#3b82f6';
      case 'UE': return '#10b981';
      default: return '#888888';
    }
  };

  // Get RF signal quality for a link
  const getLinkRFData = (source, target) => {
    if (!isRF || !rfMetrics?.links) return null;
    return rfMetrics.links[`${source}-${target}`] || null;
  };

  // Get RF data for a node
  const getNodeRFData = (nodeId) => {
    if (!isRF || !rfMetrics?.nodes) return null;
    return rfMetrics.nodes[String(nodeId)] || null;
  };

  // Link color based on signal quality in RF mode
  const getLinkColor = (link, rfData) => {
    const uActive = !inactiveNodes.includes(link.source);
    const vActive = !inactiveNodes.includes(link.target);
    if (!uActive || !vActive) return 'rgba(100, 100, 100, 0.2)';

    if (isRF && rfData) {
      const snr = rfData.output_snr || 0;
      if (snr > 20) return 'rgba(6, 182, 212, 0.7)';     // Cyan — excellent
      if (snr > 10) return 'rgba(251, 191, 36, 0.6)';     // Yellow — moderate
      return 'rgba(239, 68, 68, 0.6)';                       // Red — poor
    }
    return 'rgba(59, 130, 246, 0.5)';
  };

  const getLinkWidth = (link, rfData) => {
    const uActive = !inactiveNodes.includes(link.source);
    const vActive = !inactiveNodes.includes(link.target);
    if (!uActive || !vActive) return 1.5;

    if (isRF && rfData) {
      const quality = rfData.link_quality || 0.5;
      return 2 + quality * 4;  // 2–6 width based on quality
    }
    return 3;
  };

  return (
    <div className="w-full glass-panel p-6 overflow-hidden">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-bold flex items-center gap-2">
            {isRF ? <Radio size={20} className="text-cyan-400" /> : <Zap size={20} className="text-red-500" />}
            {isRF ? 'RF SIGNAL TOPOLOGY' : 'LIVE NETWORK TOPOLOGY'}
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            {isRF
              ? 'Waveguide links • Circuit nodes • Signal flow visualization'
              : 'Click nodes to toggle | Red=CU | Amber=DU | Blue=RRH | Green=UE'}
          </p>
        </div>
        <div className="flex gap-2">
          {isRF && (
            <div className="flex items-center gap-2 px-3 py-2 bg-cyan-500/10 border border-cyan-500/30 rounded text-xs text-cyan-400">
              <Radio size={14} /> RF Mode
            </div>
          )}
          {inactiveNodes.length > 0 && (
            <div className="flex items-center gap-2 px-3 py-2 bg-red-500/10 border border-red-500/30 rounded text-sm text-red-400">
              <AlertTriangle size={16} />
              {inactiveNodes.length} Offline
            </div>
          )}
        </div>
      </div>

      <svg
        className={`w-full h-96 border rounded ${isRF
          ? 'border-cyan-900/40 bg-gradient-to-br from-slate-950 via-cyan-950/10 to-slate-950'
          : 'border-slate-700 bg-gradient-to-br from-slate-900 to-slate-950'}`}
        viewBox="0 0 900 400"
      >
        <defs>
          <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
            <path d="M 50 0 L 0 0 0 50" fill="none" stroke={isRF ? '#0a3a3a' : '#333'} strokeWidth="0.5" />
          </pattern>
          {/* Waveguide gradient for RF mode */}
          <linearGradient id="waveguideGood" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="rgba(6,182,212,0.6)" />
            <stop offset="50%" stopColor="rgba(6,182,212,0.9)" />
            <stop offset="100%" stopColor="rgba(6,182,212,0.6)" />
          </linearGradient>
          <linearGradient id="waveguideMed" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="rgba(251,191,36,0.4)" />
            <stop offset="50%" stopColor="rgba(251,191,36,0.7)" />
            <stop offset="100%" stopColor="rgba(251,191,36,0.4)" />
          </linearGradient>
          <linearGradient id="waveguidePoor" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="rgba(239,68,68,0.4)" />
            <stop offset="50%" stopColor="rgba(239,68,68,0.7)" />
            <stop offset="100%" stopColor="rgba(239,68,68,0.4)" />
          </linearGradient>
          {/* Signal flow particle */}
          <circle id="signalParticle" r="2" fill="#06b6d4" opacity="0.9">
            <animate attributeName="opacity" values="0.9;0.3;0.9" dur="1s" repeatCount="indefinite" />
          </circle>
          {/* Glow filter for RF nodes */}
          <filter id="rfGlow">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <rect width="900" height="400" fill="url(#grid)" opacity="0.3" />

        {/* Links / Waveguides */}
        {topology.links &&
          topology.links.map((link, idx) => {
            const u = topology.nodes.find((n) => n.id === link.source);
            const v = topology.nodes.find((n) => n.id === link.target);
            if (!u || !v) return null;

            const uActive = !inactiveNodes.includes(u.id);
            const vActive = !inactiveNodes.includes(v.id);
            const linkActive = uActive && vActive;
            const [x1, y1] = getPos(u.pos);
            const [x2, y2] = getPos(v.pos);
            const rfData = getLinkRFData(link.source, link.target);
            const linkColor = getLinkColor(link, rfData);
            const linkWidth = getLinkWidth(link, rfData);
            const isHovered = hoveredLink === idx;

            return (
              <g key={`link-${idx}`}
                onMouseEnter={() => setHoveredLink(idx)}
                onMouseLeave={() => setHoveredLink(null)}
              >
                {/* Waveguide pipe (RF mode) or simple line */}
                {isRF && linkActive ? (
                  <>
                    {/* Outer glow pipe */}
                    <line x1={x1} y1={y1} x2={x2} y2={y2}
                      stroke={linkColor} strokeWidth={linkWidth + 4}
                      opacity={0.15} strokeLinecap="round"
                    />
                    {/* Core pipe */}
                    <line x1={x1} y1={y1} x2={x2} y2={y2}
                      stroke={linkColor} strokeWidth={linkWidth}
                      strokeLinecap="round" opacity={0.8}
                    />
                    {/* Signal flow particle animation */}
                    {linkActive && (
                      <circle r="2.5" fill="#06b6d4" opacity="0.8">
                        <animateMotion
                          dur={`${1.5 + Math.random()}s`}
                          repeatCount="indefinite"
                          path={`M${x1},${y1} L${x2},${y2}`}
                        />
                        <animate attributeName="opacity" values="0.8;0.2;0.8" dur="1s" repeatCount="indefinite" />
                      </circle>
                    )}
                  </>
                ) : (
                  <line x1={x1} y1={y1} x2={x2} y2={y2}
                    stroke={linkActive ? 'rgba(59, 130, 246, 0.5)' : 'rgba(100, 100, 100, 0.2)'}
                    strokeWidth={linkActive ? 3 : 1.5}
                  />
                )}

                {/* Link tooltip */}
                {isHovered && (
                  <g>
                    <rect x={(x1 + x2) / 2 - 50} y={(y1 + y2) / 2 - 35} width="100" height={isRF && rfData ? 48 : 22}
                      rx="4" fill="#0a0a0a" stroke={isRF ? '#06b6d4' : '#3b82f6'} opacity="0.95"
                    />
                    <text x={(x1 + x2) / 2} y={(y1 + y2) / 2 - 20} textAnchor="middle" fontSize="9" fill="#fff">
                      {link.cap}Mbps / {link.lat}ms
                    </text>
                    {isRF && rfData && (
                      <>
                        <text x={(x1 + x2) / 2} y={(y1 + y2) / 2 - 8} textAnchor="middle" fontSize="8" fill="#06b6d4">
                          SNR: {(rfData.output_snr || 0).toFixed(1)}dB
                        </text>
                        <text x={(x1 + x2) / 2} y={(y1 + y2) / 2 + 4} textAnchor="middle" fontSize="8" fill="#f59e0b">
                          Quality: {((rfData.link_quality || 0) * 100).toFixed(0)}%
                        </text>
                      </>
                    )}
                  </g>
                )}
              </g>
            );
          })}

        {/* Nodes / Circuit Blocks */}
        {topology.nodes &&
          topology.nodes.map((node) => {
            const [x, y] = getPos(node.pos);
            const isInactive = inactiveNodes.includes(node.id);
            const nodeType = getNodeType(node);
            const nodeColor = getNodeColor(node);
            const isHovered = hoveredNode === node.id;
            const nodeRF = getNodeRFData(node.id);

            return (
              <g
                key={`node-${node.id}`}
                onMouseEnter={() => setHoveredNode(node.id)}
                onMouseLeave={() => setHoveredNode(null)}
                onClick={() => onNodeToggle(node.id, isInactive)}
                style={{ cursor: 'pointer' }}
              >
                {/* RF mode: circuit block rendering */}
                {isRF && !isInactive ? (
                  <>
                    {/* Outer glow */}
                    <rect x={x - 22} y={y - 18} width="44" height="36" rx="6"
                      fill="none" stroke={nodeColor} strokeWidth="1.5" opacity="0.3"
                      filter="url(#rfGlow)"
                    >
                      <animate attributeName="opacity" values="0.3;0.15;0.3" dur="3s" repeatCount="indefinite" />
                    </rect>
                    {/* Circuit block body */}
                    <rect x={x - 20} y={y - 16} width="40" height="32" rx="5"
                      fill={`${nodeColor}22`} stroke={nodeColor}
                      strokeWidth={isHovered ? 2 : 1}
                      opacity={0.95}
                    />
                    {/* Connection pins */}
                    <line x1={x - 20} y1={y - 4} x2={x - 24} y2={y - 4} stroke={nodeColor} strokeWidth="1.5" opacity="0.6" />
                    <line x1={x + 20} y1={y - 4} x2={x + 24} y2={y - 4} stroke={nodeColor} strokeWidth="1.5" opacity="0.6" />
                    <line x1={x - 20} y1={y + 6} x2={x - 24} y2={y + 6} stroke={nodeColor} strokeWidth="1.5" opacity="0.6" />
                    <line x1={x + 20} y1={y + 6} x2={x + 24} y2={y + 6} stroke={nodeColor} strokeWidth="1.5" opacity="0.6" />
                    {/* Node label */}
                    <text x={x} y={y - 5} textAnchor="middle" fontSize="8" fontWeight="bold"
                      fill={nodeColor} opacity="0.7" pointerEvents="none">{nodeType}</text>
                    <text x={x} y={y + 8} textAnchor="middle" fontSize="11" fontWeight="bold"
                      fill="#fff" pointerEvents="none">{node.id}</text>
                    {/* SNR indicator bar */}
                    {nodeRF && (
                      <g>
                        <rect x={x - 16} y={y + 12} width="32" height="2" rx="1" fill="#1e293b" />
                        <rect x={x - 16} y={y + 12}
                          width={Math.min(32, Math.max(2, (nodeRF.output_snr / 30) * 32))}
                          height="2" rx="1"
                          fill={nodeRF.output_snr > 20 ? '#10b981' : nodeRF.output_snr > 10 ? '#f59e0b' : '#ef4444'}
                        />
                      </g>
                    )}
                  </>
                ) : (
                  <>
                    {/* Standard mode: circle rendering */}
                    {!isInactive && (
                      <circle cx={x} cy={y} r="24" fill="none" stroke={nodeColor} strokeWidth="2" opacity="0.5">
                        <animate attributeName="opacity" values="0.5;0.2;0.5" dur="2s" repeatCount="indefinite" />
                      </circle>
                    )}
                    <circle cx={x} cy={y} r="16" fill={nodeColor}
                      opacity={isInactive ? 0.4 : 1}
                      stroke={isHovered ? '#fff' : 'none'}
                      strokeWidth={isHovered ? 2 : 0}
                    />
                    <text x={x} y={y} textAnchor="middle" dy="0.3em" fontSize="11"
                      fontWeight="bold" fill={isInactive ? '#999' : '#fff'} pointerEvents="none">
                      {node.id}
                    </text>
                  </>
                )}

                {isInactive && <circle cx={x + 12} cy={y - 12} r="4" fill="#ef4444" />}

                {/* Hover tooltip */}
                {isHovered && (
                  <g>
                    <rect x={x - 45} y={y - (isRF ? 50 : 40)} width="90"
                      height={isRF && nodeRF ? 42 : 36} rx="4"
                      fill="#0a0a0a" stroke={isRF ? '#06b6d4' : '#3b82f6'} opacity="0.95"
                    />
                    <text x={x} y={y - (isRF ? 36 : 28)} textAnchor="middle" fontSize="10"
                      fontWeight="bold" fill="#fff" pointerEvents="none">{nodeType}</text>
                    <text x={x} y={y - (isRF ? 24 : 15)} textAnchor="middle" fontSize="9"
                      fill={isInactive ? '#ef4444' : '#10b981'} pointerEvents="none">
                      {isInactive ? 'OFFLINE' : 'ACTIVE'}
                    </text>
                    {isRF && nodeRF && (
                      <text x={x} y={y - 12} textAnchor="middle" fontSize="8"
                        fill="#06b6d4" pointerEvents="none">
                        SNR: {(nodeRF.output_snr || 0).toFixed(1)}dB
                      </text>
                    )}
                  </g>
                )}
              </g>
            );
          })}
      </svg>

      <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#ff3131' }}></div>
          <span>CU {isRF ? '(Core Unit)' : ''}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#fbbf24' }}></div>
          <span>DU {isRF ? '(Distributed)' : ''}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#3b82f6' }}></div>
          <span>RRH {isRF ? '(Radio Head)' : ''}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#10b981' }}></div>
          <span>UE {isRF ? '(User Equip)' : ''}</span>
        </div>
      </div>
    </div>
  );
}
