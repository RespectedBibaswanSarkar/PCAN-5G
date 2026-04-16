import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from collections import deque

class CongestionPredictor(nn.Module):
    """
    LSTM based prediction module for next-step traffic load.
    """
    def __init__(self, input_dim, hidden_dim=32):
        super(CongestionPredictor, self).__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, input_dim)
        
    def forward(self, x):
        # x shape: (batch, seq_len, input_dim)
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])

class QNetwork(nn.Module):
    """
    DQN Architecture for Joint Cross-Layer Decisions.
    """
    def __init__(self, state_dim, action_dim):
        super(QNetwork, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim)
        )
        
    def forward(self, x):
        return self.network(x)

class XDQNAgent:
    def __init__(self, state_dim, action_dim):
        self.state_dim = state_dim
        self.action_dim = action_dim
        
        # Hyperparameters
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.lr = 0.001
        self.batch_size = 32
        self.memory = deque(maxlen=2000)
        
        # Models
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = QNetwork(state_dim, action_dim).to(self.device)
        self.target_model = QNetwork(state_dim, action_dim).to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
        
        # LSTM module for congestion prediction (Bonus Module)
        # We predict traffic load for 3 slices
        self.predictor = CongestionPredictor(input_dim=3).to(self.device)
        self.predictor_opt = optim.Adam(self.predictor.parameters(), lr=0.005)
        self.traffic_history = deque(maxlen=10)

        self.update_target_model()

    def update_target_model(self):
        self.target_model.load_state_dict(self.model.state_dict())

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_dim)
        
        state_t = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            q_values = self.model(state_t)
        return torch.argmax(q_values).item()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train(self):
        if len(self.memory) < self.batch_size:
            return 0
        
        minibatch = random.sample(self.memory, self.batch_size)
        states = torch.FloatTensor([m[0] for m in minibatch]).to(self.device)
        actions = torch.LongTensor([m[1] for m in minibatch]).unsqueeze(1).to(self.device)
        rewards = torch.FloatTensor([m[2] for m in minibatch]).to(self.device)
        next_states = torch.FloatTensor([m[3] for m in minibatch]).to(self.device)
        dones = torch.FloatTensor([float(m[4]) for m in minibatch]).to(self.device)

        # Q-Learning update
        current_q = self.model(states).gather(1, actions)
        next_q = self.target_model(next_states).max(1)[0].detach()
        target_q = rewards + (1 - dones) * self.gamma * next_q
        
        loss = nn.MSELoss()(current_q.squeeze(), target_q)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
            
        return loss.item()

    def update_prediction_module(self, traffic_data):
        """
        Updates the LSTM with recent traffic load data.
        traffic_data: list of 3 items [eMBB_load, URLLC_load, mMTC_load]
        """
        self.traffic_history.append(traffic_data)
        if len(self.traffic_history) < 5:
            return 0
            
        history = np.array(list(self.traffic_history))
        x = torch.FloatTensor(history[:-1]).unsqueeze(0).to(self.device)
        y = torch.FloatTensor(history[-1]).unsqueeze(0).to(self.device)
        
        pred = self.predictor(x)
        loss = nn.MSELoss()(pred, y)
        
        self.predictor_opt.zero_grad()
        loss.backward()
        self.predictor_opt.step()
        
        return loss.item()
