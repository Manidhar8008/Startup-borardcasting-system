import React, { useState, useEffect } from 'react';
import { Bot, CheckCircle, CircleDashed, Loader2 } from 'lucide-react';
import { cn } from '../lib/utils';

type AgentStatus = 'idle' | 'running' | 'completed' | 'error';

interface AgentNode {
  id: string;
  name: string;
  status: AgentStatus;
  detail?: string;
}

const mockPipeline: AgentNode[] = [
  { id: '1', name: 'TrendAgent', status: 'completed', detail: 'Found 3 high-impact trends' },
  { id: '2', name: 'MarketingBrain', status: 'completed', detail: 'Strategy set: B2B Growth' },
  { id: '3', name: 'ContentAgent', status: 'running', detail: 'Drafting LinkedIn carousel...' },
  { id: '4', name: 'ReviewAgent', status: 'idle' },
  { id: '5', name: 'PublisherAgent', status: 'idle' },
];

const AgentPipelineView = () => {
  const [nodes, setNodes] = useState<AgentNode[]>(mockPipeline);

  // In a real app, this would connect to a WebSocket or poll /pipeline/status

  return (
    <div className="rounded-xl border bg-card p-6 shadow-sm">
      <div className="mb-4 flex items-center gap-2">
        <Bot className="h-5 w-5 text-indigo-500" />
        <h3 className="text-lg font-semibold tracking-tight">Realtime Agent Pipeline</h3>
      </div>
      
      <div className="space-y-4 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-300 before:to-transparent">
        {nodes.map((node, i) => (
          <div key={node.id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
            {/* Icon Center */}
            <div className={cn(
              "flex items-center justify-center w-10 h-10 rounded-full border-4 border-white shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2",
              node.status === 'completed' ? 'bg-green-500' :
              node.status === 'running' ? 'bg-indigo-500' : 'bg-gray-300'
            )}>
              {node.status === 'completed' ? <CheckCircle className="h-5 w-5 text-white" /> :
               node.status === 'running' ? <Loader2 className="h-5 w-5 text-white animate-spin" /> :
               <CircleDashed className="h-5 w-5 text-white" />}
            </div>
            
            {/* Card */}
            <div className={cn(
              "w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-lg border bg-white shadow-sm",
              node.status === 'running' && "ring-2 ring-indigo-500"
            )}>
              <div className="flex items-center justify-between space-x-2 mb-1">
                <div className="font-bold text-slate-900">{node.name}</div>
                <div className={cn(
                  "text-xs font-medium px-2 py-1 rounded-full",
                  node.status === 'completed' && "bg-green-100 text-green-700",
                  node.status === 'running' && "bg-indigo-100 text-indigo-700",
                  node.status === 'idle' && "bg-gray-100 text-gray-700",
                )}>
                  {node.status.toUpperCase()}
                </div>
              </div>
              <div className="text-sm text-slate-500">{node.detail || "Waiting in queue..."}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AgentPipelineView;
