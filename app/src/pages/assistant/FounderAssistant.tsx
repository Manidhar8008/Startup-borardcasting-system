import React, { useState } from 'react';
import { Send, Bot } from 'lucide-react';

const FounderAssistant = () => {
  const [messages, setMessages] = useState([
    { role: 'assistant', text: "Welcome back, Founder. I've analyzed your growth trajectory. You are 14% below target for LinkedIn engagement this week. Should we re-allocate focus, or spin up a new high-leverage thread?" }
  ]);
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input) return;
    setMessages(prev => [...prev, { role: 'user', text: input }, { role: 'assistant', text: "Analyzing your request based on current market trends..." }]);
    setInput('');
  };

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col bg-gray-50 p-8">
      <header className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Founder Assistant</h1>
        <p className="mt-1 text-sm text-gray-500">
          Your 24/7 AI confidant for growth and strategy.
        </p>
      </header>

      <div className="flex-1 bg-white rounded-xl border shadow-sm flex flex-col overflow-hidden max-w-4xl">
        <div className="flex-1 p-6 overflow-y-auto space-y-6">
          {messages.map((m, i) => (
            <div key={i} className={`flex gap-4 ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`h-10 w-10 shrink-0 rounded-full flex items-center justify-center ${m.role === 'assistant' ? 'bg-indigo-100 text-indigo-600' : 'bg-gray-200 text-gray-600'}`}>
                {m.role === 'assistant' ? <Bot className="h-6 w-6" /> : "US"}
              </div>
              <div className={`px-4 py-3 rounded-2xl max-w-[75%] ${m.role === 'assistant' ? 'bg-indigo-50 text-indigo-900 rounded-tl-none' : 'bg-gray-900 text-white rounded-tr-none'}`}>
                {m.text}
              </div>
            </div>
          ))}
        </div>
        
        <div className="p-4 border-t bg-gray-50/50">
          <div className="relative flex items-center">
            <input 
              type="text" 
              className="w-full bg-white border rounded-full px-6 py-3 pr-12 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Ask for strategy, content review, or analytics..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSend()}
            />
            <button 
              onClick={handleSend}
              className="absolute right-2 h-10 w-10 bg-indigo-600 rounded-full flex items-center justify-center text-white hover:bg-indigo-700 hover:shadow shadow-indigo-500/30 transition-all"
            >
              <Send className="h-4 w-4 ml-1" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FounderAssistant;
