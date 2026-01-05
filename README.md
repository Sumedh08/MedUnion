# Digital Twin for Supply Chain Resilience

**AI-Driven Risk Simulation for the India-Middle East-Europe Corridor**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg)](https://reactjs.org/)

## 🌍 Overview

A cyber-physical digital twin framework for simulating and analyzing disruption scenarios in multi-modal trade corridors. This system integrates **Graph Neural Networks (GNN)**, **Reinforcement Learning (PPO)**, and **Retrieval-Augmented Generation (RAG)** to provide decision-support for shipping companies and marine insurers.

### Key Features

- **3D Interactive Globe**: Real-time visualization of IMEC vs. Suez Canal routes
- **AI-Powered Route Optimization**: PPO-based reinforcement learning agent
- **Network Risk Prediction**: GCN-based disruption propagation analysis
- **Strategic AI Advisor**: RAG-powered chatbot for scenario analysis
- **Disruption Simulation**: Heatwaves, geopolitical conflicts, piracy, canal blockages

## 🏗️ Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   React UI      │◄────►│  FastAPI Backend │◄────►│  AI Models      │
│  (Vite + 3D)    │      │  (Simulation)    │      │  (GNN/RL/RAG)   │
└─────────────────┘      └──────────────────┘      └─────────────────┘
```

### Tech Stack

**Frontend:**
- React 18.3 + Vite
- react-globe.gl (3D Visualization)
- Tailwind CSS v4
- Lucide React Icons

**Backend:**
- Python 3.13
- FastAPI + Uvicorn
- PyTorch (GNN)
- Stable Baselines3 (RL)
- LangChain + HuggingFace (RAG)

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.13+
- npm or yarn

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Sumedh08/Digital-Twin-for-Supply-Chain-Resilience.git
cd Digital-Twin-for-Supply-Chain-Resilience
```

2. **Install Frontend Dependencies**
```bash
npm install
```

3. **Install Backend Dependencies**
```bash
pip install -r requirements.txt
```

### Running the Application

**Terminal 1 - Frontend:**
```bash
npm run dev
```

**Terminal 2 - Backend:**
```bash
python -m uvicorn backend.main:app --reload --port 8000
```

**Access the application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

## 🧠 AI Components

### 1. Reinforcement Learning Agent (PPO)
- **File**: `backend/ai_agent.py`
- **Purpose**: Learns optimal route selection based on disruption parameters
- **Training**: 10,000 timesteps on synthetic scenarios
- **Output**: Route recommendation (IMEC vs. Suez)

### 2. Graph Neural Network (GCN)
- **File**: `backend/gnn_model.py`
- **Purpose**: Predicts risk propagation across network nodes
- **Architecture**: 2-layer GCN with ReLU activation
- **Output**: Risk scores for 6 corridor nodes

### 3. RAG Chatbot
- **File**: `backend/rag_system.py`
- **Purpose**: Strategic advisor for scenario analysis
- **Modes**: 
  - Rule-based (No API key required)
  - HuggingFace API (Mistral-7B)
  - Groq API (Llama 3)

## 📊 Usage Example

### Simulation API

```bash
curl -X POST http://localhost:8000/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "heatwave_level": 0.7,
    "conflict_level": 0.5,
    "piracy_level": 0.3,
    "suez_blocked": false
  }'
```

### Chat API

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the risks of the IMEC route?",
    "simulation_context": "Normal operations"
  }'
```

## 🔧 Configuration

### Optional: Enable Real LLM (HuggingFace)

1. Sign up at [HuggingFace](https://huggingface.co/)
2. Get your API token
3. Set environment variable:
```bash
export HUGGINGFACEHUB_API_TOKEN="your_token_here"
```

## 📁 Project Structure

```
capstonedigi/
├── backend/
│   ├── main.py           # FastAPI server
│   ├── ai_agent.py       # RL Agent (PPO)
│   ├── gnn_model.py      # Graph Neural Network
│   ├── rag_system.py     # RAG Chatbot
│   └── env.py            # Custom Gym Environment
├── src/
│   ├── App.jsx           # Main React Component
│   ├── GlobeComponent.jsx # 3D Globe Visualization
│   └── index.css         # Tailwind Styles
├── public/
├── package.json
├── requirements.txt
└── README.md
```

## 🎯 Use Cases

- **Shipping Companies**: Route planning under uncertainty
- **Marine Insurers**: Premium risk assessment
- **Policy Makers**: Infrastructure resilience analysis
- **Researchers**: Supply chain disruption modeling

## 📝 Citation

If you use this project in your research, please cite:

```bibtex
@software{digital_twin_imec_2026,
  author = {Sumedh},
  title = {Digital Twin for Supply Chain Resilience: AI-Driven Risk Simulation for the India-Middle East-Europe Corridor},
  year = {2026},
  url = {https://github.com/Sumedh08/Digital-Twin-for-Supply-Chain-Resilience}
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- IMEC Corridor Initiative
- Stable Baselines3 Team
- PyTorch Geometric Community
- LangChain & HuggingFace

## 📧 Contact

**Sumedh** - [@Sumedh08](https://github.com/Sumedh08)

Project Link: [https://github.com/Sumedh08/Digital-Twin-for-Supply-Chain-Resilience](https://github.com/Sumedh08/Digital-Twin-for-Supply-Chain-Resilience)

---

**⭐ Star this repo if you find it useful!**
