import { useEffect, useState } from "react";

type Reading = {
  _id: string;
  bin_id: string;
  capacity_percent: number;
  timestamp: string;
};

type Report = {
  _id: string;
  bin_id: string;
  report_start_time: string;
  report_end_time: string;
  capacity_avg_percent: number;
  capacity_max_percent: number;
  capacity_min_percent: number;
  emptied_count: number;
  last_emptied_time: string | null;
  readings_count: number;
  max_full_duration_seconds: number; // ✅ NEW
};

type Alert = {
  _id: string;
  bin_id: string;
  status: string;
  capacity: number;
  alert_timestamp: string;
  message: string;
};

// ✅ Helper: format seconds → readable duration
function formatDuration(seconds: number) {
  if (!seconds || seconds === 0) return "—";

  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;

  if (mins > 0) return `${mins}m ${secs}s`;
  return `${secs}s`;
}

export default function App() {
  const [readings, setReadings] = useState<Reading[]>([]);
  const [reports, setReports] = useState<Report[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);

  useEffect(() => {
    const fetchData = () => {
      fetch("http://localhost:5000/api/readings")
        .then(res => res.json())
        .then(setReadings)
        .catch(console.error);

      fetch("http://localhost:5000/api/reports")
        .then(res => res.json())
        .then(setReports)
        .catch(console.error);

      fetch("http://localhost:5000/api/alerts")
        .then(res => res.json())
        .then(setAlerts)
        .catch(console.error);
    };

    fetchData(); 
    const interval = setInterval(fetchData, 3000); 

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6">
      <header className="mb-8">
        <h1 className="text-4xl font-bold tracking-tight">SmartBin Dashboard</h1>
        <p className="text-slate-400 mt-1">
          Real-time monitoring & analytics for smart waste bins
        </p>
      </header>

      {/* Alerts */}
      <section className="mb-10">
        <h2 className="text-xl font-semibold mb-4">🚨 Latest Alerts</h2>
        {alerts.length === 0 ? (
          <div className="text-slate-400 italic">No active alerts</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {alerts.map(alert => (
              <div
                key={alert._id}
                className="rounded-2xl bg-red-950/40 border border-red-800 p-5 shadow-lg"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-red-400 font-semibold">{alert.status}</span>
                  <span className="text-xs text-slate-400">
                    {new Date(alert.alert_timestamp).toLocaleString()}
                  </span>
                </div>
                <p className="font-medium mb-1">{alert.message}</p>
                <p className="text-sm text-slate-400">
                  Bin <span className="font-semibold">{alert.bin_id}</span> · Capacity {alert.capacity}%
                </p>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Stats */}
      <section className="mb-10 grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard label="Total Bins" value={new Set(readings.map(r => r.bin_id)).size} />
        <StatCard label="Total Readings" value={readings.length} />
        <StatCard label="Generated Reports" value={reports.length} />
      </section>

      {/* Readings */}
      <section className="mb-10">
        <h2 className="text-xl font-semibold mb-4">📊 Latest Bin Readings</h2>
        <div className="overflow-hidden rounded-2xl border border-slate-800">
          <table className="w-full text-sm">
            <thead className="bg-slate-900 text-slate-400">
              <tr>
                <th className="px-4 py-3 text-left">Bin ID</th>
                <th className="px-4 py-3 text-left">Capacity</th>
                <th className="px-4 py-3 text-left">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {readings.map(r => (
                <tr key={r._id} className="hover:bg-slate-900/60">
                  <td className="px-4 py-3 font-medium">{r.bin_id}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-full bg-slate-800 rounded-full h-2">
                        <div
                          className="h-2 rounded-full bg-emerald-500"
                          style={{ width: `${r.capacity_percent}%` }}
                        />
                      </div>
                      <span className="w-12 text-right">{r.capacity_percent}%</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-slate-400">
                    {new Date(r.timestamp).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Reports */}
      <section>
        <h2 className="text-xl font-semibold mb-4">📁 Reports Summary</h2>
        <div className="overflow-x-auto rounded-2xl border border-slate-800">
          <table className="w-full text-sm">
            <thead className="bg-slate-900 text-slate-400">
              <tr>
                <th className="px-4 py-3 text-left">Bin</th>
                <th className="px-4 py-3">Avg</th>
                <th className="px-4 py-3">Max</th>
                <th className="px-4 py-3">Min</th>
                <th className="px-4 py-3">Emptied</th>
                <th className="px-4 py-3">Full Duration</th>
                <th className="px-4 py-3">Last Emptied</th>
                <th className="px-4 py-3">Readings</th>
                <th className="px-4 py-3">Report End</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {reports.map(r => (
                <tr key={r._id} className="hover:bg-slate-900/60">
                  <td className="px-4 py-3 font-medium">{r.bin_id}</td>
                  <td className="px-4 py-3 text-center">{r.capacity_avg_percent}%</td>
                  <td className="px-4 py-3 text-center text-emerald-400">{r.capacity_max_percent}%</td>
                  <td className="px-4 py-3 text-center text-amber-400">{r.capacity_min_percent}%</td>
                  <td className="px-4 py-3 text-center">{r.emptied_count}</td>
                  <td className="px-4 py-3 text-center font-medium text-indigo-400">
                    {formatDuration(r.max_full_duration_seconds)}
                  </td>
                  <td className="px-4 py-3 text-center text-slate-400">
                    {r.last_emptied_time
                      ? new Date(r.last_emptied_time).toLocaleString()
                      : "—"}
                  </td>
                  <td className="px-4 py-3 text-center">{r.readings_count}</td>
                  <td className="px-4 py-3 text-center text-slate-400">
                    {new Date(r.report_end_time).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-2xl bg-slate-900 border border-slate-800 p-5 shadow">
      <p className="text-sm text-slate-400 mb-1">{label}</p>
      <p className="text-3xl font-bold">{value}</p>
    </div>
  );
}
