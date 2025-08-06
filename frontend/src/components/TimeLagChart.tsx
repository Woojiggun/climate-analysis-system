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
  ChartData,
  ChartOptions,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import axios from 'axios';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
// import { AlertCircle, TrendingUp, Droplets } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from './ui/alert';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface TimeLagData {
  location: string;
  optimal_lag_months: number;
  correlation_coefficient: number;
  chart_data: Array<{
    date: string;
    groundwater_level: number;
    current_temperature: number;
    lagged_temperature: number | null;
    water_level_change: number;
  }>;
  summary: {
    finding: string;
    correlation_strength: string;
  };
}

interface TimeLagChartProps {
  location?: string;
  startDate?: string;
  endDate?: string;
}

const TimeLagChart: React.FC<TimeLagChartProps> = ({
  location = 'California Central Valley',
  startDate,
  endDate,
}) => {
  const [data, setData] = useState<TimeLagData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTimeLagData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location, startDate, endDate]);


  const fetchTimeLagData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params: any = { location };
      // 날짜 파라미터는 일단 제외 (API가 기본값 사용)

      const response = await axios.get(
        'http://localhost:8000/api/analysis/visualization/time-lag-chart-data',
        { params }
      );

      setData(response.data);
    } catch (err: any) {
      console.error('Error fetching time-lag data:', err);
      console.error('Error response:', err.response?.data);
      setError('Failed to load time-lag correlation data.');
    } finally {
      setLoading(false);
    }
  };

  const chartData: ChartData<'line'> = {
    labels: data?.chart_data.map((d) => 
      new Date(d.date).toLocaleDateString('en-US', { year: 'numeric', month: 'short' })
    ) || [],
    datasets: [
      {
        label: 'Groundwater Level (m below surface)',
        data: data?.chart_data.map((d) => d.groundwater_level) || [],
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderWidth: 2,
        yAxisID: 'y1',
        tension: 0.1,
      },
      {
        label: `Temperature Anomaly (${data?.optimal_lag_months || 0} months later)`,
        data: data?.chart_data.map((d) => d.lagged_temperature) || [],
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        borderWidth: 2,
        yAxisID: 'y2',
        tension: 0.1,
      },
    ],
  };

  const chartOptions: ChartOptions<'line'> = {
    responsive: true,
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
        text: `Time-Lag Correlation: ${location}`,
      },
      tooltip: {
        callbacks: {
          afterLabel: (context) => {
            if (context.datasetIndex === 0) {
              const change = data?.chart_data[context.dataIndex]?.water_level_change;
              return change ? `Change: ${change.toFixed(2)}m` : '';
            }
            return '';
          },
        },
      },
    },
    scales: {
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        title: {
          display: true,
          text: 'Groundwater Level (m)',
        },
        reverse: true, // Lower values (deeper) at top
      },
      y2: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        title: {
          display: true,
          text: 'Temperature Anomaly (°C)',
        },
        grid: {
          drawOnChartArea: false,
        },
      },
    },
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-96">
          <div className="text-gray-500">Loading time-lag correlation data...</div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <span>⚠️</span>
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!data) {
    return null;
  }

  const correlationColor = Math.abs(data.correlation_coefficient) > 0.7 
    ? 'text-green-600' 
    : Math.abs(data.correlation_coefficient) > 0.5 
    ? 'text-yellow-600' 
    : 'text-red-600';

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span>📈</span>
          Time-Lag Correlation Analysis
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Key Findings Alert */}
          <Alert>
            <span>💧</span>
            <AlertTitle>Key Finding</AlertTitle>
            <AlertDescription>
              {data.summary.finding}
            </AlertDescription>
          </Alert>

          {/* Statistics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600">Location</div>
              <div className="text-lg font-semibold">{data.location}</div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600">Optimal Time Lag</div>
              <div className="text-lg font-semibold">{data.optimal_lag_months} months</div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600">Correlation Coefficient</div>
              <div className={`text-lg font-semibold ${correlationColor}`}>
                {data.correlation_coefficient.toFixed(3)}
              </div>
              <div className="text-xs text-gray-500">
                ({data.summary.correlation_strength})
              </div>
            </div>
          </div>

          {/* Chart */}
          <div className="h-96">
            <Line data={chartData} options={chartOptions} />
          </div>

          {/* Explanation */}
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <h4 className="font-semibold text-blue-900 mb-2">How to interpret this chart:</h4>
            <ul className="space-y-1 text-sm text-blue-800">
              <li>• Blue line shows groundwater levels (deeper = higher values)</li>
              <li>• Red line shows temperature anomalies {data.optimal_lag_months} months later</li>
              <li>• A negative correlation suggests groundwater depletion leads to temperature increases</li>
              <li>• The time lag indicates how long it takes for groundwater changes to affect temperature</li>
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default TimeLagChart;