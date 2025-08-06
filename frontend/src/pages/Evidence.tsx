import React, { useState } from 'react';
import CO2GapChart from '../components/CO2GapChart';
import ComparisonChart from '../components/ComparisonChart';
import TimeLagAnalysis from '../components/TimeLagAnalysis';

const Evidence: React.FC = () => {
  const [activeTab, setActiveTab] = useState('co2-gap');

  const tabs = [
    { id: 'co2-gap', name: 'CO₂ Gap Analysis' },
    { id: 'time-lag', name: 'Time-Lag Correlation' },
    { id: 'regional', name: 'Regional Comparison' }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Scientific Evidence</h1>
        <p className="text-gray-600">
          Explore the data and analysis supporting our hypothesis about groundwater depletion's role in climate change.
        </p>
      </div>

      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                py-2 px-1 border-b-2 font-medium text-sm
                ${activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
            >
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      <div className="mt-6">
        {activeTab === 'co2-gap' && (
          <div className="space-y-6">
            <CO2GapChart />
            <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
              <div className="flex">
                <div className="ml-3">
                  <p className="text-sm text-blue-700">
                    <strong>Key Insight:</strong> The growing gap between theoretical CO₂-based temperature 
                    predictions and actual observed temperatures suggests additional factors are at play in 
                    global warming beyond greenhouse gases alone.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'time-lag' && (
          <TimeLagAnalysis />
        )}

        {activeTab === 'regional' && (
          <ComparisonChart />
        )}
      </div>
    </div>
  );
};

export default Evidence;