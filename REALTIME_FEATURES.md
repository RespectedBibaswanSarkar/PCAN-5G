# 5G X-DQN Real-Time Visualization System

## Overview

The system has been enhanced with comprehensive real-time visualization capabilities powered by **WebSocket** bidirectional communication, interactive network topology control, and live metric streaming. This document describes all new features and how to use them.

---

## 🎯 Key Features

### 1. **Real-Time WebSocket Communication**
- **Bidirectional WebSocket Connection** (`/ws` endpoint)
- **Live Metric Streaming**: All simulation metrics pushed to frontend in real-time
- **Automatic Reconnection**: Intelligent fallback to polling if WebSocket fails
- **Sub-100ms Latency**: Near-instantaneous metric updates

#### WebSocket Message Types:
- `metrics_update`: Real-time network and slice metrics
- `episode_complete`: Notification when training episode finishes
- `training_complete`: Notification when full training completes
- `node_status_change`: Node activation/deactivation events
- `snapshot`: Full system state snapshot on request

---

### 2. **Interactive Network Topology Visualization**

#### Features:
- **Node Status Indicators**:
  - 🔴 **CU (Core)** - Red, center core unit
  - 🟡 **DU (Distributed)** - Amber, distributed units
  - 🔵 **RRH (Radio)** - Blue, radio remote heads
  - 🟢 **UE (User Equipment)** - Green, user devices

- **Interactive Node Control**:
  - **Click Nodes**: Simulate outages by clicking on network nodes
  - **Toggle On/Off**: Turn nodes offline/online to test rerouting
  - **Hover Tooltips**: See node details on hover
  - **Status Indicator**: Red dot indicates offline nodes
  - **Automatic Rerouting**: System automatically reroutes traffic around failed nodes

- **Real-Time Visualization**:
  - **Active/Inactive Status**: Visual indication of node operational state
  - **Signal Strength Visualization**: Link opacity indicates signal quality
  - **Animated Data Particles**: Colored particles show traffic flow (eMBB=Blue, URLLC=Red, mMTC=Green)
  - **Grid Background**: Professional NS3-style visualization
  - **Glowing Effects**: Active nodes pulse with glow animation
  - **Hover States**: Links show capacity and latency info on node hover

---

### 3. **Real-Time Charts**

Four comprehensive real-time charts display live metrics:

#### Chart 1: **Latency (ms)**
- Tracks latency for each slice (eMBB, URLLC, mMTC)
- Updates every step
- Line chart with 30-step window

#### Chart 2: **Throughput (Mbps)**
- Shows effective capacity for eMBB and mMTC
- Area chart for trend visualization
- Real-time updates

#### Chart 3: **Packet Loss**
- Displays packet loss percentage for all slices
- Highlights URLLC as "Critical"
- Identifies network congestion points

#### Chart 4: **Congestion & PHY Factor**
- URLLC congestion levels
- Physical layer factor (signal quality indicator)
- Combined view for optimization insights

---

### 4. **Real-Time Metrics Panel**

Live system status display showing:
- **Average Latency (ms)**: Current network latency
- **Reward**: Current training reward signal
- **Episode Progress**: Displays episode count and total
- **Inactive Nodes**: Shows offline nodes in real-time
- **Progress Bar**: Visual training progress indicator

---

### 5. **Node Control Panel**

Interactive grid of all network nodes:
- **Visual Status**: Green (Active) / Red (Offline)
- **Quick Toggle**: Click any node to simulate outage
- **Real-Time Feedback**: Immediate visual update

---

### 6. **Training Progress Chart**

Displays episode-level metrics:
- **Reward Trend**: Training reward improvement over episodes
- **Latency Trend**: Network latency optimization
- **Historical View**: See full training progression

---

## 🚀 How to Use

### Starting the System

1. **Start Backend**:
   ```bash
   cd backend
   python main.py
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access Dashboard**:
   - Navigate to `http://localhost:5173` (or the port shown in terminal)
   - System auto-starts training with 20 episodes

---

### Simulating Network Faults

