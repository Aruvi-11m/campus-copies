import { useState, useEffect } from 'react';
import api from '../../api';

const CATEGORIES = {
  "Paper reams": [],
  "Photo sheet 135 gsm single side": [],
  "Photo sheet 180 gsm single side": [],
  "Glass sheet": [],
  "Stapler 45 hp": [],
  "Stapler pin": ["Small", "Medium", "Large", "Big"],
  "Tape": [],
  "Chart paper": [],
  "Canon ink": ["Cyan", "Magenta", "Red", "Black"],
  "Epson M1170 ink": []
};

export default function MaterialLogs() {
  const [logs, setLogs] = useState([]);
  const [category, setCategory] = useState("Paper reams");
  const [variant, setVariant] = useState("");
  const [quantity, setQuantity] = useState(1);
  const [totalCost, setTotalCost] = useState(0);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      const res = await api.get('/admin/materials');
      setLogs(res.data);
      setError(null);
    } catch (err) {
      console.error(err);
      setError('Cannot connect to backend server to fetch logs.');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/admin/materials', {
        category,
        variant: variant || null,
        quantity: parseInt(quantity),
        total_cost: parseFloat(totalCost)
      });
      alert('Material logged successfully');
      setQuantity(1);
      setTotalCost(0);
      fetchLogs();
    } catch (err) {
      console.error(err);
      alert('Failed to log material');
    }
  };

  const handleCategoryChange = (e) => {
    const newCategory = e.target.value;
    setCategory(newCategory);
    setVariant(CATEGORIES[newCategory].length > 0 ? CATEGORIES[newCategory][0] : "");
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Material Purchase Logs</h1>
      {error && <div className="p-4 bg-red-100 text-red-700 rounded-md border border-red-300 font-medium">{error}</div>}
      
      <div className="bg-white p-6 rounded shadow-sm border border-gray-200">
        <h2 className="text-lg font-semibold mb-4">Add New Purchase</h2>
        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-5 gap-4 items-end">
          <div>
            <label className="block text-sm font-medium text-gray-700">Category</label>
            <select value={category} onChange={handleCategoryChange} className="mt-1 w-full border rounded p-2" required>
              {Object.keys(CATEGORIES).map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Variant/Size</label>
            <select value={variant} onChange={(e) => setVariant(e.target.value)} className="mt-1 w-full border rounded p-2" disabled={CATEGORIES[category].length === 0}>
              {CATEGORIES[category].map(v => (
                <option key={v} value={v}>{v}</option>
              ))}
              {CATEGORIES[category].length === 0 && <option value="">N/A</option>}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Quantity (Nos)</label>
            <input type="number" min="1" value={quantity} onChange={e => setQuantity(e.target.value)} className="mt-1 w-full border rounded p-2" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Total Cost (₹)</label>
            <input type="number" step="0.01" min="0" value={totalCost} onChange={e => setTotalCost(e.target.value)} className="mt-1 w-full border rounded p-2" required />
          </div>
          <div>
            <button type="submit" className="w-full bg-blue-600 text-white font-medium py-2 rounded hover:bg-blue-700">Log Purchase</button>
          </div>
        </form>
      </div>

      <div className="bg-white rounded shadow-sm border border-gray-200 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Item</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Qty</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cost</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {logs.map((log) => (
              <tr key={log.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(log.purchased_at).toLocaleString()}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{log.category} {log.variant ? `(${log.variant})` : ''}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{log.quantity}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">₹{log.total_cost.toFixed(2)}</td>
              </tr>
            ))}
            {logs.length === 0 && (
              <tr>
                <td colSpan="4" className="px-6 py-4 text-center text-gray-500">No purchases logged yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
