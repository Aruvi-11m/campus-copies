import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../api';

export default function StudentLogin() {
  const [mobile, setMobile] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const formData = new URLSearchParams();
      formData.append('username', mobile);
      formData.append('password', password);
      
      const res = await api.post('/auth/student/login', formData);
      localStorage.setItem('token', res.data.access_token);
      localStorage.setItem('role', res.data.role);
      navigate('/student/dashboard');
    } catch (err) {
      setError('Invalid credentials');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-campus-light">
      <div className="bg-white p-8 rounded-lg shadow-md w-96 border-t-4 border-campus-blue">
        <h2 className="text-2xl font-bold mb-6 text-center text-campus-blue">Campus Copies</h2>
        {error && <div className="text-red-500 mb-4 text-center text-sm">{error}</div>}
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Mobile Number</label>
            <input type="text" value={mobile} onChange={e => setMobile(e.target.value)} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Password</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border" required />
          </div>
          <button type="submit" className="w-full bg-campus-blue text-white p-2 rounded-md hover:bg-blue-800 transition">Login</button>
        </form>
      </div>
    </div>
  );
}
