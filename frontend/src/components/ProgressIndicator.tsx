import React from 'react';

interface Phase {
  name: string;
  progress: number;
  status: 'completed' | 'in-progress' | 'pending';
}

const ProgressIndicator: React.FC = () => {
  const phases: Phase[] = [
    { name: 'Data Collection', progress: 100, status: 'completed' },
    { name: 'Core Analysis', progress: 100, status: 'completed' },
    { name: 'Visualization', progress: 60, status: 'in-progress' },
    { name: 'Advanced Features', progress: 0, status: 'pending' }
  ];

  const totalProgress = phases.reduce((sum, phase) => sum + phase.progress, 0) / phases.length;

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">Project Progress</h2>
        <span className="text-2xl font-bold text-blue-600">{totalProgress.toFixed(0)}%</span>
      </div>
      
      <div className="space-y-3">
        {phases.map((phase, index) => (
          <div key={index}>
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="font-medium">{phase.name}</span>
              <span className="text-gray-600">{phase.progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all duration-500 ${
                  phase.status === 'completed' ? 'bg-green-500' :
                  phase.status === 'in-progress' ? 'bg-blue-500' : 'bg-gray-300'
                }`}
                style={{ width: `${phase.progress}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 text-sm text-gray-600">
        Currently working on: <span className="font-semibold">CO₂ Gap Chart Visualization</span>
      </div>
    </div>
  );
};

export default ProgressIndicator;