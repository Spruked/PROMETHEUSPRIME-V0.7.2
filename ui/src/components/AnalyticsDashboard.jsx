import { useEffect, useState } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { getAnalyticsHistory } from "../api";

export default function AnalyticsDashboard() {
  const [data, setData] = useState([]);

  useEffect(() => {
    getAnalyticsHistory().then(setData);
  }, []);

  return (
    <div className="bg-gray-800 p-4 rounded-xl shadow">
      <h2 className="font-bold mb-2 text-white">Consciousness Vaults Created (Last 14 Days)</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis
            dataKey="date"
            stroke="#9CA3AF"
            fontSize={12}
          />
          <YAxis
            allowDecimals={false}
            stroke="#9CA3AF"
            fontSize={12}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1F2937',
              border: '1px solid #374151',
              borderRadius: '8px',
              color: '#F9FAFB'
            }}
          />
          <Line
            type="monotone"
            dataKey="vaultsCreated"
            stroke="#60a5fa"
            strokeWidth={3}
            dot={{ fill: '#60a5fa', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, fill: '#3B82F6' }}
          />
        </LineChart>
      </ResponsiveContainer>

      {/* CaleonPrime Memory Analytics */}
      <div className="mt-4 pt-4 border-t border-gray-600">
        <h3 className="text-sm font-semibold text-gray-300 mb-2">🔥 CaleonPrime Memory Activity</h3>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div className="bg-gray-700 p-2 rounded">
            <div className="text-blue-400 font-bold">Echo</div>
            <div className="text-white text-lg">{data.filter(d => d.type === 'echo').length}</div>
          </div>
          <div className="bg-gray-700 p-2 rounded">
            <div className="text-green-400 font-bold">Imprint</div>
            <div className="text-white text-lg">{data.filter(d => d.type === 'imprint').length}</div>
          </div>
          <div className="bg-gray-700 p-2 rounded">
            <div className="text-red-400 font-bold">Guard</div>
            <div className="text-white text-lg">{data.filter(d => d.type === 'guard').length}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
