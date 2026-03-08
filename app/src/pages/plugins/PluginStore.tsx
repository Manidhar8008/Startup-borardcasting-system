import React from 'react';
import { Download, CheckCircle } from 'lucide-react';

const PluginStore = () => {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Plugin Ecosystem</h1>
        <p className="mt-1 text-sm text-gray-500">
          Extend JAN AI's capabilities with community-built integrations.
        </p>
      </header>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="flex bg-white rounded-xl shadow-sm border p-6">
          <div className="h-16 w-16 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600 font-bold text-xl shrink-0">
            LI
          </div>
          <div className="ml-6 flex-1">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-lg font-bold text-gray-900">LinkedIn Growth Hack</h3>
                <p className="text-sm text-gray-500 mt-1">Automatically DM engaged users after 24 hrs.</p>
              </div>
              <button className="flex items-center gap-2 bg-indigo-50 text-indigo-700 px-3 py-1.5 rounded-md text-sm font-semibold hover:bg-indigo-100">
                <CheckCircle className="h-4 w-4" /> Installed
              </button>
            </div>
            <div className="mt-4 text-xs text-gray-500 flex items-center gap-4">
              <span>By JAN AI Core</span>
              <span>12.4k Installs</span>
            </div>
          </div>
        </div>

        <div className="flex bg-white rounded-xl shadow-sm border p-6">
          <div className="h-16 w-16 bg-red-100 rounded-lg flex items-center justify-center text-red-600 font-bold text-xl shrink-0">
            YT
          </div>
          <div className="ml-6 flex-1">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-lg font-bold text-gray-900">Auto Shorts Clipper</h3>
                <p className="text-sm text-gray-500 mt-1">Converts 10m videos into 3 viral Shorts.</p>
              </div>
              <button className="flex items-center gap-2 bg-gray-900 text-white px-3 py-1.5 rounded-md text-sm font-semibold hover:bg-gray-800">
                <Download className="h-4 w-4" /> Install
              </button>
            </div>
             <div className="mt-4 text-xs text-gray-500 flex items-center gap-4">
              <span>By CreatorLabs</span>
              <span>8.1k Installs</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PluginStore;
