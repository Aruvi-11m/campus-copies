import { useState, useEffect } from 'react';
import api from '../../api';

export default function Settings() {
  const [pricing, setPricing] = useState(null);
  const [costs, setCosts] = useState(null);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const [resPricing, resCosts] = await Promise.all([
        api.get('/admin/pricing'),
        api.get('/admin/cost')
      ]);
      setPricing(resPricing.data);
      setCosts(resCosts.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handlePricingChange = (e) => {
    const { name, value, type } = e.target;
    setPricing({ ...pricing, [name]: type === 'number' ? (parseFloat(value) || 0) : value });
  };

  const handleCostsChange = (e) => {
    const { name, value, type } = e.target;
    setCosts({ ...costs, [name]: type === 'number' ? (parseFloat(value) || 0) : value });
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const res = await api.post('/admin/pricing/qr-code', formData);
      setPricing(res.data);
      alert('QR Code uploaded successfully!');
    } catch (err) {
      console.error(err);
      alert('Failed to upload QR Code');
    }
  };

  const savePricing = async (e) => {
    e.preventDefault();
    try {
      await api.put('/admin/pricing', pricing);
      alert('Pricing settings saved!');
    } catch (err) {
      alert('Failed to save pricing settings');
    }
  };

  const saveCosts = async (e) => {
    e.preventDefault();
    try {
      await api.put('/admin/cost', costs);
      alert('Internal cost settings saved!');
    } catch (err) {
      alert('Failed to save cost settings');
    }
  };

  if (!pricing || !costs) return <div>Loading...</div>;

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-gray-900">Settings & Pricing</h1>
      
      <div className="grid grid-cols-2 gap-8">
        {/* Pricing Settings (Public) */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h2 className="text-lg font-bold mb-4">Pricing Settings (Student Facing)</h2>
          <form onSubmit={savePricing} className="space-y-4">
            <div><label className="block text-sm font-medium">Single Side Price</label><input type="number" step="0.01" name="single_side_price" value={pricing.single_side_price} onChange={handlePricingChange} className="mt-1 block w-full rounded border p-2"/></div>
            <div><label className="block text-sm font-medium">Double Side Price</label><input type="number" step="0.01" name="double_side_price" value={pricing.double_side_price} onChange={handlePricingChange} className="mt-1 block w-full rounded border p-2"/></div>
            <div><label className="block text-sm font-medium">Multi Page Price</label><input type="number" step="0.01" name="multi_page_price" value={pricing.multi_page_price} onChange={handlePricingChange} className="mt-1 block w-full rounded border p-2"/></div>
            <div><label className="block text-sm font-medium">Color Surcharge (Per Page)</label><input type="number" step="0.01" name="color_price" value={pricing.color_price} onChange={handlePricingChange} className="mt-1 block w-full rounded border p-2"/></div>
            <div><label className="block text-sm font-medium">Spiral Binding Price</label><input type="number" step="0.01" name="spiral_binding_price" value={pricing.spiral_binding_price} onChange={handlePricingChange} className="mt-1 block w-full rounded border p-2"/></div>
            <div><label className="block text-sm font-medium">Soft Binding Price</label><input type="number" step="0.01" name="soft_binding_price" value={pricing.soft_binding_price} onChange={handlePricingChange} className="mt-1 block w-full rounded border p-2"/></div>
            <div><label className="block text-sm font-medium">GST %</label><input type="number" step="0.01" name="gst_percent" value={pricing.gst_percent} onChange={handlePricingChange} className="mt-1 block w-full rounded border p-2"/></div>
            <div><label className="block text-sm font-medium">UPI ID</label><input type="text" name="upi_id" value={pricing.upi_id || ''} onChange={handlePricingChange} className="mt-1 block w-full rounded border p-2"/></div>
            <div>
              <label className="block text-sm font-medium">QR Code</label>
              {pricing.qr_code_path && (
                <img src={`${api.defaults.baseURL}/${pricing.qr_code_path}`} alt="QR Code" className="w-32 h-32 mt-2 mb-2 object-contain border" />
              )}
              <input type="file" onChange={handleFileUpload} accept="image/*" className="mt-1 block w-full text-sm" />
            </div>
            <button type="submit" className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700">Save Pricing</button>
          </form>
        </div>

        {/* Cost Settings (Internal) */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h2 className="text-lg font-bold mb-4">Internal Cost Settings (Hidden)</h2>
          <form onSubmit={saveCosts} className="space-y-4">
            <div><label className="block text-sm font-medium">Paper Cost Per Sheet</label><input type="number" step="0.01" name="paper_cost_per_sheet" value={costs.paper_cost_per_sheet} onChange={handleCostsChange} className="mt-1 block w-full rounded border p-2"/></div>
            <div><label className="block text-sm font-medium">Printing Cost Per Page</label><input type="number" step="0.01" name="printing_cost_per_page" value={costs.printing_cost_per_page} onChange={handleCostsChange} className="mt-1 block w-full rounded border p-2"/></div>
            <div><label className="block text-sm font-medium">Ink Cost Per Page</label><input type="number" step="0.01" name="ink_cost_per_page" value={costs.ink_cost_per_page} onChange={handleCostsChange} className="mt-1 block w-full rounded border p-2"/></div>
            <div><label className="block text-sm font-medium">Spiral Binding Cost</label><input type="number" step="0.01" name="spiral_binding_cost" value={costs.spiral_binding_cost} onChange={handleCostsChange} className="mt-1 block w-full rounded border p-2"/></div>
            <div><label className="block text-sm font-medium">Soft Binding Cost</label><input type="number" step="0.01" name="soft_binding_cost" value={costs.soft_binding_cost} onChange={handleCostsChange} className="mt-1 block w-full rounded border p-2"/></div>
            <button type="submit" className="w-full bg-gray-800 text-white p-2 rounded hover:bg-gray-900">Save Internal Costs</button>
          </form>
        </div>
      </div>
    </div>
  );
}
