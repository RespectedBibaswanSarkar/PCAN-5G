import { useState } from 'react';
import { Zap, AlertTriangle } from 'lucide-react';

export default function NetworkTopology({ topology, metrics, inactiveNodes = [], onNodeToggle = () => { } }) {
  if (!topology || !topology.nodes) {
    return <div className="p-4 text-slate-400">Loading topology...</div>;
  }

  const [hoveredNode, setHoveredNode] = useState(null);
  const scale = 60;
  const offsetX = 350;
  const offsetY = 80;

  const getPos = (pos) => [pos[0] * scale + offsetX, pos[1] * scale + offsetY];

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

  return (
    <div className="w-full glass-panel p-6 overflow-hidden">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-bold flex items-center gap-2">
            <Zap size={20} className="text-red-500" /> LIVE NETWORK TOPOLOGY
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Click nodes to toggle • Red=CU • Amber=DU • Blue=RRH • Green=UE
          </p>
        </div>
        {inactiveNodes.length > 0 && (
          <div className="flex items-center gap-2 px-3 py-2 bg-red-500/10 border border-red-500/30 rounded text-sm text-red-400">
            <AlertTriangle size={16} />
            {inactiveNodes.length} Offline
          </div>
        )}
      </div>

      <svg
        className="w-full h-96 border border-slate-700 rounded bg-gradient-to-br from-slate-900 to-slate-950"
        viewBox="0 0 900 400"
      >
        <defs>
          <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
            <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#333" strokeWidth="0.5" />
          </pattern>
        </defs>

        <rect width="900" height="400" fill="url(#grid)" opacity="0.3" />

        {topology.links && topology.links.map((link, idx) => {
          const u = topology.nodes.find(n => n.id === link.source);
          const v = topology.nodes.find(n => n.id === link.target);
          if (!u || !v) return null;

          const uActive = !inactiveNodes.includes(u.id);
          const vActive = !inactiveNodes.includes(v.id);
          const linkActive = uActive && vActive;

          const [x1, y1] = getPos(u.pos);
          const [x2, y2] = getPos(v.pos);
          const keyStr = 'link' + idx;

          return (
            <g key={keyStr}>
              <line
                x1={x1}
                y1={y1}
                x2={x2}
                y2={y2}
                stroke={linkActive ? 'rgba(59, 130, 246, 0.5)' : 'rgba(100, 100, 100, 0.2)'}
                strokeWidth={linkActive ? 3 : 1.5}
              />
              {hoveredNode === u.id || hoveredNode === v.id ? (
                <text
                  x={(x1 + x2) / 2}
                  y={(y1 + y2) / 2 - 8}
                  textAnchor="middle"
                  fontSize="10"
                  fill="#3b82f6"
                >
                  {link.cap}Mbps
                </text>
              ) : null}
            </g>
          );
        })}

        {topology.nodes && topology.nodes.map((node) => {
          const [x, y] = getPos(node.pos);
          const isInactive = inactiveNodes.includes(node.id);
          const nodeType = getNodeType(node);
          const nodeColor = getNodeColor(node);
          const isHovered = hoveredNode === node.id;
          const keyStr = 'node' + node.id;

          return (
            <g
              key={keyStr}
              onMouseEnter={() => setHoveredNode(node.id)}
              onMouseLeave={() => setHoveredNode(null)}
              onClick={() => onNodeToggle(node.id, isInactive)}
              style={{ cursor: 'pointer' }}
            >
              {!isInactive && (
                <circle
                  cx={x}
                  cy={y}
                  r="24"
                  fill="none"
                  stroke={nodeColor}
                  strokeWidth="2"
                  opacity="0.5"
                >
                  <animate
                    attributeName="opacity"
                    values="0.5;0.2;0.5"
                    dur="2s"
                    repeatCount="indefinite"
                  />
                </circle>
              )}
              <circle
                cx={x}
                cy={y}
                r="16"
                fill={nodeColor}
                opacity={isInactive ? 0.4 : 1}
                stroke={isHovered ? '#fff' : 'none'}
                strokeWidth={isHovered ? 2 : 0}
              />
              <text
                x={x}
                y={y}
                textAnchor="middle"
                dy="0.3em"
                fontSize="11"
                fontWeight="bold"
                fill={isInactive ? '#999' : '#fff'}
                pointerEvents="none"
              >
                {node.id}
              </text>
              {isInactive && (
                <circle cx={x + 12} cy={y - 12} r="4" fill="#ef4444" />
              )}
              {isHovered && (
                <g>
                  <rect
                    x={x - 35}
                    y={y - 40}
                    width="70"
                    height="36"
                    rx="4"
                    fill="#1a1a1a"
                    stroke="#3b82f6"
                    opacity="0.95"
                  />
                  <text x={x} y={y - 28} textAnchor="middle" fontSize="10" fontWeight="bold" fill="#fff" pointerEvents="none">
                    {nodeType}
                  </text>
                  <text x={x} y={y - 15} textAnchor="middle" fontSize="9" fill={isInactive ? '#ef4444' : '#10b981'} pointerEvents="none">
                    {isInactive ? 'OFFLINE' : 'ACTIVE'}
                  </text>
                </g>
              )}
            </g>
          );
        })}
      </svg>

      <div className="mt-4 grid grid-cols-4 gap-3 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#ff3131' }}></div>
          <span>CU</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#fbbf24' }}></div>
          <span>DU</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#3b82f6' }}></div>
          <span>RRH</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#10b981' }}></div>
          <span>UE</span>
        </div>
    
    </div>
  );
}
  </div >
  );
}