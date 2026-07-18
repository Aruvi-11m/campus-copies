import { useState, useEffect } from 'react';
import api from '../../api';

export default function OrderManagement() {
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const res = await api.get('/admin/orders');
      setOrders(res.data);
    } catch (err) {
      console.error(err);
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

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Order Management</h1>
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
            {orders.map(order => (
              <tr key={order.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {order.order_number}<br/>
                  <span className="text-xs text-gray-500">{new Date(order.created_at).toLocaleDateString()}</span>
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
                    <>
                      <button onClick={() => updateStatus(order.id, 'PAYMENT_RECEIVED')} className="text-green-600 hover:text-green-900">Approve</button>
                      <button onClick={() => updateStatus(order.id, 'PENDING_PAYMENT')} className="text-red-600 hover:text-red-900">Reject</button>
                    </>
                  )}
                  {order.status === 'PRINTING' && order.color === 'color' && (
                    <button onClick={() => updateStatus(order.id, 'READY_FOR_PICKUP')} className="text-blue-600 hover:text-blue-900">Mark Printed</button>
                  )}
                  {order.status === 'READY_FOR_PICKUP' && (
                    <button onClick={() => updateStatus(order.id, 'COMPLETED')} className="text-indigo-600 hover:text-indigo-900">Mark Picked Up</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
