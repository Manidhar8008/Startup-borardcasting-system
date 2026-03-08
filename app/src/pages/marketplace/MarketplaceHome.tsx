import React from 'react';

const MarketplaceHome = () => {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Creator Marketplace</h1>
        <p className="mt-1 text-sm text-gray-500">
          Hire vetted creators and agencies to scale your brand.
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Mock Creator Card */}
        <div className="rounded-xl border bg-white p-6 shadow-sm flex flex-col items-center">
          <div className="h-24 w-24 rounded-full bg-gradient-to-r from-blue-400 to-indigo-500 mb-4 flex items-center justify-center text-white text-2xl font-bold">
            AM
          </div>
          <h3 className="text-xl font-bold text-gray-900">Alex Mercer</h3>
          <p className="text-sm text-gray-500 text-center mt-2">
            Ghostwriter & Ex-VC. Helping B2B founders scale on LinkedIn.
          </p>
          <div className="mt-4 flex gap-2">
            <span className="px-3 py-1 bg-indigo-50 text-indigo-700 text-xs font-semibold rounded-full">LinkedIn</span>
            <span className="px-3 py-1 bg-blue-50 text-blue-700 text-xs font-semibold rounded-full">Copywriting</span>
          </div>
          <div className="mt-6 w-full pt-4 border-t flex justify-between items-center">
            <span className="text-sm font-semibold text-gray-900">$150/hr</span>
            <button className="bg-gray-900 text-white px-4 py-2 rounded-md text-sm font-semibold hover:bg-gray-800">
              Hire Creator
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MarketplaceHome;
