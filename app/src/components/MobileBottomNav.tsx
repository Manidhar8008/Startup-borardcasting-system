import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, PenTool, Zap, MessageSquare, User } from 'lucide-react';

const MobileBottomNav = () => {
  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 flex items-center justify-between bg-white border-t border-gray-200 px-6 py-3 pb-safe shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)] sm:hidden">
      <NavLink 
        to="/" 
        className={({ isActive }) => `flex flex-col items-center gap-1 ${isActive ? 'text-indigo-600' : 'text-gray-500 hover:text-gray-900'}`}
        end
      >
        <LayoutDashboard className="h-6 w-6" />
        <span className="text-[10px] font-medium">Dashboard</span>
      </NavLink>

      <NavLink 
        to="/content" 
        className={({ isActive }) => `flex flex-col items-center gap-1 ${isActive ? 'text-indigo-600' : 'text-gray-500 hover:text-gray-900'}`}
      >
        <PenTool className="h-6 w-6" />
        <span className="text-[10px] font-medium">Content</span>
      </NavLink>

      <NavLink 
        to="/automation" 
        className="relative flex flex-col items-center gap-1 -mt-5"
      >
        {({ isActive }) => (
          <>
            <div className={`h-14 w-14 rounded-full flex items-center justify-center shadow-lg ${isActive ? 'bg-indigo-700' : 'bg-indigo-600 hover:bg-indigo-700'} text-white border-4 border-white`}>
              <Zap className="h-6 w-6" />
            </div>
            <span className="text-[10px] font-medium text-gray-900 mt-1">Auto</span>
          </>
        )}
      </NavLink>

      <NavLink 
        to="/assistant" 
        className={({ isActive }) => `flex flex-col items-center gap-1 ${isActive ? 'text-indigo-600' : 'text-gray-500 hover:text-gray-900'}`}
      >
        <MessageSquare className="h-6 w-6" />
        <span className="text-[10px] font-medium">Assistant</span>
      </NavLink>

      <NavLink 
        to="/profile" 
        className={({ isActive }) => `flex flex-col items-center gap-1 ${isActive ? 'text-indigo-600' : 'text-gray-500 hover:text-gray-900'}`}
      >
        <User className="h-6 w-6" />
        <span className="text-[10px] font-medium">Profile</span>
      </NavLink>
    </div>
  );
};

export default MobileBottomNav;
