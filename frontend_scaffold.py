import os

FRONTEND_DIR = "/Users/thamizaruvi/.gemini/antigravity-ide/scratch/campus_copies/frontend"

files_to_create = {
    "package.json": """{
  "name": "frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "eslint .",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.6.8",
    "jwt-decode": "^4.0.0",
    "lucide-react": "^0.364.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.22.3"
  },
  "devDependencies": {
    "@types/react": "^18.2.66",
    "@types/react-dom": "^18.2.22",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.19",
    "eslint": "^8.57.0",
    "postcss": "^8.4.38",
    "tailwindcss": "^3.4.3",
    "vite": "^5.2.0"
  }
}
""",
    "vite.config.js": """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
""",
    "tailwind.config.js": """/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
""",
    "postcss.config.js": """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
""",
    "index.html": """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Campus Copies</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
""",
    "src/index.css": """@tailwind base;
@tailwind components;
@tailwind utilities;
""",
    "src/main.jsx": """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { AuthProvider } from './context/AuthContext'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </React.StrictMode>,
)
""",
    "src/api/index.js": """import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
""",
    "src/context/AuthContext.jsx": """import React, { createContext, useState, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';
import api from '../api';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const decoded = jwtDecode(token);
        setUser(decoded);
      } catch (e) {
        localStorage.removeItem('token');
      }
    }
    setLoading(false);
  }, []);

  const login = async (mobile_number, password) => {
    const formData = new FormData();
    formData.append('username', mobile_number);
    formData.append('password', password);
    const response = await api.post('/auth/login', formData);
    localStorage.setItem('token', response.data.access_token);
    setUser(jwtDecode(response.data.access_token));
    return response.data;
  };

  const register = async (userData) => {
    await api.post('/auth/register', userData);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, register, loading }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
""",
    "src/App.jsx": """import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useContext } from 'react';
import { AuthContext } from './context/AuthContext';
import Login from './pages/student/Login';
import Register from './pages/student/Register';
import Dashboard from './pages/student/Dashboard';
import NewOrder from './pages/student/NewOrder';
import AdminLogin from './pages/admin/AdminLogin';
import AdminDashboard from './pages/admin/AdminDashboard';
import OrdersList from './pages/admin/OrdersList';
import Settings from './pages/admin/Settings';

const PrivateRoute = ({ children, role }) => {
  const { user } = useContext(AuthContext);
  if (!user) return <Navigate to={role === 'admin' ? "/admin/login" : "/login"} />;
  if (role && user.role !== role) return <Navigate to="/" />;
  return children;
};

function App() {
  return (
    <Router>
      <Routes>
        {/* Student Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<PrivateRoute role="student"><Dashboard /></PrivateRoute>} />
        <Route path="/new-order" element={<PrivateRoute role="student"><NewOrder /></PrivateRoute>} />
        
        {/* Admin Routes */}
        <Route path="/admin/login" element={<AdminLogin />} />
        <Route path="/admin/dashboard" element={<PrivateRoute role="admin"><AdminDashboard /></PrivateRoute>} />
        <Route path="/admin/orders" element={<PrivateRoute role="admin"><OrdersList /></PrivateRoute>} />
        <Route path="/admin/settings" element={<PrivateRoute role="admin"><Settings /></PrivateRoute>} />

        <Route path="/" element={<Navigate to="/login" />} />
      </Routes>
    </Router>
  );
}

export default App;
""",
    "src/pages/student/Login.jsx": """import { useState, useContext } from 'react';
import { AuthContext } from '../../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

export default function Login() {
  const [mobile, setMobile] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = await login(mobile, password);
      if(data.role === 'admin') {
          navigate('/admin/dashboard');
      } else {
          navigate('/dashboard');
      }
    } catch (err) {
      setError('Invalid credentials');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-center mb-6">Student Login</h2>
        {error && <div className="text-red-500 mb-4">{error}</div>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Mobile Number</label>
            <input type="text" required value={mobile} onChange={e => setMobile(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Password</label>
            <input type="password" required value={password} onChange={e => setPassword(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2" />
          </div>
          <button type="submit" className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700">
            Login
          </button>
        </form>
        <div className="mt-4 text-center">
          <Link to="/register" className="text-indigo-600 hover:text-indigo-500">Need an account? Register</Link>
        </div>
      </div>
    </div>
  );
}
""",
    "src/pages/student/Register.jsx": """import { useState, useContext } from 'react';
import { AuthContext } from '../../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

export default function Register() {
  const [formData, setFormData] = useState({ name: '', department: '', mobile_number: '', password: '' });
  const { register } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await register(formData);
      navigate('/login');
    } catch (err) {
      alert('Registration failed');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-center mb-6">Register</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input type="text" placeholder="Name" required className="w-full border p-2 rounded"
            onChange={e => setFormData({...formData, name: e.target.value})} />
          <input type="text" placeholder="Department" required className="w-full border p-2 rounded"
            onChange={e => setFormData({...formData, department: e.target.value})} />
          <input type="text" placeholder="Mobile Number" required className="w-full border p-2 rounded"
            onChange={e => setFormData({...formData, mobile_number: e.target.value})} />
          <input type="password" placeholder="Password" required className="w-full border p-2 rounded"
            onChange={e => setFormData({...formData, password: e.target.value})} />
          <button type="submit" className="w-full bg-indigo-600 text-white p-2 rounded">Register</button>
        </form>
        <div className="mt-4 text-center">
          <Link to="/login" className="text-indigo-600 hover:text-indigo-500">Back to Login</Link>
        </div>
      </div>
    </div>
  );
}
""",
    "src/pages/student/Dashboard.jsx": """import { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api';
import { AuthContext } from '../../context/AuthContext';

export default function Dashboard() {
  const [orders, setOrders] = useState([]);
  const { logout } = useContext(AuthContext);

  useEffect(() => {
    api.get('/orders/').then(res => setOrders(res.data)).catch(console.error);
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">My Orders</h1>
          <div>
            <Link to="/new-order" className="bg-indigo-600 text-white px-4 py-2 rounded shadow mr-4">New Print Order</Link>
            <button onClick={logout} className="text-gray-600">Logout</button>
          </div>
        </div>
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {orders.map(order => (
              <li key={order.id} className="p-4">
                <div className="flex justify-between">
                  <div>
                    <p className="font-medium text-gray-900">Order #{order.id}</p>
                    <p className="text-sm text-gray-500">Pickup Code: <span className="font-bold">{order.pickup_code}</span></p>
                    <p className="text-sm text-gray-500">Status: {order.status}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold">₹{order.total_cost}</p>
                    <p className="text-sm text-gray-500">{new Date(order.created_at).toLocaleDateString()}</p>
                  </div>
                </div>
              </li>
            ))}
            {orders.length === 0 && <li className="p-4 text-center text-gray-500">No orders yet</li>}
          </ul>
        </div>
      </div>
    </div>
  );
}
""",
    "src/pages/student/NewOrder.jsx": """import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../api';

export default function NewOrder() {
  const [file, setFile] = useState(null);
  const [printType, setPrintType] = useState('single_side');
  const [colorType, setColorType] = useState('black_and_white');
  const [copies, setCopies] = useState(1);
  const [bindingType, setBindingType] = useState('none');
  const [transactionId, setTransactionId] = useState('');
  const [screenshot, setScreenshot] = useState(null);
  const [step, setStep] = useState(1);
  const [order, setOrder] = useState(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleCreateOrder = async (e) => {
    e.preventDefault();
    if (!file) return setError('Please upload a PDF');
    try {
      // 1. Upload PDF
      const fd = new FormData();
      fd.append('file', file);
      const fileRes = await api.post('/uploads/pdf', fd);
      
      // 2. Create Order
      const orderRes = await api.post('/orders/', {
        file_id: fileRes.data.id,
        print_type: printType,
        color_type: colorType,
        copies: parseInt(copies),
        binding_type: bindingType,
      });
      setOrder(orderRes.data);
      setStep(2);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error creating order');
    }
  };

  const handlePaymentSubmit = async (e) => {
    e.preventDefault();
    if (!screenshot || !transactionId) return setError('Provide transaction ID and screenshot');
    try {
      const fd = new FormData();
      fd.append('file', screenshot);
      await api.post(`/uploads/payment-screenshot?transaction_id=${transactionId}&order_id=${order.id}`, fd);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Error uploading payment');
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 mt-10 bg-white shadow-md rounded">
      <h2 className="text-2xl font-bold mb-4">Create New Order</h2>
      {error && <div className="text-red-500 mb-4">{error}</div>}
      
      {step === 1 && (
        <form onSubmit={handleCreateOrder} className="space-y-4">
          <div>
            <label className="block text-sm font-medium">Upload PDF</label>
            <input type="file" accept=".pdf" onChange={e => setFile(e.target.files[0])} className="mt-1 block w-full border p-2" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm">Print Type</label>
              <select value={printType} onChange={e => setPrintType(e.target.value)} className="w-full border p-2">
                <option value="single_side">Single Side</option>
                <option value="double_side">Double Side</option>
              </select>
            </div>
            <div>
              <label className="block text-sm">Color Type</label>
              <select value={colorType} onChange={e => setColorType(e.target.value)} className="w-full border p-2">
                <option value="black_and_white">Black & White</option>
                <option value="color">Color</option>
              </select>
            </div>
            <div>
              <label className="block text-sm">Copies</label>
              <input type="number" min="1" value={copies} onChange={e => setCopies(e.target.value)} className="w-full border p-2" />
            </div>
            <div>
              <label className="block text-sm">Binding</label>
              <select value={bindingType} onChange={e => setBindingType(e.target.value)} className="w-full border p-2">
                <option value="none">None</option>
                <option value="spiral">Spiral Binding</option>
                <option value="soft">Soft Binding</option>
              </select>
            </div>
          </div>
          <button type="submit" className="w-full bg-indigo-600 text-white p-2 rounded">Calculate Cost & Continue</button>
        </form>
      )}

      {step === 2 && order && (
        <form onSubmit={handlePaymentSubmit} className="space-y-4">
          <div className="bg-gray-100 p-4 rounded">
            <h3 className="font-bold">Total Cost: ₹{order.total_cost}</h3>
            <p className="text-sm mt-2">Please pay to the UPI ID: <strong>campuscopies@upi</strong> (Check settings if changed)</p>
          </div>
          <div>
            <label className="block text-sm">Transaction ID</label>
            <input type="text" required value={transactionId} onChange={e => setTransactionId(e.target.value)} className="w-full border p-2" />
          </div>
          <div>
            <label className="block text-sm">Upload Screenshot</label>
            <input type="file" accept="image/*" onChange={e => setScreenshot(e.target.files[0])} className="w-full border p-2" />
          </div>
          <button type="submit" className="w-full bg-green-600 text-white p-2 rounded">Submit Payment Info</button>
        </form>
      )}
    </div>
  );
}
""",
    "src/pages/admin/AdminLogin.jsx": """import { useState, useContext } from 'react';
import { AuthContext } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function AdminLogin() {
  const [mobile, setMobile] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = await login(mobile, password);
      if (data.role === 'admin') navigate('/admin/dashboard');
      else alert('Not an admin account');
    } catch (err) {
      alert('Login failed');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-800">
      <div className="max-w-md w-full p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-center mb-6">Admin Portal</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input type="text" placeholder="Admin Mobile/ID" required value={mobile} onChange={e => setMobile(e.target.value)} className="w-full border p-2 rounded" />
          <input type="password" placeholder="Password" required value={password} onChange={e => setPassword(e.target.value)} className="w-full border p-2 rounded" />
          <button type="submit" className="w-full bg-gray-900 text-white p-2 rounded">Login to Dashboard</button>
        </form>
      </div>
    </div>
  );
}
""",
    "src/pages/admin/AdminDashboard.jsx": """import { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api';
import { AuthContext } from '../../context/AuthContext';

export default function AdminDashboard() {
  const [stats, setStats] = useState({});
  const { logout } = useContext(AuthContext);

  useEffect(() => {
    api.get('/admin/dashboard/stats').then(res => setStats(res.data)).catch(console.error);
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 flex">
      <div className="w-64 bg-gray-900 text-white p-6">
        <h2 className="text-2xl font-bold mb-8">Admin Panel</h2>
        <nav className="space-y-4 flex flex-col">
          <Link to="/admin/dashboard" className="text-gray-300 hover:text-white">Dashboard</Link>
          <Link to="/admin/orders" className="text-gray-300 hover:text-white">Orders</Link>
          <Link to="/admin/settings" className="text-gray-300 hover:text-white">Settings</Link>
          <button onClick={logout} className="text-left text-gray-300 hover:text-white mt-8">Logout</button>
        </nav>
      </div>
      <div className="flex-1 p-8">
        <h1 className="text-3xl font-bold mb-6">Dashboard Overview</h1>
        <div className="grid grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded shadow">
            <h3 className="text-gray-500">Total Orders</h3>
            <p className="text-3xl font-bold">{stats.total_orders || 0}</p>
          </div>
          <div className="bg-white p-6 rounded shadow">
            <h3 className="text-gray-500">Pending Orders</h3>
            <p className="text-3xl font-bold">{stats.pending_orders || 0}</p>
          </div>
          <div className="bg-white p-6 rounded shadow">
            <h3 className="text-gray-500">Completed Orders</h3>
            <p className="text-3xl font-bold">{stats.completed_orders || 0}</p>
          </div>
          <div className="bg-white p-6 rounded shadow">
            <h3 className="text-gray-500">Total Revenue</h3>
            <p className="text-3xl font-bold text-green-600">₹{stats.revenue || 0}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
""",
    "src/pages/admin/OrdersList.jsx": """import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api';

export default function OrdersList() {
  const [orders, setOrders] = useState([]);

  const fetchOrders = () => {
    api.get('/admin/orders').then(res => setOrders(res.data)).catch(console.error);
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const updateStatus = async (id, status) => {
    try {
      await api.put(`/admin/orders/${id}/status?status=${status}`);
      fetchOrders();
    } catch (e) { console.error(e); }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex">
      <div className="w-64 bg-gray-900 text-white p-6">
        <h2 className="text-2xl font-bold mb-8">Admin Panel</h2>
        <nav className="space-y-4 flex flex-col">
          <Link to="/admin/dashboard" className="text-gray-300 hover:text-white">Dashboard</Link>
          <Link to="/admin/orders" className="text-gray-300 hover:text-white">Orders</Link>
          <Link to="/admin/settings" className="text-gray-300 hover:text-white">Settings</Link>
        </nav>
      </div>
      <div className="flex-1 p-8">
        <h1 className="text-3xl font-bold mb-6">Manage Orders</h1>
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cost</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {orders.map(order => (
                <tr key={order.id}>
                  <td className="px-6 py-4 whitespace-nowrap">{order.pickup_code}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{order.print_type} | {order.color_type}</td>
                  <td className="px-6 py-4 whitespace-nowrap">₹{order.total_cost}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                      {order.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <select 
                      value={order.status} 
                      onChange={(e) => updateStatus(order.id, e.target.value)}
                      className="border p-1 rounded"
                    >
                      <option value="Pending Payment">Pending Payment</option>
                      <option value="Payment Verification">Payment Verification</option>
                      <option value="Payment Received">Payment Received</option>
                      <option value="Printing">Printing</option>
                      <option value="Ready For Pickup">Ready For Pickup</option>
                      <option value="Completed">Completed</option>
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
""",
    "src/pages/admin/Settings.jsx": """import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api';

export default function Settings() {
  const [settings, setSettings] = useState([]);

  useEffect(() => {
    api.get('/settings/').then(res => setSettings(res.data)).catch(console.error);
  }, []);

  const handleChange = (index, value) => {
    const newSettings = [...settings];
    newSettings[index].value = value;
    setSettings(newSettings);
  };

  const handleSave = async (setting) => {
    try {
      await api.put(`/settings/${setting.key}`, setting);
      alert('Saved');
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex">
      <div className="w-64 bg-gray-900 text-white p-6">
        <h2 className="text-2xl font-bold mb-8">Admin Panel</h2>
        <nav className="space-y-4 flex flex-col">
          <Link to="/admin/dashboard" className="text-gray-300 hover:text-white">Dashboard</Link>
          <Link to="/admin/orders" className="text-gray-300 hover:text-white">Orders</Link>
          <Link to="/admin/settings" className="text-gray-300 hover:text-white">Settings</Link>
        </nav>
      </div>
      <div className="flex-1 p-8">
        <h1 className="text-3xl font-bold mb-6">Pricing Settings</h1>
        <div className="bg-white shadow rounded p-6 max-w-2xl">
          {settings.map((s, i) => (
            <div key={s.key} className="mb-4 flex items-center justify-between">
              <div className="w-1/2">
                <p className="font-bold">{s.key}</p>
                <p className="text-sm text-gray-500">{s.description}</p>
              </div>
              <input type="text" value={s.value} onChange={e => handleChange(i, e.target.value)} className="border p-2 rounded w-1/3" />
              <button onClick={() => handleSave(s)} className="bg-blue-600 text-white px-4 py-2 rounded">Save</button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
"""
}

for rel_path, content in files_to_create.items():
    file_path = os.path.join(FRONTEND_DIR, rel_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        f.write(content)

print("Frontend scaffolding complete.")