#### Method 1: Click on Network Topology
1. Navigate to the network topology visualization (top right)
2. **Click any node** to toggle its status
3. The node will turn gray and go offline
4. Traffic automatically reroutes around the failed node
5. **Click again** to bring the node back online

#### Method 2: Use Node Control Panel
1. Locate the **NODE CONTROL** panel (left sidebar)
2. Click any node button (green=online, red=offline)
3. Status updates in real-time across all visualizations

---

### Monitoring Real-Time Metrics

#### Live Metrics Panel (Left Sidebar)
- Shows current network statistics
- Updates every step
- Color-coded for easy interpretation

#### Real-Time Charts (Right Panel)
- **Four charts** display different metric aspects
- Charts scroll horizontally to show 30-step history
- Tooltips show exact values on hover

#### Training Progress
- Bottom chart shows episode-level trends
- Observe how reward improves over training episodes
- Compare with baseline latency reference

---

### Adjusting Training Parameters

1. Click **PARAMETERS** tab in System Control
2. Available parameters:
   - `slice_priority`: Service priority levels
   - `bandwidth_allocation`: Resource distribution
   - `traffic_weights`: Traffic mix simulation
3. Changes apply to next training episode

---

## 📊 Metric Explanations

### Real-Time Metrics (Per-Step)

| Metric | Range | Interpretation |
|--------|-------|-----------------|
| **Latency (ms)** | 0-50 | Lower is better; URLLC target: 1ms |
| **Throughput (Mbps)** | 0-200 | Higher is better; eMBB prefers high throughput |
| **Packet Loss** | 0-1 | Lower is better; URLLC intolerant of loss |
| **Congestion** | 0-1 | Lower is better; shows queue buildup |
| **PHY Factor** | 0.1-1.5 | Signal quality multiplier |
| **Reward** | -50 to +50 | Agent performance; higher = better optimization |

### Node Types

| Type | Role | Color |
|------|------|-------|
| **CU** | Central processing | Red |
| **DU** | Distributed processing | Amber |
| **RRH** | Radio transmission | Blue |
| **UE** | User endpoint | Green |

---

## 🔌 WebSocket Connection Details

### Endpoint
- **URL**: `ws://localhost:8000/ws`
- **Auto-Reconnects**: Up to 5 attempts with 3-second delays
- **Fallback**: Automatic polling if WebSocket unavailable

### Message Format (Client to Server)

```json
{
  "type": "node_toggle",
  "node_id": 3,
  "toggle": true
}
```

### Message Format (Server to Client)

```json
{
  "type": "metrics_update",
  "data": {
    "timestamp": 1681234567,
    "episode": 5,
    "step": 42,
    "reward": 23.45,
    "metrics": {
      "eMBB": {
        "latency": 5.2,
        "throughput": 120.5,
        "packet_loss": 0.01,
        "congestion": 0.3,
        "allocated_bw": 100,
        "traffic_load": 120,
        "phy_factor": 1.2
      },
      ...
    },
    "active_nodes": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    "inactive_nodes": []
  }
}
```

---

## 🎬 Visual Design

### NS3-Inspired Design Elements
- **Professional Color Scheme**: Dark background with neon red accents
- **Grid Background**: Subtle grid pattern like NS3 simulator
- **Real-Time Animations**: Smooth transitions and data flow particles
- **Responsive Layout**: Adapts from mobile to 4K displays
- **Typography**: Monospace font for metric values

