import React, { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import { LabLivreLogo } from '../components/LabLivreLogo';

export function Login({ onLogin }: { onLogin: () => void }) {
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    // Mock login delay
    setTimeout(() => {
      localStorage.setItem('token', 'fake-jwt-token-mvp');
      onLogin();
    }, 800);
  };

  return (
    <div className="min-h-screen bg-zinc-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl shadow-zinc-200/50 p-8 w-full max-w-md border border-zinc-100">
        <div className="flex justify-center mb-6">
            <LabLivreLogo className="w-48 text-zinc-900" />
        </div>
        <h1 className="text-2xl font-semibold text-center text-zinc-900 mb-2">Admin Portal</h1>
        <p className="text-zinc-500 text-center mb-8">Sign in to manage Ponto Digital</p>
        
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-zinc-700 mb-1">Email</label>
            <input 
              type="email" 
              required 
              defaultValue="admin@example.com" 
              className="w-full px-4 py-2.5 rounded-xl border border-zinc-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-zinc-900" 
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-zinc-700 mb-1">Password</label>
            <div className="relative">
              <input 
                type={showPassword ? "text" : "password"} 
                required 
                defaultValue="password" 
                className="w-full pl-4 pr-11 py-2.5 rounded-xl border border-zinc-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-zinc-900" 
              />
              <button 
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-zinc-600 focus:outline-none"
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>
          <button 
            type="submit" 
            disabled={isLoading} 
            className="w-full mt-2 py-2.5 px-4 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-xl transition-all shadow-md shadow-indigo-600/10 disabled:opacity-70 disabled:cursor-not-allowed flex justify-center items-center h-11"
          >
            {isLoading ? <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
}
