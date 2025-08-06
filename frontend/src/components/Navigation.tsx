import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navigation: React.FC = () => {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="bg-blue-900 text-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <h1 className="text-xl font-bold">🌍 Climate Analysis System</h1>
          </div>
          <div className="flex space-x-4">
            <Link
              to="/"
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                isActive('/') ? 'bg-blue-700' : 'hover:bg-blue-700'
              }`}
            >
              Dashboard
            </Link>
            <Link
              to="/evidence"
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                isActive('/evidence') ? 'bg-blue-700' : 'hover:bg-blue-700'
              }`}
            >
              Evidence
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;