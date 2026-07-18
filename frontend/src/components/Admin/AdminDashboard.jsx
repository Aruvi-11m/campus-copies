import { useState, useEffect } from 'react';
import api from '../../api';

export default function AdminDashboard() {
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const res = await api.get('/admin/orders');
      setOrders(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const completed = orders.filter(o => o.status === 'COMPLETED');
  const revenue = completed.reduce((sum, o) => sum + o.grand_total, 0);
  const pending = orders.filter(o => o.status !== 'COMPLETED');

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-gray-500 text-sm">Total Orders</div>
          <div className="text-3xl font-bold text-gray-900">{orders.length}</div>
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
    </div>
  );
}
