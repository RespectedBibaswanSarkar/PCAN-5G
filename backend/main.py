"""
5G X-DQN Management System - REAL-TIME VISUALIZATION VERSION
Enhanced with WebSocket support for live metric streaming and interactive network control.
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

app = FastAPI(title="5G X-DQN Management System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State
env = FiveGEnvironment()
state_dim = 21
action_dim = 9
agent = XDQNAgent(state_dim, action_dim)

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


def run_baseline_comparison():
    """Simulates a static baseline (no AI) for comparison."""
    baseline_env = FiveGEnvironment()
    baseline_env.reset()
    results = []
    for _ in range(100):
        _, _, _, metrics = baseline_env.step(4)
        avg_lat = np.mean([m['latency'] for m in metrics.values()])
        results.append(avg_lat)
    return float(np.mean(results))


async def training_loop(episodes: int):
    """Background training loop for DQN agent with real-time metric broadcasting."""
    global training_status, real_time_metrics
    training_status["status"] = "training"
    training_status["total_episodes"] = episodes
    training_status["history"] = []

    baseline_lat = run_baseline_comparison()

    for ep in range(episodes):
        state = env.reset()
        prediction = np.zeros(3)
        state_with_pred = np.concatenate([state, prediction])

        total_reward = 0
        ep_metrics = []

        for t in range(100):
            action = agent.act(state_with_pred)
            next_state, reward, done, metrics = env.step(action)

            # Update prediction module
            traffic_data = [metrics[s]['throughput']
                            for s in ['eMBB', 'URLLC', 'mMTC']]
            agent.update_prediction_module(traffic_data)

            # Get next prediction
            if len(agent.traffic_history) >= 5:
                history = np.array(list(agent.traffic_history))
                with torch.no_grad():
                    pred_tensor = agent.predictor(torch.FloatTensor(
                        history[-5:]).unsqueeze(0).to(agent.device))
                    prediction = pred_tensor.cpu().numpy().flatten()

            next_state_with_pred = np.concatenate([next_state, prediction])

            agent.remember(state_with_pred, action, reward,
                           next_state_with_pred, done)
            agent.train()

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
                "metrics": {
                    s: {
                        'latency': float(metrics[s]['latency']),
                        'throughput': float(metrics[s]['throughput']),
                        'packet_loss': float(metrics[s]['packet_loss']),
                        'congestion': float(metrics[s]['congestion_level']),
                        'allocated_bw': float(metrics[s]['allocated_bw']),
                        'traffic_load': float(metrics[s]['traffic_load']),
                        'phy_factor': float(metrics[s]['phy_factor'])
                    }
                    for s in metrics
                },
                "active_nodes": list(active_nodes),
                "inactive_nodes": list(inactive_nodes)
            }

            # Broadcast to all connected WebSocket clients
            await manager.broadcast({
                "type": "metrics_update",
                "data": real_time_metrics
            })

            if done:
                break

        agent.update_target_model()

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
                await websocket.send_json({
                    "type": "snapshot",
                    "data": {
                        "status": training_status,
                        "metrics": real_time_metrics,
                        "active_nodes": list(active_nodes),
                        "inactive_nodes": list(inactive_nodes)
                    }
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
        "inactive_nodes": list(inactive_nodes)
    }


@app.get("/topology")
async def get_topology():
    """Get network topology information with node status."""
    return {
        "nodes": [
            {
                "id": n,
                "pos": env.positions[n],
                "active": n in active_nodes,
                "type": "CU" if n == 0 else "DU" if n < 3 else "RRH" if n < 6 else "UE"
            }
            for n in env.topology.nodes
        ],
        "links": [
            {
                "source": u,
                "target": v,
                "cap": env.topology[u][v].get('cap', 100),
                "lat": env.topology[u][v].get('lat', 1),
                "active": (u in active_nodes) and (v in active_nodes)
            }
            for u, v in env.topology.edges()
        ]
    }


@app.get("/metrics/current")
async def get_current_metrics():
    """Get current network metrics."""
    return {
        "metrics": real_time_metrics,
        "status": {
            "active_nodes": list(active_nodes),
            "inactive_nodes": list(inactive_nodes)
        }
    }


@app.get("/")
async def root():
    """Root endpoint - redirect to docs."""
    return {
        "message": "5G X-DQN Management System",
        "docs": "http://localhost:8000/docs",
        "status": training_status["status"]
    }


@app.get("/info")
async def get_system_info():
    """Get system information."""
    return {
        "title": "5G X-DQN Management System",
        "version": "1.0",
        "status": "working",
        "components": {
            "environment": "5G C-RAN",
            "agent": "DQN with LSTM",
            "training": "Live"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*80)
    print("5G X-DQN Management System - ACTIVE")
    print("="*80)
    print("Starting API server...")
    print("Available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("="*80 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