### Color Coding
- 🔴 **Red (#ff3131)**: Critical elements, CU nodes, errors
- 🟡 **Amber (#fbbf24)**: Warnings, DU nodes
- 🔵 **Blue (#3b82f6)**: eMBB traffic, RRH nodes
- 🟢 **Green (#10b981)**: mMTC traffic, UE nodes

---

## ⚡ Performance Optimization

### Real-Time Updates
- **Metrics History**: Stores latest 100 data points (auto-prunes older data)
- **WebSocket Batching**: Metrics sent at step granularity (not sub-millisecond)
- **Chart Optimization**: Recharts configured for smooth animation
- **Polling Fallback**: 500ms polling interval if WebSocket unavailable

### Network Efficiency
- **Compressed Messages**: JSON payloads ~500 bytes each
- **Selective Rendering**: SVG optimized with `isAnimationActive={false}`
- **Debounced Updates**: UI updates coalesced per render cycle

---

## 🔧 API Reference

### REST Endpoints (Existing)

```
GET  /topology          # Network topology structure
GET  /status            # Current training status
GET  /metrics/current   # Latest real-time metrics
POST /train             # Start training with episodes count
POST /node/toggle       # Toggle node active/inactive
```

### WebSocket Endpoint (New)

```
WS   /ws                # Bidirectional metric streaming
```

---

## 📋 Troubleshooting

### WebSocket Not Connecting?
- Check backend is running (`http://localhost:8000/docs`)
- Check no firewall blocking port 8000
- System auto-falls back to polling

### Charts Not Updating?
- Ensure training is running (check status indicator)
- Check metrics history has data points (need at least 1 step)
- Try refreshing page

### Nodes Not Toggling?
- Verify WebSocket connected or polling active
- Check browser console for errors
- Ensure nodes are valid IDs (0-9)

### Performance Issues?
- Close unused browser tabs
- Try different browser
- Reduce number of parallel connections

---

## 🎯 Use Cases

### 1. **Network Resilience Testing**
- Simulate cascading node failures
- Observe automatic rerouting
- Measure recovery time

### 2. **Slice Performance Validation**
- Monitor eMBB, URLLC, mMTC metrics separately
- Test QoS compliance
- Validate SLA requirements

### 3. **Real-Time Optimization Verification**
- Watch DQN agent adapt to faults
- Compare with baseline policies
- Validate reward convergence

### 4. **Presentation & Demonstration**
- Live visualize 5G network behavior
- Show real-time adaptation
- Demonstrate AI orchestration

---

## 📝 Configuration

### Backend (main.py)
- WebSocket reconnection attempts: `maxReconnectAttempts = 5`
- Reconnection delay: `reconnectDelay = 3000ms`

### Frontend (RealtimeCharts)
- Chart window size: `30` steps
- Update frequency: WebSocket (event-driven) or 500ms polling

### Environment Variables
- `API_BASE_URL`: Backend URL (default: `http://localhost:8000`)
- `WS_BASE_URL`: WebSocket URL (default: `ws://localhost:8000`)

---

## 🚀 Advanced Usage

### Custom Metrics Integration
To add new metrics:

1. **Backend**: Add to `real_time_metrics` dict in `main.py`
2. **Frontend**: Add to `displayData` computation in `RealtimeCharts.jsx`
3. **Chart**: Create new chart component following the same pattern

### Custom Node Actions
To add node-specific behaviors:

1. **Backend**: Extend WebSocket message types
2. **Frontend**: Add handlers in `App.jsx` WebSocket subscription
3. **Topology**: Add visual feedback for node actions

---

## 📚 Further Reading

- **5G Slicing**: See [5G Architecture Documentation]
- **DQN Training**: See [Agent Documentation](backend/README_RESEARCH_PLATFORM.md)
- **Network Topology**: See [Environment Documentation](backend/environment.py)

---

## ✅ Verification Checklist

- [ ] Backend running and accessible at `http://localhost:8000`
- [ ] Frontend running and accessible at `http://localhost:5173`
- [ ] WebSocket connected (check status in header)
- [ ] Real-time charts updating every step
- [ ] Node controls working (click topology to toggle)
- [ ] Metrics panel showing current values
- [ ] Training progress visible in bottom chart
- [ ] Auto-training started and progressing

---

## 📞 Support & Issues

For issues or questions:
1. Check troubleshooting section above
2. Review browser console for errors
3. Check backend logs for WebSocket issues
4. Ensure all dependencies installed: `npm install && pip install -r requirements.txt`

---

**Last Updated**: April 2026  
**Version**: 2.0 (Real-Time Visualization Release)
