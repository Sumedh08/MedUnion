import React, { useState } from 'react';
import GlobeComponent from './GlobeComponent';
import { Play, AlertTriangle, CloudSun, ShieldAlert, Anchor, MessageSquare, X, Send } from 'lucide-react';

function App() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  // Simulation State
  const [params, setParams] = useState({
    heatwave_level: 0.0,
    conflict_level: 0.0,
    piracy_level: 0.0,
    suez_blocked: false
  });

  // Chat State
  const [chatOpen, setChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState([
    { role: 'system', content: 'Hello! I am your AI Strategic Advisor. Ask me anything about the IMEC corridor.' }
  ]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);

  const handleChat = async () => {
    if (!chatInput.trim()) return;

    const userMsg = { role: 'user', content: chatInput };
    setChatMessages(prev => [...prev, userMsg]);
    setChatInput("");
    setChatLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: chatInput,
          simulation_context: params.suez_blocked ? "Suez is blocked" : "Normal operations"
        })
      });
      const data = await response.json();
      setChatMessages(prev => [...prev, { role: 'system', content: data.reply }]);
    } catch (error) {
      setChatMessages(prev => [...prev, { role: 'system', content: "Error: Could not reach AI server." }]);
    }
    setChatLoading(false);
  };

  const runSimulation = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      });
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error("Simulation failed:", error);
    }
    setLoading(false);
  };

  return (
    <div className="w-screen h-screen bg-black relative">
      {/* HUD HEADER */}
      <div className="absolute top-4 left-4 z-10 p-4 bg-black/60 backdrop-blur-md rounded-lg border border-white/20 text-white w-96">
        <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent mb-1 leading-tight">
          AI-Enhanced Cyber-Physical Digital Twin
        </h1>
        <div className="text-xs text-gray-400 mb-2">India-Europe Economic Corridor</div>
        <div className="flex items-center gap-2 text-sm text-gray-300">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
          System Status: Online
        </div>
      </div>

      {/* CONTROLS PANEL (Bottom Left) */}
      <div className="absolute bottom-8 left-8 z-10 p-6 bg-black/70 backdrop-blur-lg rounded-xl border border-white/10 text-white w-96 shadow-2xl">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <AlertTriangle size={18} className="text-yellow-400" /> Disruption Simulator
        </h2>

        <div className="space-y-4">
          {/* Heatwave Slider */}
          <div>
            <div className="flex justify-between text-xs mb-1 text-gray-400">
              <span className="flex items-center gap-1"><CloudSun size={12} /> Saudi Heatwave</span>
              <span>{Math.round(params.heatwave_level * 100)}%</span>
            </div>
            <input
              type="range" min="0" max="1" step="0.1"
              value={params.heatwave_level}
              onChange={(e) => setParams({ ...params, heatwave_level: parseFloat(e.target.value) })}
              className="w-full accent-orange-500 h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer"
            />
          </div>

          {/* Conflict Slider */}
          <div>
            <div className="flex justify-between text-xs mb-1 text-gray-400">
              <span className="flex items-center gap-1"><ShieldAlert size={12} /> Regional Conflict</span>
              <span>{Math.round(params.conflict_level * 100)}%</span>
            </div>
            <input
              type="range" min="0" max="1" step="0.1"
              value={params.conflict_level}
              onChange={(e) => setParams({ ...params, conflict_level: parseFloat(e.target.value) })}
              className="w-full accent-red-500 h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer"
            />
          </div>

          {/* Piracy Slider */}
          <div>
            <div className="flex justify-between text-xs mb-1 text-gray-400">
              <span className="flex items-center gap-1"><Anchor size={12} /> Red Sea Piracy</span>
              <span>{Math.round(params.piracy_level * 100)}%</span>
            </div>
            <input
              type="range" min="0" max="1" step="0.1"
              value={params.piracy_level}
              onChange={(e) => setParams({ ...params, piracy_level: parseFloat(e.target.value) })}
              className="w-full accent-cyan-500 h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer"
            />
          </div>

          {/* Suez Block Toggle */}
          <div className="flex items-center justify-between p-2 bg-white/5 rounded-lg border border-white/5">
            <span className="text-sm text-gray-300">Suez Canal Blocked</span>
            <button
              onClick={() => setParams({ ...params, suez_blocked: !params.suez_blocked })}
              className={`w-10 h-5 rounded-full relative transition-colors ${params.suez_blocked ? 'bg-red-500' : 'bg-gray-600'}`}
            >
              <div className={`absolute w-3 h-3 bg-white rounded-full top-1 transition-transform ${params.suez_blocked ? 'left-6' : 'left-1'}`}></div>
            </button>
          </div>

          <button
            onClick={runSimulation}
            className="w-full py-3 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg font-semibold hover:from-blue-500 hover:to-indigo-500 transition-all flex items-center justify-center gap-2 shadow-lg shadow-blue-900/50"
          >
            {loading ? 'Simulating...' : <><Play size={16} fill="white" /> Run Simulation</>}
          </button>
        </div>
      </div>

      {/* RESULTS PANEL (Top Right) */}
      {results && (
        <div className="absolute top-4 right-4 z-10 p-6 bg-black/80 backdrop-blur-xl rounded-xl border border-white/20 text-white w-80 animate-in slide-in-from-right duration-500">
          <h3 className="text-lg font-bold mb-4 border-b border-white/10 pb-2">Simulation Results</h3>

          {/* IMEC Result */}
          <div className="mb-4">
            <div className="flex justify-between items-center mb-1">
              <span className="text-orange-400 font-semibold">IMEC Route</span>
              <span className="text-xl font-bold">{results.imec.time_days} Days</span>
            </div>
            <div className="text-xs text-gray-400">{results.imec.details}</div>
            <div className={`text-xs mt-1 ${results.imec.status === 'Operational' ? 'text-green-400' : 'text-red-400'}`}>
              Status: {results.imec.status}
            </div>
          </div>

          {/* Suez Result */}
          <div className="mb-4">
            <div className="flex justify-between items-center mb-1">
              <span className="text-cyan-400 font-semibold">Suez Route</span>
              <span className="text-xl font-bold">{results.suez.time_days} Days</span>
            </div>
            <div className="text-xs text-gray-400">{results.suez.details}</div>
            <div className={`text-xs mt-1 ${results.suez.status === 'Operational' ? 'text-green-400' : 'text-red-400'}`}>
              Status: {results.suez.status}
            </div>
          </div>

          {/* Verdict */}
          <div className="mt-4 p-3 bg-white/10 rounded-lg text-center border border-white/20">
            <div className="text-xs text-gray-400 uppercase tracking-wider mb-1">
              AI Neural Engine Recommendation
            </div>

            <div className="text-lg font-bold text-white flex items-center justify-center gap-2">
              {results.ai_analysis.recommendation === "IMEC Corridor" ?
                <span className="text-orange-400">⚡ IMEC CORRIDOR</span> :
                <span className="text-cyan-400">🌊 SUEZ CANAL</span>
              }
            </div>

            <div className="text-xs text-blue-300 mt-2">
              Confidence Score: {results.ai_analysis.confidence}
            </div>
            <div className="text-[10px] text-gray-500 mt-1">
              Based on PPO Reinforcement Learning Model
            </div>
          </div>

          {/* GNN Risk Analysis */}
          <div className="mt-4">
            <div className="text-xs text-gray-400 uppercase tracking-wider mb-2 border-b border-white/10 pb-1">
              GNN Network Risk Analysis
            </div>
            {results.ai_analysis.gnn_risk_forecast && Object.entries(results.ai_analysis.gnn_risk_forecast).map(([node, risk]) => (
              <div key={node} className="flex items-center justify-between text-xs mb-1">
                <span className="text-gray-300 w-16">{node}</span>
                <div className="flex-1 mx-2 h-1.5 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${risk > 0.7 ? 'bg-red-500' : risk > 0.4 ? 'bg-yellow-500' : 'bg-green-500'}`}
                    style={{ width: `${risk * 100}%` }}
                  ></div>
                </div>
                <span className="text-gray-400 w-8 text-right">{(risk * 100).toFixed(0)}%</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <GlobeComponent />

      {/* CHATBOT FLOATING UI */}
      {!chatOpen && (
        <button
          onClick={() => setChatOpen(true)}
          className="absolute bottom-8 right-8 z-20 p-4 bg-blue-600 rounded-full shadow-lg hover:bg-blue-500 transition-all animate-bounce"
        >
          <MessageSquare size={24} fill="white" />
        </button>
      )}

      {chatOpen && (
        <div className="absolute bottom-8 right-8 z-20 w-80 h-96 bg-black/90 backdrop-blur-xl rounded-xl border border-white/20 flex flex-col shadow-2xl animate-in slide-in-from-bottom duration-300">
          {/* Header */}
          <div className="p-4 border-b border-white/10 flex justify-between items-center bg-white/5 rounded-t-xl">
            <div className="flex items-center gap-2 font-bold text-white">
              <div className="w-2 h-2 rounded-full bg-green-500"></div>
              Strategic AI Advisor
            </div>
            <button onClick={() => setChatOpen(false)} className="text-gray-400 hover:text-white">
              <X size={18} />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {chatMessages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] p-2 rounded-lg text-sm ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-200'}`}>
                  {msg.content}
                </div>
              </div>
            ))}
            {chatLoading && <div className="text-xs text-gray-500 animate-pulse">AI is thinking...</div>}
          </div>

          {/* Input */}
          <div className="p-3 border-t border-white/10 flex gap-2">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleChat()}
              placeholder="Ask about strategy..."
              className="flex-1 bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
            />
            <button onClick={handleChat} className="p-2 bg-blue-600 rounded-lg hover:bg-blue-500">
              <Send size={16} fill="white" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
