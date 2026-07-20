import { useState, useEffect } from 'react';
import api from '../../api';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

export default function AdminDashboard() {
  const [orders, setOrders] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [exporting, setExporting] = useState(false);

  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([fetchData(), fetchChartData()]).catch(() => {
      setError('Cannot connect to the backend server.');
    });
  }, []);

  const fetchData = async () => {
    try {
      const res = await api.get('/admin/orders');
      setOrders(res.data);
    } catch (err) {
      console.error(err);
      throw err;
    }
  };

  const fetchChartData = async () => {
    try {
      const res = await api.get('/admin/analytics/control-chart');
      setChartData(res.data);
    } catch (err) {
      console.error(err);
      throw err;
    }
  };

  const downloadCSV = () => {
    const headers = ['Date', 'Material Cost', 'Cost of Pages', 'UPI Revenue', 'Cash Revenue', 'Total Order Amount'];
    const rows = chartData.map(d => [
      d.date,
      d.material_cost,
      d.cost_of_pages,
      d.upi_revenue || 0,
      d.cash_revenue || 0,
      d.order_amount
    ]);
    const csvContent = "data:text/csv;charset=utf-8," 
      + [headers.join(','), ...rows.map(e => e.join(','))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "control_chart_data.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const exportToDrive = async () => {
    setExporting(true);
    try {
      const res = await api.post('/admin/export-to-drive');
      alert(`Export successful! File available at:\n${res.data.drive_link}`);
    } catch (err) {
      console.error(err);
      alert('Export to Drive failed. Ensure your Service Account and Folder ID are configured.');
    } finally {
      setExporting(false);
    }
  };

  const visibleOrders = orders.filter(o => o.status !== 'CANCELLED');
  const completed = visibleOrders.filter(o => o.status === 'COMPLETED');
  const revenue = completed.reduce((sum, o) => sum + o.grand_total, 0);
  const pending = visibleOrders.filter(o => o.status !== 'COMPLETED');

  const chartJsData = {
    labels: chartData.map(d => d.date),
    datasets: [
      {
        label: 'Material Cost',
        data: chartData.map(d => d.material_cost),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
      },
      {
        label: 'Cost of Pages (Expenses)',
        data: chartData.map(d => d.cost_of_pages),
        borderColor: 'rgb(53, 162, 235)',
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
      },
      {
        label: 'UPI Revenue',
        data: chartData.map(d => d.upi_revenue || 0),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
      },
      {
        label: 'Cash Revenue',
        data: chartData.map(d => d.cash_revenue || 0),
        borderColor: 'rgb(153, 102, 255)',
        backgroundColor: 'rgba(153, 102, 255, 0.5)',
      }
    ],
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
      {error && <div className="p-4 bg-red-100 text-red-700 rounded-md border border-red-300 font-medium">{error}</div>}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-gray-500 text-sm">Total Orders</div>
          <div className="text-3xl font-bold text-gray-900">{visibleOrders.length}</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-gray-500 text-sm">Pending Orders</div>
          <div className="text-3xl font-bold text-yellow-600">{pending.length}</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-gray-500 text-sm">Completed Orders</div>
          <div className="text-3xl font-bold text-green-600">{completed.length}</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-gray-500 text-sm">Total Revenue</div>
          <div className="text-3xl font-bold text-blue-600">₹{revenue.toFixed(2)}</div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 mt-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-900">Control Chart (Revenue vs Expenses)</h2>
          <div className="space-x-2">
            <button onClick={downloadCSV} className="bg-gray-200 text-gray-800 px-4 py-2 rounded hover:bg-gray-300">
              Download CSV
            </button>
            <button onClick={exportToDrive} disabled={exporting} className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:bg-green-300 flex-inline items-center">
              {exporting ? 'Exporting...' : 'Export Data to Google Drive'}
            </button>
          </div>
        </div>
        {chartData.length > 0 ? (
          <div className="h-96">
            <Line data={chartJsData} options={{ responsive: true, maintainAspectRatio: false }} />
          </div>
        ) : (
          <p className="text-gray-500">No data available for chart.</p>
        )}
      </div>

      <h2 className="text-xl font-bold text-gray-900 mt-8 mb-4">Recent Feedback</h2>
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <ul className="divide-y divide-gray-200">
          {orders.filter(o => o.feedback_rating).slice(0, 10).map(order => (
            <li key={order.id} className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-semibold">{order.student_name}</div>
                  <div className="text-sm text-gray-500">{order.order_number}</div>
                </div>
                <div className="flex text-yellow-400">
                  {[...Array(5)].map((_, i) => (
                    <svg key={i} className={`w-5 h-5 ${i < order.feedback_rating ? 'text-yellow-400' : 'text-gray-300'}`} fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  ))}
                </div>
              </div>
              {order.feedback_text && (
                <p className="mt-2 text-sm text-gray-700 italic">"{order.feedback_text}"</p>
              )}
            </li>
          ))}
          {orders.filter(o => o.feedback_rating).length === 0 && (
            <li className="p-4 text-gray-500 text-center">No feedback received yet.</li>
          )}
        </ul>
      </div>
    </div>
  );
}
