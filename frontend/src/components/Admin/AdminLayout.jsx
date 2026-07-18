import { Outlet, Link, useNavigate } from 'react-router-dom';

export default function AdminLayout() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    navigate('/admin/login');
  };

  return (
    <div className="min-h-screen flex bg-gray-100">
      <aside className="w-64 bg-gray-900 text-white flex flex-col">
        <div className="h-16 flex items-center px-6 border-b border-gray-800">
          <span className="font-bold text-xl text-white">Admin Panel</span>
        </div>
        <nav className="flex-1 px-4 py-4 space-y-2">
          <Link to="/admin/dashboard" className="block px-4 py-2 rounded text-gray-300 hover:bg-gray-800 hover:text-white">Dashboard</Link>
          <Link to="/admin/orders" className="block px-4 py-2 rounded text-gray-300 hover:bg-gray-800 hover:text-white">Orders</Link>
          <Link to="/admin/settings" className="block px-4 py-2 rounded text-gray-300 hover:bg-gray-800 hover:text-white">Settings & Pricing</Link>
          {/* Missing links for Inventory, Sales, Customers, Profit Calculator, etc. - adding a placeholder for brevity */}
        </nav>
        <div className="p-4 border-t border-gray-800">
          <button onClick={handleLogout} className="w-full bg-red-600 text-white py-2 rounded hover:bg-red-700">Logout</button>
        </div>
      </aside>
      <main className="flex-1 overflow-auto">
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
