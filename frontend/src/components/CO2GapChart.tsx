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

interface CO2GapData {
  date: string;
  co2_ppm: number;
  theoretical_temp: number;
  actual_temp: number;
  unexplained_gap: number;
  gap_percentage: number;
}

const CO2GapChart: React.FC = () => {
  const [gapData, setGapData] = useState<CO2GapData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchGapData();
  }, []);

  const fetchGapData = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/api/analysis/co2-gap', {
        params: {
          // API는 날짜 파라미터 없이도 작동합니다
        }
      });
      setGapData(response.data);
    } catch (err) {
      setError('Failed to fetch CO2 gap data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="text-center py-8">Loading CO2 gap analysis...</div>;
  if (error) return <div className="text-red-600 text-center py-8">{error}</div>;
  if (!gapData.length) return <div className="text-center py-8">No data available</div>;

  const chartData = {
    labels: gapData.map(d => new Date(d.date).toLocaleDateString()),
    datasets: [
      {
        label: 'Actual Temperature',
        data: gapData.map(d => d.actual_temp),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.1)',
        borderWidth: 1,
        tension: 0.1,
        pointRadius: 0,
        pointHoverRadius: 3
      },
      {
        label: 'Theoretical Temperature (CO2 only)',
        data: gapData.map(d => d.theoretical_temp),
        borderColor: 'rgb(53, 162, 235)',
        backgroundColor: 'rgba(53, 162, 235, 0.1)',
        borderWidth: 1,
        tension: 0.1,
        pointRadius: 0,
        pointHoverRadius: 3
      },
      {
        label: 'Unexplained Gap',
        data: gapData.map(d => d.unexplained_gap),
        borderColor: 'rgb(255, 206, 86)',
        backgroundColor: 'rgba(255, 206, 86, 0.2)',
        borderWidth: 1,
        fill: true,
        tension: 0.1,
        pointRadius: 0,
        pointHoverRadius: 3
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'CO₂ Gap Analysis: Theoretical vs Actual Temperature',
        font: {
          size: 16
        }
      },
      tooltip: {
        callbacks: {
          afterLabel: (context: any) => {
            const index = context.dataIndex;
            const gap = gapData[index].unexplained_gap;
            const percentage = gapData[index].gap_percentage;
            return `Gap: ${gap.toFixed(2)}°C (${percentage.toFixed(1)}%)`;
          }
        }
      }
    },
    scales: {
      y: {
        title: {
          display: true,
          text: 'Temperature (°C)'
        },
        min: -2,
        max: 16
      },
      x: {
        title: {
          display: true,
          text: 'Date'
        }
      }
    }
  };

  const summary = {
    avgGap: gapData.reduce((sum, d) => sum + d.unexplained_gap, 0) / gapData.length,
    avgPercentage: gapData.reduce((sum, d) => sum + d.gap_percentage, 0) / gapData.length,
    maxGap: Math.max(...gapData.map(d => d.unexplained_gap)),
    latestGap: gapData[gapData.length - 1].unexplained_gap
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="h-96">
        <Line data={chartData} options={options} />
      </div>
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 p-4 rounded">
          <div className="text-sm text-gray-600">Average Gap</div>
          <div className="text-xl font-bold text-blue-600">
            {summary.avgGap.toFixed(2)}°C
          </div>
        </div>
        <div className="bg-yellow-50 p-4 rounded">
          <div className="text-sm text-gray-600">Average %</div>
          <div className="text-xl font-bold text-yellow-600">
            {summary.avgPercentage.toFixed(1)}%
          </div>
        </div>
        <div className="bg-red-50 p-4 rounded">
          <div className="text-sm text-gray-600">Max Gap</div>
          <div className="text-xl font-bold text-red-600">
            {summary.maxGap.toFixed(2)}°C
          </div>
        </div>
        <div className="bg-green-50 p-4 rounded">
          <div className="text-sm text-gray-600">Latest Gap</div>
          <div className="text-xl font-bold text-green-600">
            {summary.latestGap.toFixed(2)}°C
          </div>
        </div>
      </div>
    </div>
  );
};

export default CO2GapChart;