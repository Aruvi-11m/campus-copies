import { useState, useEffect } from 'react';
import api from '../../api';

export default function StudentDashboard() {
  const [orders, setOrders] = useState([]);
  const [serviceActive, setServiceActive] = useState(true);

  useEffect(() => {
    fetchOrders();
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const res = await api.get('/public/settings');
      setServiceActive(res.data.service_active ?? true);
    } catch (err) {
      console.error('Failed to fetch settings', err);
    }
  };

  const fetchOrders = async () => {
    try {
      const res = await api.get('/orders');
      setOrders(res.data);
    } catch (error) {
      console.error('Failed to fetch orders', error);
    }
  };

  const cancelOrder = async (orderId) => {
    if (!confirm('Are you sure you want to cancel this order?')) return;
    try {
      await api.put(`/orders/${orderId}/cancel`);
      fetchOrders();
    } catch (err) {
      alert("Failed to cancel order");
    }
  };

  const submitFeedback = async (orderId) => {
    const ratingStr = prompt('Rate this order from 1 to 5:');
    if (!ratingStr) return;
    const rating = parseInt(ratingStr);
    if (rating < 1 || rating > 5 || isNaN(rating)) {
      alert('Invalid rating');
      return;
    }
    const text = prompt('Any additional feedback? (optional)') || '';
    
    try {
      await api.post(`/orders/${orderId}/feedback`, { rating, text });
      fetchOrders();
      alert('Feedback submitted! Thank you.');
    } catch (err) {
      alert("Failed to submit feedback");
    }
  };

  const completedOrders = orders.filter(o => o.status === 'COMPLETED');
  const pendingOrders = orders.filter(o => o.status !== 'COMPLETED');
  const totalSpent = completedOrders.reduce((sum, o) => sum + o.grand_total, 0);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
      
      {!serviceActive && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
          <p className="text-red-700 font-bold">Service is not available at the moment.</p>
          <p className="text-red-600 mt-1">Contact ARV for further on-demand orders.</p>
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-gray-500 text-sm">Total Orders</div>
          <div className="text-3xl font-bold text-campus-blue">{orders.length}</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-gray-500 text-sm">Amount Spent</div>
          <div className="text-3xl font-bold text-campus-blue">₹{totalSpent.toFixed(2)}</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-gray-500 text-sm">Completed</div>
          <div className="text-3xl font-bold text-green-600">{completedOrders.length}</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-gray-500 text-sm">Pending</div>
          <div className="text-3xl font-bold text-yellow-600">{pendingOrders.length}</div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold">Order History</h2>
        </div>
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order #</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">File</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pickup Code</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {orders.map(order => (
              <tr key={order.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{order.order_number}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(order.created_at).toLocaleDateString()}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{order.original_filename}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">₹{order.grand_total.toFixed(2)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                    ${order.status === 'COMPLETED' ? 'bg-green-100 text-green-800' : 
                      order.status === 'READY_FOR_PICKUP' ? 'bg-blue-100 text-blue-800' : 'bg-yellow-100 text-yellow-800'}`}>
                    {order.status.replace(/_/g, ' ')}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-mono font-bold">
                  {order.pickup_code || '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                  {(order.status === 'PENDING_PAYMENT' || order.status === 'PAYMENT_VERIFICATION') && (
                    <button onClick={() => cancelOrder(order.id)} className="text-red-600 hover:text-red-900">Cancel</button>
                  )}
                  {order.status === 'COMPLETED' && !order.feedback_rating && (
                    <button onClick={() => submitFeedback(order.id)} className="text-blue-600 hover:text-blue-900">Leave Feedback</button>
                  )}
                  {order.status === 'COMPLETED' && order.feedback_rating && (
                    <span className="text-gray-500">Rated {order.feedback_rating}/5</span>
                  )}
                </td>
              </tr>
            ))}
            {orders.length === 0 && (
              <tr>
                <td colSpan="6" className="px-6 py-4 text-center text-gray-500">No orders found.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
