import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface Finding {
  icon: string;
  title: string;
  value: string;
  description: string;
  trend: 'up' | 'down' | 'neutral';
}

const KeyFindings: React.FC = () => {
  const [findings, setFindings] = useState<Finding[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFindings();
  }, []);

  const fetchFindings = async () => {
    try {
      const [co2Response, tempResponse, gapResponse] = await Promise.all([
        axios.get('http://localhost:8000/api/co2/summary'),
        axios.get('http://localhost:8000/api/temperature/summary'),
        axios.get('http://localhost:8000/api/analysis/co2-gap/summary')
      ]);

      const findings: Finding[] = [
        {
          icon: '🏭',
          title: 'Current CO₂ Level',
          value: `${co2Response.data.statistics.latest_ppm.toFixed(1)} ppm`,
          description: `+${co2Response.data.trend.annual_average_increase.toFixed(1)} ppm/year`,
          trend: 'up'
        },
        {
          icon: '🌡️',
          title: 'Temperature Anomaly',
          value: `+${tempResponse.data.anomaly_statistics.latest_anomaly.toFixed(2)}°C`,
          description: `${tempResponse.data.warming_trend.rate_per_year.toFixed(3)}°C/year warming`,
          trend: 'up'
        },
        {
          icon: '❓',
          title: 'Unexplained Warming',
          value: `${gapResponse.data.percentage_statistics.mean_gap_percentage.toFixed(1)}%`,
          description: gapResponse.data.key_finding,
          trend: 'neutral'
        }
      ];

      setFindings(findings);
    } catch (error) {
      console.error('Failed to fetch key findings:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold mb-4">Key Findings</h2>
        <div className="animate-pulse space-y-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-20 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-bold mb-4">Key Findings</h2>
      <div className="space-y-4">
        {findings.map((finding, index) => (
          <div key={index} className="border-l-4 border-blue-500 pl-4 py-2">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <span className="text-2xl">{finding.icon}</span>
                  <h3 className="font-semibold text-gray-900">{finding.title}</h3>
                </div>
                <div className="mt-1">
                  <span className="text-2xl font-bold text-gray-900">{finding.value}</span>
                  {finding.trend === 'up' && (
                    <span className="ml-2 text-red-500">↑</span>
                  )}
                  {finding.trend === 'down' && (
                    <span className="ml-2 text-green-500">↓</span>
                  )}
                </div>
                <p className="text-sm text-gray-600 mt-1">{finding.description}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default KeyFindings;