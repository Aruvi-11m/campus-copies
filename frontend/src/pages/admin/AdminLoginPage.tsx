import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { adminLogin } from '../../api/auth';
import { useAuth } from '../../hooks/useAuth';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';
import { Card } from '../../components/common/Card';
import { ShieldCheck } from 'lucide-react';

export const AdminLoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleAdminAuth = async (user: string, pass: string) => {
    setError('');
    setIsLoading(true);
    try {
      const data = await adminLogin(user, pass);
      login(data, true);
      navigate('/admin');
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Invalid username or password';
      setError(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleAdminAuth(username, password);
  };

  return (
    <Card className="px-4 py-8 sm:px-10 max-w-lg mx-auto shadow-lg border border-gray-100">
      <div className="sm:mx-auto sm:w-full text-center mb-8">
        <div className="mx-auto h-14 w-14 bg-gradient-to-tr from-blue-600 to-indigo-600 rounded-2xl flex items-center justify-center mb-4 shadow-md text-white">
          <ShieldCheck className="h-7 w-7" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900">Campus Copies ERP</h2>
        <p className="mt-2 text-sm text-gray-600">Dual-Admin Management Portal</p>
      </div>

      {/* Quick Dual Admin Selector */}
      <div className="mb-6 bg-slate-50 p-4 rounded-xl border border-slate-200">
        <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 text-center">
          Quick Dual Admin Login
        </p>
        <div className="grid grid-cols-2 gap-3">
          <button
            type="button"
            onClick={() => handleAdminAuth('thamizaruvi', 'admin123')}
            disabled={isLoading}
            className="flex flex-col items-center justify-center p-3 rounded-lg border border-indigo-200 bg-white hover:bg-indigo-50 hover:border-indigo-300 transition-all group text-left shadow-sm"
          >
            <span className="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-xs mb-1">
              T
            </span>
            <span className="text-sm font-semibold text-gray-900 group-hover:text-indigo-600">
              Thamizaruvi
            </span>
            <span className="text-[10px] text-indigo-600 font-medium">Primary Admin</span>
          </button>

          <button
            type="button"
            onClick={() => handleAdminAuth('barathwaj', 'admin123')}
            disabled={isLoading}
            className="flex flex-col items-center justify-center p-3 rounded-lg border border-emerald-200 bg-white hover:bg-emerald-50 hover:border-emerald-300 transition-all group text-left shadow-sm"
          >
            <span className="w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center font-bold text-xs mb-1">
              B
            </span>
            <span className="text-sm font-semibold text-gray-900 group-hover:text-emerald-600">
              Barathwaj
            </span>
            <span className="text-[10px] text-emerald-600 font-medium">Co-Admin</span>
          </button>
        </div>
      </div>

      <div className="relative flex py-2 items-center mb-6">
        <div className="flex-grow border-t border-gray-200"></div>
        <span className="flex-shrink mx-4 text-xs text-gray-400 font-medium uppercase">Or Custom Sign In</span>
        <div className="flex-grow border-t border-gray-200"></div>
      </div>

      <form className="space-y-5" onSubmit={handleSubmit}>
        {error && (
          <div className="bg-red-50 border-l-4 border-red-400 p-3 rounded-r">
            <p className="text-xs text-red-700">{error}</p>
          </div>
        )}

        <Input
          id="username"
          label="Username"
          type="text"
          required
          placeholder="e.g. thamizaruvi or barathwaj"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          disabled={isLoading}
        />

        <Input
          id="password"
          label="Password"
          type="password"
          required
          placeholder="••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          disabled={isLoading}
        />

        <div>
          <Button type="submit" className="w-full bg-indigo-600 hover:bg-indigo-700" isLoading={isLoading}>
            Sign in to ERP
          </Button>
        </div>
      </form>
    </Card>
  );
};
