"""
5G X-DQN Management System - SIMPLIFIED VERSION (Working)
Restored to original working state with basic training functionality.
"""
import asyncio
import torch
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import time
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


class TrainingConfig(BaseModel):
    episodes: int = 100


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
    """Background training loop for DQN agent."""
    global training_status
    training_status["status"] = "training"
    training_status["total_episodes"] = episodes
    training_status["history"] = []

    baseline_lat = run_baseline_comparison()

    for ep in range(episodes):
        state = env.reset()
        # Initial prediction (zeros)
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

        # Slow down slightly for frontend visualization sync if needed
        await asyncio.sleep(0.01)

    training_status["status"] = "completed"


@app.post("/train")
async def start_training(config: TrainingConfig, background_tasks: BackgroundTasks):
    """Start DQN training."""
    background_tasks.add_task(training_loop, config.episodes)
    return {"message": "Training started", "episodes": config.episodes}


@app.get("/status")
async def get_status():
    """Get current training status."""
    return training_status


@app.get("/topology")
async def get_topology():
    """Get network topology information."""
    return {
        "nodes": [{"id": n, "pos": env.positions[n]} for n in env.topology.nodes],
        "links": [{"source": u, "target": v} for u, v in env.topology.edges()]
    }


@app.get("/metrics/current")
async def get_current_metrics():
    """Get current network metrics."""
    return sim_state


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
