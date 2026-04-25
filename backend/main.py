"""
5G X-DQN Management System - REAL-TIME VISUALIZATION VERSION
Enhanced with WebSocket support for live metric streaming, interactive network control,
and Physical Signal Layer with Hardware Abstraction (RF Mode).
"""
import asyncio
import torch
from fastapi import FastAPI, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import time
import json
from environment import FiveGEnvironment
from agent import XDQNAgent
from rf_agent import RFAwareAgent

app = FastAPI(title="5G X-DQN Management System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State — default to ideal mode (backward compatible)
env = FiveGEnvironment(simulation_mode='ideal')
state_dim = env.get_state_dim() + 3  # +3 for LSTM prediction concat
action_dim = 9
agent = XDQNAgent(state_dim, action_dim)
rf_agent = None  # Created on-demand when switching to RF mode

training_status = {"status": "idle", "episode": 0,
                   "total_episodes": 100, "history": []}
sim_state = {"topology": list(env.topology.edges(data=True)), "metrics": {}}

# Real-time state for frontend
active_nodes = set(env.topology.nodes())
inactive_nodes = set()
real_time_metrics = {}
path_state = {}

# WebSocket connections manager


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to client: {e}")


manager = ConnectionManager()


class TrainingConfig(BaseModel):
    episodes: int = 100


class NodeToggleRequest(BaseModel):
    node_id: int
    active: bool


class RFModeRequest(BaseModel):
    mode: str = 'ideal'  # 'ideal' or 'realistic_rf'


def run_baseline_comparison():
    """Simulates a static baseline (no AI) for comparison."""
    baseline_env = FiveGEnvironment(simulation_mode=env.simulation_mode)
    baseline_env.reset()
    results = []
    for _ in range(100):
        _, _, _, metrics = baseline_env.step(4)
        avg_lat = np.mean([m['latency'] for m in metrics.values()])
        results.append(avg_lat)
    return float(np.mean(results))


def _get_current_agent():
    """Get the appropriate agent for current simulation mode."""
    if env.simulation_mode == 'realistic_rf' and rf_agent is not None:
        return rf_agent
    return agent


async def training_loop(episodes: int):
    """Background training loop for DQN agent with real-time metric broadcasting."""
    global training_status, real_time_metrics
    training_status["status"] = "training"
    training_status["total_episodes"] = episodes
    training_status["history"] = []

    baseline_lat = run_baseline_comparison()
    current_agent = _get_current_agent()

    for ep in range(episodes):
        state = env.reset()
        prediction = np.zeros(3)

        # Only concat prediction if state dim matches
        if len(state) + 3 == current_agent.state_dim:
            state_with_pred = np.concatenate([state, prediction])
        else:
            state_with_pred = state

        total_reward = 0
        ep_metrics = []

        for t in range(100):
            # RF-aware action selection if available
            if env.simulation_mode == 'realistic_rf' and isinstance(current_agent, RFAwareAgent):
                action = current_agent.act_with_rf_awareness(state_with_pred)
            else:
                action = current_agent.act(state_with_pred)

            next_state, reward, done, metrics = env.step(action)

            # Update prediction module
            traffic_data = [metrics[s]['throughput']
                            for s in ['eMBB', 'URLLC', 'mMTC']]
            current_agent.update_prediction_module(traffic_data)

            # Get next prediction
            if len(current_agent.traffic_history) >= 5:
                history = np.array(list(current_agent.traffic_history))
                with torch.no_grad():
                    pred_tensor = current_agent.predictor(torch.FloatTensor(
                        history[-5:]).unsqueeze(0).to(current_agent.device))
                    prediction = pred_tensor.cpu().numpy().flatten()

            if len(next_state) + 3 == current_agent.state_dim:
                next_state_with_pred = np.concatenate([next_state, prediction])
            else:
                next_state_with_pred = next_state

            current_agent.remember(state_with_pred, action, reward,
                           next_state_with_pred, done)
            current_agent.train()

            state_with_pred = next_state_with_pred
            total_reward += reward
            ep_metrics.append(np.mean([m['latency']
                              for m in metrics.values()]))

            # Store real-time metrics for WebSocket broadcast
            real_time_metrics = {
                "timestamp": time.time(),
                "episode": ep,
                "step": t,
                "reward": float(reward),
                "simulation_mode": env.simulation_mode,
                "metrics": {
                    s: {
                        'latency': float(metrics[s]['latency']),
                        'throughput': float(metrics[s]['throughput']),
                        'packet_loss': float(metrics[s]['packet_loss']),
                        'congestion': float(metrics[s]['congestion_level']),
                        'allocated_bw': float(metrics[s]['allocated_bw']),
                        'traffic_load': float(metrics[s]['traffic_load']),
                        'phy_factor': float(metrics[s]['phy_factor']),
                    }
                    for s in metrics
                },
                "active_nodes": list(active_nodes),
                "inactive_nodes": list(inactive_nodes)
            }

            # Add RF metrics when in RF mode
            if env.simulation_mode == 'realistic_rf':
                rf_metrics = env._rf_metrics_cache
                if rf_metrics:
                    # Serialize link metrics (convert tuple keys to strings)
                    serialized_links = {}
                    for (u, v), data in rf_metrics.get('links', {}).items():
                        serialized_links[f"{u}-{v}"] = data

                    real_time_metrics["rf_metrics"] = {
                        "links": serialized_links,
                        "nodes": {
                            str(k): v for k, v in rf_metrics.get('nodes', {}).items()
                        },
                    }

                    # Add per-slice RF data
                    for s in metrics:
                        if 'avg_snr' in metrics[s]:
                            real_time_metrics["metrics"][s]['avg_snr'] = float(metrics[s].get('avg_snr', 0))
                            real_time_metrics["metrics"][s]['avg_interference'] = float(metrics[s].get('avg_interference', 0))
                            real_time_metrics["metrics"][s]['rf_factor'] = float(metrics[s].get('rf_factor', 1.0))

            # Broadcast to all connected WebSocket clients
            await manager.broadcast({
                "type": "metrics_update",
                "data": real_time_metrics
            })

            if done:
                break

        current_agent.update_target_model()

        avg_lat = np.mean(ep_metrics)
        training_status["episode"] = ep + 1
        training_status["history"].append({
            "episode": ep,
            "reward": float(total_reward),
            "latency": float(avg_lat),
            "baseline_latency": baseline_lat
        })

        # Broadcast episode complete
        await manager.broadcast({
            "type": "episode_complete",
            "data": training_status["history"][-1]
        })

        await asyncio.sleep(0.01)

    training_status["status"] = "completed"
    await manager.broadcast({
        "type": "training_complete",
        "data": training_status
    })


@app.post("/train")
async def start_training(config: TrainingConfig, background_tasks: BackgroundTasks):
    """Start DQN training."""
    background_tasks.add_task(training_loop, config.episodes)
    return {"message": "Training started", "episodes": config.episodes}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics streaming."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "node_toggle":
                node_id = message.get("node_id")
                toggle = message.get("toggle", True)

                if toggle:
                    if node_id in inactive_nodes:
                        inactive_nodes.remove(node_id)
                    active_nodes.add(node_id)
                else:
                    if node_id in active_nodes:
                        active_nodes.remove(node_id)
                    inactive_nodes.add(node_id)

                # Broadcast node status change
                await manager.broadcast({
                    "type": "node_status_change",
                    "data": {
                        "node_id": node_id,
                        "active": toggle,
                        "active_nodes": list(active_nodes),
                        "inactive_nodes": list(inactive_nodes)
                    }
                })

            elif message.get("type") == "get_snapshot":
                # Send current state snapshot
                snapshot_data = {
                    "status": training_status,
                    "metrics": real_time_metrics,
                    "active_nodes": list(active_nodes),
                    "inactive_nodes": list(inactive_nodes),
                    "simulation_mode": env.simulation_mode,
                }
                await websocket.send_json({
                    "type": "snapshot",
                    "data": snapshot_data
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.post("/node/toggle")
async def toggle_node(request: NodeToggleRequest):
    """Toggle node active/inactive status."""
    if request.active:
        if request.node_id in inactive_nodes:
            inactive_nodes.remove(request.node_id)
        active_nodes.add(request.node_id)
    else:
        if request.node_id in active_nodes:
            active_nodes.remove(request.node_id)
        inactive_nodes.add(request.node_id)

    # Broadcast the change
    await manager.broadcast({
        "type": "node_status_change",
        "data": {
            "node_id": request.node_id,
            "active": request.active,
            "active_nodes": list(active_nodes),
            "inactive_nodes": list(inactive_nodes)
        }
    })

    return {
        "node_id": request.node_id,
        "active": request.active,
        "active_nodes": list(active_nodes),
        "inactive_nodes": list(inactive_nodes)
    }


@app.get("/status")
async def get_status():
    """Get current training status."""
    return {
        **training_status,
        "active_nodes": list(active_nodes),
        "inactive_nodes": list(inactive_nodes),
        "simulation_mode": env.simulation_mode,
    }


@app.get("/topology")
async def get_topology():
    """Get network topology information with node status and RF attributes."""
    nodes_data = []
    for n in env.topology.nodes:
        node_info = {
            "id": n,
            "pos": env.positions[n],
            "active": n in active_nodes,
            "type": "CU" if n == 0 else "DU" if n < 3 else "RRH" if n < 6 else "UE"
        }
        # Add pipeline info in RF mode
        if env.simulation_mode == 'realistic_rf' and n in env.node_pipelines:
            pipeline = env.node_pipelines[n]
            node_info["pipeline"] = pipeline.get_current_signal_quality()
        nodes_data.append(node_info)

    links_data = []
    for u, v in env.topology.edges():
        link_info = {
            "source": u,
            "target": v,
            "cap": env.topology[u][v].get('cap', 100),
            "lat": env.topology[u][v].get('lat', 1),
            "active": (u in active_nodes) and (v in active_nodes)
        }
        # Add waveguide info in RF mode
        if env.simulation_mode == 'realistic_rf' and (u, v) in env.waveguides:
            wg = env.waveguides[(u, v)]
            link_info["waveguide"] = wg.to_dict()
        links_data.append(link_info)

    return {
        "nodes": nodes_data,
        "links": links_data,
        "simulation_mode": env.simulation_mode,
    }


@app.get("/metrics/current")
async def get_current_metrics():
    """Get current network metrics."""
    return {
        "metrics": real_time_metrics,
        "status": {
            "active_nodes": list(active_nodes),
            "inactive_nodes": list(inactive_nodes),
            "simulation_mode": env.simulation_mode,
        }
    }


# ─────────────────────────────────────────────
# RF Mode Endpoints (NEW)
# ─────────────────────────────────────────────

@app.get("/rf/mode")
async def get_rf_mode():
    """Get current simulation mode."""
    return {
        "mode": env.simulation_mode,
        "state_dim": env.get_state_dim(),
        "rf_active": env.simulation_mode == 'realistic_rf',
    }


@app.post("/rf/mode")
async def set_rf_mode(request: RFModeRequest):
    """Switch simulation mode between ideal and realistic_rf."""
    global agent, rf_agent, state_dim

    old_mode = env.simulation_mode
    env.set_simulation_mode(request.mode)
    state_dim = env.get_state_dim() + 3  # +3 for LSTM prediction concat

    # Create appropriate agent for the mode
    if request.mode == 'realistic_rf':
        if rf_agent is None:
            rf_agent = RFAwareAgent(state_dim=state_dim, action_dim=action_dim)
    elif request.mode == 'ideal':
        # Reset to base agent with standard state dim
        agent = XDQNAgent(state_dim=state_dim, action_dim=action_dim)

    # Broadcast mode change
    await manager.broadcast({
        "type": "rf_mode_change",
        "data": {
            "mode": env.simulation_mode,
            "state_dim": state_dim,
            "old_mode": old_mode,
        }
    })

    return {
        "mode": env.simulation_mode,
        "state_dim": state_dim,
        "previous_mode": old_mode,
        "message": f"Switched from {old_mode} to {request.mode}",
    }


@app.get("/rf/metrics")
async def get_rf_metrics():
    """Get per-link and per-node RF metrics (realistic_rf mode only)."""
    if env.simulation_mode != 'realistic_rf':
        return {
            "message": "RF metrics only available in realistic_rf mode",
            "mode": env.simulation_mode,
            "links": {},
            "nodes": {},
        }

    rf = env._get_rf_metrics()

    # Serialize link keys (tuples → strings)
    serialized_links = {}
    for (u, v), data in rf.get('links', {}).items():
        serialized_links[f"{u}-{v}"] = data

    serialized_nodes = {
        str(k): v for k, v in rf.get('nodes', {}).items()
    }

    return {
        "mode": env.simulation_mode,
        "links": serialized_links,
        "nodes": serialized_nodes,
        "snr_violations": [
            {"source": u, "target": v}
            for u, v in env.get_snr_threshold_violations()
        ],
        "interference_spikes": [
            {"source": u, "target": v}
            for u, v in env.get_interference_spikes()
        ],
    }


@app.get("/rf/pipeline/{node_id}")
async def get_node_pipeline(node_id: int):
    """Get signal pipeline state for a specific node."""
    if env.simulation_mode != 'realistic_rf':
        return {
            "message": "Pipeline info only available in realistic_rf mode",
            "node_id": node_id,
        }

    pipeline = env.node_pipelines.get(node_id)
    if pipeline is None:
        return {"error": f"Node {node_id} not found", "node_id": node_id}

    return pipeline.to_dict()


@app.get("/")
async def root():
    """Root endpoint - redirect to docs."""
    return {
        "message": "5G X-DQN Management System",
        "docs": "http://localhost:8000/docs",
        "status": training_status["status"],
        "simulation_mode": env.simulation_mode,
    }


@app.get("/info")
async def get_system_info():
    """Get system information."""
    return {
        "title": "5G X-DQN Management System",
        "version": "2.0",
        "status": "working",
        "simulation_mode": env.simulation_mode,
        "components": {
            "environment": "5G C-RAN",
            "agent": "DQN with LSTM",
            "training": "Live",
            "hardware_layer": "Active" if env.simulation_mode == 'realistic_rf' else "Inactive",
            "modules": ["Signal Model", "Waveguide", "Filter", "Amplifier", "Oscillator", "Pipeline"],
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*80)
    print("5G X-DQN Management System - ACTIVE")
    print("="*80)
    print(f"Simulation Mode: {env.simulation_mode}")
    print("Starting API server...")
    print("Available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("="*80 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
