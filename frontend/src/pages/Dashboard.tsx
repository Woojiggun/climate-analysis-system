import React from 'react';
import CO2GapChartThin from '../components/CO2GapChartThin';
import KeyFindings from '../components/KeyFindings';
import GroundwaterChart from '../components/GroundwaterChart';

const Dashboard: React.FC = () => {
  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Climate Analysis Dashboard
        </h1>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto">
          Analyzing the relationship between CO₂ levels, temperature changes, and groundwater depletion
          to understand the full picture of climate change.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <CO2GapChartThin />
        </div>
        <div className="lg:col-span-1">
          <KeyFindings />
        </div>
      </div>

      <div className="mt-8">
        <GroundwaterChart />
      </div>
    </div>
  );
};

export default Dashboard;