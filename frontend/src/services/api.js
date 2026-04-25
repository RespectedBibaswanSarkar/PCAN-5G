import axios from 'axios';

const host = typeof window !== 'undefined' ? window.location.hostname : 'localhost';
const API_BASE_URL = `http://${host}:8000`;
const WS_BASE_URL = `ws://${host}:8000`;

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 6000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// REST API Endpoints
export const getTopology = async () => {
    const response = await api.get('/topology');
    return response.data;
};

export const getStatus = async () => {
    const response = await api.get('/status');
    return response.data;
};

export const getParameters = async () => {
    const response = await api.get('/parameters');
    return response.data;
};

export const updateParameters = async (params) => {
    const response = await api.post('/parameters/update', params);
    return response.data;
};

export const runExperiment = async (config) => {
    const response = await api.post('/experiment/run', config);
    return response.data;
};

export const getCurrentMetrics = async () => {
    const response = await api.get('/metrics/current');
    return response.data;
};

export const getGraphs = async () => {
    const response = await api.get('/graphs/list');
    return response.data;
};

export const startTraining = async (episodes = 20) => {
    const response = await api.post('/train', { episodes });
    return response.data;
};

// Node Control
export const toggleNode = async (nodeId, active) => {
    const response = await api.post('/node/toggle', {
        node_id: nodeId,
        active: active
    });
    return response.data;
};

// ─────────────────────────────────────────────
// RF Mode API Endpoints (NEW)
// ─────────────────────────────────────────────

export const getRFMode = async () => {
    const response = await api.get('/rf/mode');
    return response.data;
};

export const setRFMode = async (mode) => {
    const response = await api.post('/rf/mode', { mode });
    return response.data;
};

export const getRFMetrics = async () => {
    const response = await api.get('/rf/metrics');
    return response.data;
};

export const getNodePipeline = async (nodeId) => {
    const response = await api.get(`/rf/pipeline/${nodeId}`);
    return response.data;
};

// WebSocket Manager
export class WebSocketManager {
    constructor() {
        this.ws = null;
        this.listeners = [];
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
    }

    connect() {
        return new Promise((resolve, reject) => {
            try {
                this.ws = new WebSocket(`${WS_BASE_URL}/ws`);

                this.ws.onopen = () => {
                    console.log('WebSocket connected');
                    this.reconnectAttempts = 0;
                    resolve();
                };

                this.ws.onmessage = (event) => {
                    try {
                        const message = JSON.parse(event.data);
                        this.notifyListeners(message);
                    } catch (e) {
                        console.error('Failed to parse WebSocket message:', e);
                    }
                };

                this.ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    reject(error);
                };

                this.ws.onclose = () => {
                    console.log('WebSocket disconnected');
                    this.attemptReconnect();
                };
            } catch (error) {
                reject(error);
            }
        });
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            setTimeout(() => {
                this.connect().catch(err => console.error('Reconnect failed:', err));
            }, this.reconnectDelay);
        }
    }

    subscribe(callback) {
        this.listeners.push(callback);
        return () => {
            this.listeners = this.listeners.filter(l => l !== callback);
        };
    }

    notifyListeners(message) {
        this.listeners.forEach(callback => {
            try {
                callback(message);
            } catch (e) {
                console.error('Error in listener:', e);
            }
        });
    }

    send(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        } else {
            console.warn('WebSocket not connected');
        }
    }

    toggleNode(nodeId, active) {
        this.send({
            type: 'node_toggle',
            node_id: nodeId,
            toggle: !active // Toggle the inverse (if inactive, make active)
        });
    }

    getSnapshot() {
        this.send({
            type: 'get_snapshot'
        });
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    isConnected() {
        return this.ws && this.ws.readyState === WebSocket.OPEN;
    }
}

export default api;
