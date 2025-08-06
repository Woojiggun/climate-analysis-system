import React, { useEffect, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import axios from 'axios';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface GroundwaterData {
  date: string;
  groundwater_level: number;
  current_temperature: number;
  lagged_temperature: number | null;
  water_level_change: number;
}

interface TimeLagData {
  location: string;
  optimal_lag_months: number;
  correlation_coefficient: number;
  chart_data: GroundwaterData[];
  summary: {
    finding: string;
    correlation_strength: string;
  };
}

const GroundwaterChart: React.FC = () => {
  const [data, setData] = useState<TimeLagData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/api/analysis/visualization/time-lag-chart-data-fixed');
      setData(response.data);
    } catch (err) {
      setError('Failed to fetch groundwater data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="text-center py-8">Loading groundwater analysis...</div>;
  if (error) return <div className="text-red-600 text-center py-8">{error}</div>;
  if (!data) return <div className="text-center py-8">No data available</div>;

  const chartData = {
    labels: data.chart_data.map(d => new Date(d.date).toLocaleDateString()),
    datasets: [
      {
        label: 'Groundwater Level (m)',
        data: data.chart_data.map(d => d.groundwater_level),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderWidth: 1,
        tension: 0.1,
        pointRadius: 0,
        pointHoverRadius: 3,
        yAxisID: 'y',
      },
      {
        label: 'Current Temperature Anomaly (°C)',
        data: data.chart_data.map(d => d.current_temperature),
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        borderWidth: 1,
        tension: 0.1,
        pointRadius: 0,
        pointHoverRadius: 3,
        yAxisID: 'y1',
      },
      {
        label: `Temperature ${data.optimal_lag_months} Months Later (°C)`,
        data: data.chart_data.map(d => d.lagged_temperature),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        borderWidth: 1,
        borderDash: [5, 5],
        tension: 0.1,
        pointRadius: 0,
        pointHoverRadius: 3,
        yAxisID: 'y1',
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Groundwater-Temperature Time-Lag Analysis',
        font: {
          size: 16
        }
      },
      tooltip: {
        callbacks: {
          afterLabel: (context: any) => {
            const index = context.dataIndex;
            const change = data.chart_data[index].water_level_change;
            return `Water level change: ${change.toFixed(2)}m`;
          }
        }
      }
    },
    scales: {
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        title: {
          display: true,
          text: 'Groundwater Level (m)'
        },
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        title: {
          display: true,
          text: 'Temperature Anomaly (°C)'
        },
        grid: {
          drawOnChartArea: false,
        },
      },
    },
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="mb-4">
        <h2 className="text-xl font-bold mb-2">Groundwater Depletion & Temperature Correlation</h2>
        <p className="text-gray-600 text-sm">{data.location}</p>
      </div>
      
      <div className="h-96">
        <Line data={chartData} options={options} />
      </div>
      
      <div className="mt-6 grid grid-cols-2 md:grid-cols-3 gap-4">
        <div className="bg-blue-50 p-4 rounded">
          <div className="text-sm text-gray-600">Optimal Lag</div>
          <div className="text-xl font-bold text-blue-600">
            {data.optimal_lag_months} months
          </div>
        </div>
        <div className="bg-purple-50 p-4 rounded">
          <div className="text-sm text-gray-600">Correlation</div>
          <div className="text-xl font-bold text-purple-600">
            {data.correlation_coefficient.toFixed(3)}
          </div>
        </div>
        <div className="bg-green-50 p-4 rounded">
          <div className="text-sm text-gray-600">Strength</div>
          <div className="text-xl font-bold text-green-600">
            {data.summary.correlation_strength}
          </div>
        </div>
      </div>
      
      <div className="mt-4 p-4 bg-gray-50 rounded">
        <p className="text-sm text-gray-700">
          <span className="font-semibold">Key Finding:</span> {data.summary.finding}
        </p>
      </div>
    </div>
  );
};

export default GroundwaterChart;