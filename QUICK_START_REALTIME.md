# 🚀 Quick Start: Real-Time Visualization

## ⚡ 5-Minute Setup

### 1. **Start the Backend**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

Expected output:
```
================================================================================
5G X-DQN Management System - ACTIVE
================================================================================
Starting API server...
Available at: http://localhost:8000
API Documentation: http://localhost:8000/docs
================================================================================
```

### 2. **Start the Frontend** (in a new terminal)
```bash
cd frontend
npm install
npm run dev
```

Expected output:
```
  VITE v5.1.6  ready in *** ms

  ➜  Local:   http://localhost:5173/
```

### 3. **Open in Browser**
Navigate to: **http://localhost:5173**

✅ **Dashboard is now live with real-time visualization!**

---

## 🎮 Basic Controls

### Viewing Real-Time Metrics
- **Live Charts**: Right panel shows 4 real-time metric charts
- **Metrics Panel**: Left sidebar displays current network stats
- **Network Topology**: Top-right shows network with animated traffic

### Simulating Network Failures

**Option 1: Click Network Topology**
1. Find the topology visualization (top-right area)
2. **Click any colored node** to turn it offline
3. Node turns gray, traffic reroutes automatically
4. Click again to bring online

**Option 2: Use Control Panel**
1. Scroll down left sidebar
2. Find **NODE CONTROL** section
3. Click node buttons to toggle online/offline

**Real-time Feedback:**
- Inactive nodes count appears in red at top-right
- Metrics update immediately
- Charts show impact of failure

---

## 📊 Understanding the Dashboard

### Left Column (Controls)
- **System Control**: Start/stop training
- **Live Metrics**: Current network performance
- **Node Control**: Toggle nodes on/off

### Right Column (Visualizations)
- **Network Topology**: Live 5G network with traffic flow
- **Real-Time Charts**: 4 charts showing different metrics
- **Training Progress**: Episode-level trends

### Color Meanings

| Color | Element | Meaning |
|-------|---------|---------|
| 🔴 Red | CU Node | Core network unit |
| 🟡 Amber | DU Node | Distributed processing |
| 🔵 Blue | RRH Node / eMBB | Base station / Broadband traffic |
| 🟢 Green | UE Node / mMTC | User device / Machine-type traffic |
| ⚫ Gray | Any Node | Offline/Inactive |

---

## 🎯 What to Watch

### Real-Time Metrics Charts

**1. Latency Chart**
- Lines show latency for each service slice
- Lower is better
- URLLC (red) should stay near 1ms

**2. Throughput Chart**
- Area shows available bandwidth
- eMBB (blue) prefers high throughput
- mMTC (green) needs minimal bandwidth

**3. Packet Loss Chart**
- Shows loss percentage
- Should be near 0%
- URLLC must have zero loss

**4. Congestion Chart**
- Shows queue buildup
- PHY factor shows signal quality
- Lower congestion = better performance

### Network Topology
- **Pulsing glow** around active nodes
- **Animated colored dots** show traffic moving (eMBB=Blue, URLLC=Red, mMTC=Green)
- **Link opacity** indicates signal strength
- **Hover info** shows link capacity and latency

---

## 🔧 Common Tasks

### Start Training with Custom Episodes
1. Click **EXPERIMENTS** tab
2. Change **Target Episodes** field
3. Click **Start Training**

### Check Current Network Status
- Look at **Live Metrics** panel on left
- Check node status (green vs gray)
- View real-time charts on right

### Monitor Specific Slice Performance
1. Look at the **Real-Time Charts**
2. Each chart shows metrics for eMBB, URLLC, mMTC
3. Color-coded: Blue for eMBB, Red for URLLC, Green for mMTC

### Test Network Resilience
1. Start training
2. Wait for network to stabilize (watch charts)
3. Click a node to simulate failure
4. Observe:
   - Immediate metric spikes
   - Automatic rerouting (visible in charts)
   - System recovery time
5. Toggle node back online
6. Watch performance normalize

---

## 🟢 Success Indicators

✅ **System is working correctly when:**
- [ ] Real-time charts update every step (smooth motion)
- [ ] Node controls respond immediately on click
- [ ] Inactive node count updates in real-time
- [ ] Network topology shows animated traffic particles
- [ ] No console errors (open DevTools: F12)
- [ ] WebSocket connection shows "Connected" status

---

## ⚠️ Troubleshooting

### Charts Not Updating?
**Solution:**
1. Wait 1-2 seconds for training to start
2. Refresh page (F5)
3. Check browser console (F12) for errors

### WebSocket Not Connected?
**It's OK!** System automatically falls back to polling every 500ms

**To reconnect manually:**
1. Refresh page
2. Check backend is running

### Nodes Not Responding?
**Solution:**
1. Click topology or control panel
2. Wait for immediate update
3. If nothing happens, refresh and try again

### Backend Shows Errors?
**Solution:**
1. Ensure Python 3.8+: `python --version`
2. Install requirements: `pip install -r requirements.txt`
3. Restart backend: `python main.py`

---

## 💡 Pro Tips

1. **Rapid Testing**: Toggle multiple nodes sequentially to test cascading failures
2. **Parameter Control**: Use PARAMETERS tab to test different configurations
3. **Performance Analysis**: Watch reward chart to see AI optimization
4. **Real-Time Comparison**: Observe latency improvement as training progresses
5. **Visual Debugging**: Pause on interesting moments and analyze charts

---

## 📊 Example Workflow

### Step 1: Observe Normal Operation (30 seconds)
- Watch charts update smoothly
- Observe reward increasing
- Note current latency baseline

### Step 2: Simulate Failure (nodes 3 and 4)
- Click node 3 in topology → goes gray
- Click node 4 → also goes gray
- Observe chart spikes

### Step 3: Watch Recovery
- Monitor latency recovery (should drop back down)
- Watch reward stabilize
- See rerouting in traffic particles

### Step 4: Restore Nodes
- Click node 3 → turns green/blue/etc
- Click node 4 → returns to normal
- System optimizes with new path

---

## 🔗 Links & Resources

**Dashboard**: http://localhost:5173  
**API Docs**: http://localhost:8000/docs  
**WebSocket**: ws://localhost:8000/ws  

**Documentation**:
- [Full Feature Documentation](./REALTIME_FEATURES.md)
- [Backend Architecture](./backend/README_RESEARCH_PLATFORM.md)
- [Network Environment](./backend/environment.py)

---

## 🎓 Learning Path

1. ✅ **Start System** (you are here)
2. 📊 **Observe Normal Operation** (watch for 1 minute)
3. 🔴 **Trigger Failures** (click nodes to test)
4. 📈 **Monitor Recovery** (watch metrics normalize)
5. 🧠 **Understand AI Adaptation** (compare different failure scenarios)
6. 💾 **Read Full Docs** (for advanced usage)

---

## ❓ Still Having Issues?

1. **Check backend running**: Visit `http://localhost:8000` in browser
2. **Check frontend running**: Visit `http://localhost:5173` in browser
3. **View console errors**: Press F12 in browser, check Console tab
4. **Read logs**: Check terminal output for error messages
5. **Restart everything**: Stop both services, restart backend, then frontend

---

🎉 **Enjoy real-time 5G network visualization!**

Need help? Check [REALTIME_FEATURES.md](./REALTIME_FEATURES.md) for comprehensive documentation.
