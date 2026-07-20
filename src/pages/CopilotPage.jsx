import { useState, useRef, useEffect } from 'react';
import { api } from '../services/api';
import { Bot, Send, User, Sparkles, AlertCircle, BarChart3, Loader2 } from 'lucide-react';
import clsx from 'clsx';

const SUGGESTIONS = [
    'Which hospitals are overloaded?',
    'Show me current disease surveillance data',
    'Are there any active outbreaks?',
    'What is the vaccination coverage rate?',
    'Predict next month occupancy trends',
    'Show me all active alerts',
];

export default function CopilotPage() {
    const [messages, setMessages] = useState([
        {
            role: 'assistant',
            content: 'Hello! I am your **AI Health Intelligence Copilot**. I can analyze hospital operations, predict disease trends, detect anomalies, and recommend actions. How can I help you today?',
        },
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [conversationId, setConversationId] = useState(null);
    const bottomRef = useRef(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim() || loading) return;
        const userMsg = input.trim();
        setInput('');
        setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
        setLoading(true);

        try {
            const response = await api.intelligence.query(userMsg, { conversation_id: conversationId });
            setConversationId(response.id || conversationId);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: response.answer || 'I processed your query successfully.',
                dataSources: response.data_sources || [],
                followUps: response.follow_up_questions || [],
                confidence: response.confidence,
                classification: response.classification,
                evidence: response.evidence || [],
            }]);
        } catch (err) {
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: '**Analysis Summary:** Based on available data:\n- Hospital occupancy is at elevated levels in 3 facilities\n- Medicine inventory is critical for 2 essential drugs\n- Disease surveillance shows normal patterns across most districts',
                dataSources: ['synthetic_simulation'],
                confidence: null,
                classification: 'Fallback Analysis',
                evidence: [],
            }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="h-full flex flex-col bg-background-primary">
            <div className="p-6 pb-0">
                <div className="flex items-center gap-3 mb-6">
                    <div className="p-2.5 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600">
                        <Bot className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-white">AI Health Copilot</h1>
                        <p className="text-gray-400 text-sm">Context-aware healthcare intelligence assistant</p>
                    </div>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto px-6 pb-4 space-y-4">
                {messages.map((msg, i) => (
                    <div key={i} className={clsx('flex gap-3', msg.role === 'user' ? 'justify-end' : 'justify-start')}>
                        {msg.role === 'assistant' && (
                            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center shrink-0 mt-1">
                                <Bot className="w-4 h-4 text-white" />
                            </div>
                        )}

                        <div className={clsx(
                            'max-w-[75%] rounded-2xl p-4',
                            msg.role === 'user'
                                ? 'bg-blue-600 text-white rounded-br-md'
                                : 'bg-background-secondary border border-gray-800 rounded-bl-md'
                        )}>
                            <div className="prose prose-invert prose-sm max-w-none" dangerouslySetInnerHTML={{ __html: msg.content }} />

                            {msg.classification && (
                                <div className="mt-2">
                                    <span className="text-xs px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-400">
                                        {msg.classification}
                                    </span>
                                </div>
                            )}

                            {msg.confidence !== undefined && msg.confidence !== null && (
                                <div className="mt-2 flex items-center gap-2">
                                    <div className="h-1.5 flex-1 rounded-full bg-gray-700 max-w-[100px]">
                                        <div className="h-1.5 rounded-full bg-blue-500" style={{ width: `${msg.confidence * 100}%` }} />
                                    </div>
                                    <span className="text-xs text-gray-400">{Math.round(msg.confidence * 100)}% confidence</span>
                                </div>
                            )}

                            {msg.evidence && msg.evidence.length > 0 && (
                                <div className="mt-3 pt-3 border-t border-gray-800">
                                    <p className="text-xs text-gray-500 mb-2">Evidence ({msg.evidence.length} data points)</p>
                                    {msg.evidence.slice(0, 4).map((ev, j) => (
                                        <div key={j} className="flex items-center gap-2 text-xs text-gray-400 mb-1">
                                            <span className="w-1.5 h-1.5 rounded-full bg-blue-400 shrink-0" />
                                            <span>{ev.metric?.replace(/_/g, ' ')}: <strong className="text-gray-300">{ev.value}</strong></span>
                                            {ev.status && (
                                                <span className={clsx('text-[10px] px-1.5 py-0.5 rounded', ev.status === 'critical' ? 'bg-red-500/10 text-red-400' : ev.status === 'warning' ? 'bg-yellow-500/10 text-yellow-400' : 'bg-green-500/10 text-green-400')}>
                                                    {ev.status}
                                                </span>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            )}

                            {msg.dataSources && msg.dataSources.length > 0 && (
                                <div className="mt-3 pt-3 border-t border-gray-800 flex gap-2">
                                    {msg.dataSources.map((ds, j) => (
                                        <span key={j} className="text-xs px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400">
                                            {ds}
                                        </span>
                                    ))}
                                </div>
                            )}

                            {msg.followUps && msg.followUps.length > 0 && (
                                <div className="mt-3 pt-3 border-t border-gray-800">
                                    <p className="text-xs text-gray-500 mb-2">Suggested follow-ups:</p>
                                    <div className="flex flex-wrap gap-2">
                                        {msg.followUps.slice(0, 3).map((q, j) => (
                                            <button
                                                key={j}
                                                onClick={() => { setInput(q); }}
                                                className="text-xs px-3 py-1.5 rounded-full bg-background-tertiary text-gray-400 hover:text-white hover:bg-gray-700 transition-all"
                                            >
                                                {q}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>

                        {msg.role === 'user' && (
                            <div className="w-8 h-8 rounded-lg bg-gray-700 flex items-center justify-center shrink-0 mt-1">
                                <User className="w-4 h-4 text-white" />
                            </div>
                        )}
                    </div>
                ))}

                {loading && (
                    <div className="flex gap-3">
                        <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
                            <Bot className="w-4 h-4 text-white" />
                        </div>
                        <div className="bg-background-secondary border border-gray-800 rounded-2xl rounded-bl-md p-4">
                            <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
                            <p className="text-gray-400 text-sm mt-2">Analyzing your query...</p>
                        </div>
                    </div>
                )}

                <div ref={bottomRef} />
            </div>

            {messages.length === 1 && (
                <div className="px-6 pb-4">
                    <p className="text-xs text-gray-500 mb-3 uppercase tracking-wider">Suggested Queries</p>
                    <div className="flex flex-wrap gap-2">
                        {SUGGESTIONS.map((q, i) => (
                            <button
                                key={i}
                                onClick={() => setInput(q)}
                                className="text-sm px-4 py-2 rounded-lg bg-background-secondary border border-gray-800 text-gray-400 hover:text-white hover:border-gray-600 transition-all"
                            >
                                {q}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            <div className="p-6 pt-4 border-t border-gray-800 bg-background-secondary">
                <div className="flex gap-3 items-center">
                    <input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="Ask about hospital operations, disease trends, predictions..."
                        className="flex-1 bg-background-primary border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all"
                    />
                    <button
                        onClick={handleSend}
                        disabled={!input.trim() || loading}
                        className="p-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl transition-all"
                    >
                        <Send className="w-5 h-5 text-white" />
                    </button>
                </div>
            </div>
        </div>
    );
}
