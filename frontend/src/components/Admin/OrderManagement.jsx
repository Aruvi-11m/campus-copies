import { useState, useEffect } from 'react';
import api from '../../api';

export default function OrderManagement() {
  const [orders, setOrders] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const res = await api.get('/admin/orders');
      setOrders(res.data);
      setError(null);
    } catch (err) {
      console.error(err);
      setError('Cannot connect to backend server to fetch orders.');
    }
  };

  const updateStatus = async (orderId, newStatus) => {
    try {
      await api.put(`/admin/orders/${orderId}/status`, { status: newStatus });
      fetchOrders();
    } catch (err) {
      alert("Failed to update status");
    }
  };

  const cancelOrder = async (orderId) => {
    if (!confirm('Are you sure you want to cancel this order?')) return;
    try {
      await api.put(`/admin/orders/${orderId}/cancel`);
      fetchOrders();
    } catch (err) {
      alert("Failed to cancel order");
    }
  };

  const deleteOrder = async (orderId) => {
    if (!confirm('Are you sure you want to permanently delete this fake order?')) return;
    try {
      await api.delete(`/admin/orders/${orderId}`);
      fetchOrders();
    } catch (err) {
      alert("Failed to delete order");
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Order Management</h1>
      {error && <div className="p-4 bg-red-100 text-red-700 rounded-md border border-red-300 font-medium">{error}</div>}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order #</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Details</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {orders.filter(o => o.status !== 'CANCELLED').map(order => (
              <tr key={order.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {order.order_number}<br/>
                  <span className="text-xs text-gray-500">{new Date(order.created_at).toLocaleDateString()}</span>
                  <div className="mt-1 text-xs font-semibold text-blue-700">{order.student_name}</div>
                  <div className="text-xs text-gray-500">{order.student_department}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {order.print_type} | {order.color} | {order.binding} | {order.copies}x
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">₹{order.grand_total.toFixed(2)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">
                    {order.status.replace(/_/g, ' ')}
                  </span>
                  {order.pickup_code && <div className="mt-1 font-mono text-xs">Code: {order.pickup_code}</div>}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                  {order.status === 'PAYMENT_VERIFICATION' && (
                    <div className="flex flex-col space-y-2">
                      <div className="text-xs text-gray-500">
                        Txn ID: {order.payment_transaction_id}
                        <br/>
                        <a href={`${api.defaults.baseURL}/${order.payment_screenshot_path}`} target="_blank" rel="noreferrer" className="text-blue-500 underline">View Screenshot</a>
                      </div>
                      <div className="space-x-2">
                        <button onClick={() => updateStatus(order.id, 'PAYMENT_RECEIVED')} className="text-green-600 hover:text-green-900">Approve</button>
                        <button onClick={() => updateStatus(order.id, 'PENDING_PAYMENT')} className="text-red-600 hover:text-red-900">Reject</button>
                      </div>
                    </div>
                  )}
                  {order.status !== 'PAYMENT_VERIFICATION' && order.payment_transaction_id && (
                    <div className="text-xs text-gray-500 mb-2">
                      Txn: {order.payment_transaction_id}
                      <br/>
                      <a href={`${api.defaults.baseURL}/${order.payment_screenshot_path}`} target="_blank" rel="noreferrer" className="text-blue-500 underline">Proof</a>
                    </div>
                  )}
                  <div className="text-xs mt-1 mb-2">
                      <a href={`${api.defaults.baseURL}/${order.file_path}`} target="_blank" rel="noreferrer" className="text-blue-600 underline font-semibold">View PDF</a>
                  </div>
                  {order.status === 'PRINTING' && order.color === 'color' && (
                    <button onClick={() => updateStatus(order.id, 'READY_FOR_PICKUP')} className="text-blue-600 hover:text-blue-900">Mark Printed</button>
                  )}
                  {order.status === 'READY_FOR_PICKUP' && (
                    <button onClick={() => updateStatus(order.id, 'COMPLETED')} className="text-indigo-600 hover:text-indigo-900">Mark Picked Up</button>
                  )}
                  {order.status !== 'CANCELLED' && order.status !== 'COMPLETED' && (
                     <button onClick={() => cancelOrder(order.id)} className="block mt-2 text-orange-600 hover:text-orange-900">Cancel</button>
                  )}
                  <button onClick={() => deleteOrder(order.id)} className="block mt-2 text-red-600 hover:text-red-900 text-xs">Delete (Spam)</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
