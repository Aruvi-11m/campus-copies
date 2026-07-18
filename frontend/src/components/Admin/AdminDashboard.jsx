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
