import React from 'react';

const DashboardOverview = () => {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard Overview</h1>
        <p className="mt-1 text-sm text-gray-500">
          Welcome back to the JAN AI Marketing OS. Here's a snapshot of your network.
        </p>
      </header>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {/* KPI Cards */}
        <div className="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
          <dt className="truncate text-sm font-medium text-gray-500">Active Brands</dt>
          <dd className="mt-1 text-3xl font-semibold tracking-tight text-gray-900">3</dd>
        </div>
        <div className="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
          <dt className="truncate text-sm font-medium text-gray-500">Posts Generated (This Week)</dt>
          <dd className="mt-1 text-3xl font-semibold tracking-tight text-gray-900">24</dd>
        </div>
        <div className="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
          <dt className="truncate text-sm font-medium text-gray-500">Autonomous Actions</dt>
          <dd className="mt-1 text-3xl font-semibold tracking-tight text-gray-900">142</dd>
        </div>
        <div className="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
          <dt className="truncate text-sm font-medium text-gray-500">Growth Score</dt>
          <dd className="mt-1 text-3xl font-semibold tracking-tight text-green-600">92%</dd>
        </div>
      </div>

      <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Upcoming Pipeline */}
        <div className="rounded-lg bg-white shadow">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-base font-semibold leading-6 text-gray-900">Approval Queue</h3>
            <div className="mt-2 max-w-xl text-sm text-gray-500">
              <p>You have 3 items waiting for your review.</p>
            </div>
            <div className="mt-5">
              <button className="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500">
                View Queue
              </button>
            </div>
          </div>
        </div>

        {/* Marketing Brain Insights */}
        <div className="rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 shadow">
          <div className="px-4 py-5 sm:p-6 relative overflow-hidden">
            <h3 className="text-base font-semibold leading-6 text-white">Marketing Brain Insights</h3>
            <div className="mt-2 max-w-xl text-sm text-indigo-100">
              <p>Viral Prediction Engine suggests posting the "LLM Trends" thread on Tuesday at 9am. +28% predicted engagement lift.</p>
            </div>
            <div className="mt-5">
              <button className="inline-flex items-center rounded-md bg-white/10 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-white/20 ring-1 ring-inset ring-white/20">
                Apply Recommendation
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardOverview;
