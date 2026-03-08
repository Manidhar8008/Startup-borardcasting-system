import React, { useState } from 'react';
import AgentPipelineView from '../../components/AgentPipelineView';

const ContentFactory = () => {
  const [topic, setTopic] = useState('');

  const generateContent = () => {
    // API Call to /automation/start
    alert("Triggered AI Pipeline for: " + topic);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Content Factory</h1>
        <p className="mt-1 text-sm text-gray-500">
          Command your agents to build cross-platform content.
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1 space-y-6">
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <h3 className="text-lg font-medium text-gray-900 mb-4">New Generation Task</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Topic or Concept</label>
                <textarea 
                  rows={4}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 ring-1 ring-inset ring-gray-300"
                  placeholder="e.g. How AI is changing SaaS pricing..."
                  value={topic}
                  onChange={e => setTopic(e.target.value)}
                />
              </div>
              
              <button 
                onClick={generateContent}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Engage Marketing Brain
              </button>
            </div>
          </div>
        </div>

        <div className="lg:col-span-2">
          <AgentPipelineView />
        </div>
      </div>
    </div>
  );
};

export default ContentFactory;
