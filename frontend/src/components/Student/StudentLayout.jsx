import { Outlet, Link, useNavigate } from 'react-router-dom';

export default function StudentLayout() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    navigate('/student/login');
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <nav className="bg-campus-blue text-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex space-x-8">
              <span className="font-bold text-xl">Campus Copies</span>
              <Link to="/student/dashboard" className="hover:text-gray-300 px-3 py-2 rounded-md text-sm font-medium">Dashboard</Link>
              <Link to="/student/new-order" className="hover:text-gray-300 px-3 py-2 rounded-md text-sm font-medium">New Order</Link>
            </div>
            <button onClick={handleLogout} className="text-sm font-medium bg-blue-700 px-4 py-2 rounded hover:bg-blue-800">
              Logout
            </button>
          </div>
        </div>
      </nav>
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
        <Outlet />
      </main>
    </div>
  );
}
