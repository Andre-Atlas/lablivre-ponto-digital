import React, { useState } from 'react';
import { Mail, Lock, ChevronRight } from 'lucide-react';
import { LabLivreLogo } from '../components/LabLivreLogo';
import { adminLogin } from '../services/api';
import { ThemeToggle } from '../components/ThemeToggle';

export function Login({ onLogin, isDark, toggleTheme }: { onLogin: () => void, isDark: boolean, toggleTheme: () => void }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsLoading(true);
      setError('');
      
      const data = await adminLogin(email, password);
      localStorage.setItem('token', data.access_token);
      onLogin();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-[100dvh] flex text-slate-900 dark:text-white relative overflow-hidden bg-[#F0F2F5] dark:bg-[#0A0A0A] font-sans transition-colors duration-500">
      
      {/* Absolute Theme Toggle at top right */}
      <div className="absolute top-6 right-6 sm:top-8 sm:right-8 z-50">
        <ThemeToggle isDark={isDark} toggle={toggleTheme} />
      </div>

      {/* Engineered Atmosphere (Impeccable Glassmorphism Background) */}
      <div className="absolute top-[-20%] left-[-10%] w-[60vw] h-[60vw] rounded-full blur-[140px] opacity-30 dark:opacity-20 pointer-events-none mix-blend-multiply dark:mix-blend-screen bg-gradient-to-br from-[#D12A6A] to-[#FF4D4D] transition-opacity duration-500"></div>
      <div className="absolute bottom-[-20%] right-[-10%] w-[50vw] h-[50vw] rounded-full blur-[140px] opacity-20 dark:opacity-15 pointer-events-none mix-blend-multiply dark:mix-blend-screen bg-gradient-to-tr from-[#00B9DE] to-[#9333EA] transition-opacity duration-500"></div>
      <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.03] dark:opacity-20 mix-blend-overlay pointer-events-none transition-opacity duration-500"></div>

      {/* Brand Context (Left) */}
      <div className="hidden lg:flex flex-1 flex-col justify-center px-24 relative z-10 selection:bg-[#D12A6A] selection:text-white">
        <div className="max-w-xl">
          <LabLivreLogo className="w-64 mb-12 drop-shadow-xl" />
          
          <h1 className="text-5xl md:text-6xl tracking-tighter leading-[1.1] mb-8 font-medium">
            O hub central de<br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#D12A6A] to-[#F39200]">
              controle e acesso.
            </span>
          </h1>
          
          <p className="text-lg text-slate-600 dark:text-white/50 font-light leading-relaxed max-w-[45ch] transition-colors duration-500">
            Gerencie credenciais, aprove novos colaboradores e monitore o fluxo de ponto do Lab Livre em tempo real.
          </p>
        </div>
      </div>

      {/* Login Interface (Right) */}
      <div className="flex-1 flex items-center justify-center p-6 sm:p-12 relative z-10">
        <div className="w-full max-w-md">
          
          {/* Glass Card with Physical Refraction (Impeccable Specs) */}
          <div className="backdrop-blur-[40px] bg-white/70 dark:bg-white/[0.02] border border-white dark:border-white/[0.08] shadow-[0_24px_48px_rgba(0,0,0,0.05)] dark:shadow-[inset_0_1px_0_rgba(255,255,255,0.1),0_24px_48px_rgba(0,0,0,0.4)] rounded-[2rem] p-10 relative overflow-hidden transition-all duration-500">
            
            {/* Ambient inner glow */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-3/4 h-[1px] bg-gradient-to-r from-transparent via-[#D12A6A]/30 dark:via-[#D12A6A]/50 to-transparent"></div>
            
            <h2 className="text-2xl font-medium tracking-tight mb-2">Entrar na plataforma</h2>
            <p className="text-slate-500 dark:text-white/40 text-sm font-light mb-8 transition-colors duration-500">Insira suas credenciais corporativas.</p>
            
            {error && (
              <div className="mb-6 p-4 backdrop-blur-md bg-red-500/10 border border-red-500/20 rounded-xl text-red-600 dark:text-red-200 text-sm flex items-start gap-3 shadow-sm transition-colors duration-500">
                <div className="w-1.5 h-1.5 bg-red-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span className="leading-snug">{error}</span>
              </div>
            )}
            
            <form onSubmit={handleLogin} className="space-y-5">
              
              <div className="space-y-2">
                <label className="text-[11px] font-medium text-slate-500 dark:text-white/50 tracking-[0.1em] uppercase ml-1 transition-colors duration-500">Email corporativo</label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Mail size={16} className="text-slate-400 dark:text-white/30 group-focus-within:text-[#D12A6A] dark:group-focus-within:text-[#D12A6A] transition-colors duration-300" />
                  </div>
                  <input 
                    type="email" 
                    required 
                    placeholder="nome@lablivre.com"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    className="w-full bg-white/50 dark:bg-black/20 border border-slate-200 dark:border-white/[0.08] rounded-xl pl-11 pr-4 py-3.5 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-white/20 text-sm outline-none focus:border-[#D12A6A]/50 focus:bg-white dark:focus:bg-black/40 transition-all shadow-[inset_0_2px_4px_rgba(0,0,0,0.02)] dark:shadow-[inset_0_2px_4px_rgba(0,0,0,0.2)]" 
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between ml-1">
                  <label className="text-[11px] font-medium text-slate-500 dark:text-white/50 tracking-[0.1em] uppercase transition-colors duration-500">Senha</label>
                  <a href="#" className="text-[11px] text-[#D12A6A] hover:text-[#F39200] transition-colors">Esqueceu?</a>
                </div>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Lock size={16} className="text-slate-400 dark:text-white/30 group-focus-within:text-[#D12A6A] dark:group-focus-within:text-[#D12A6A] transition-colors duration-300" />
                  </div>
                  <input 
                    type="password" 
                    required 
                    placeholder="••••••••"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    className="w-full bg-white/50 dark:bg-black/20 border border-slate-200 dark:border-white/[0.08] rounded-xl pl-11 pr-4 py-3.5 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-white/20 text-sm outline-none focus:border-[#D12A6A]/50 focus:bg-white dark:focus:bg-black/40 transition-all shadow-[inset_0_2px_4px_rgba(0,0,0,0.02)] dark:shadow-[inset_0_2px_4px_rgba(0,0,0,0.2)]" 
                  />
                </div>
              </div>
              
              <div className="pt-2 pb-2">
                <label className="flex items-center gap-3 cursor-pointer group w-max">
                  <div className="relative flex items-center justify-center w-4 h-4 border border-slate-300 dark:border-white/20 rounded-[4px] bg-white dark:bg-black/20 group-hover:border-[#D12A6A]/50 transition-colors">
                    <input type="checkbox" className="peer sr-only" defaultChecked />
                    <div className="w-2 h-2 bg-[#D12A6A] rounded-[2px] opacity-0 peer-checked:opacity-100 transition-opacity"></div>
                  </div>
                  <span className="text-sm text-slate-600 dark:text-white/50 group-hover:text-slate-900 dark:group-hover:text-white/80 transition-colors">Lembrar-me por 30 dias</span>
                </label>
              </div>
              
              <button 
                type="submit" 
                disabled={isLoading} 
                className="w-full group relative flex items-center justify-center gap-2 py-3.5 px-4 bg-gradient-to-r from-[#D12A6A] to-[#B01E55] hover:from-[#D12A6A] hover:to-[#F39200] text-white font-medium rounded-xl transition-all active:scale-[0.98] active:translate-y-[1px] disabled:opacity-50 disabled:pointer-events-none shadow-[0_4px_14px_rgba(209,42,106,0.3)] hover:shadow-[0_6px_20px_rgba(209,42,106,0.4)] border border-[#D12A6A]/50"
              >
                {isLoading ? (
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>
                    <span className="tracking-wide text-sm">Acessar Painel</span>
                    <ChevronRight size={16} className="group-hover:translate-x-0.5 transition-transform" />
                  </>
                )}
              </button>
            </form>
          </div>
          
          <div className="mt-8 text-center text-xs text-slate-500 dark:text-white/30 flex items-center justify-center gap-4 transition-colors duration-500">
            <a href="#" className="hover:text-slate-800 dark:hover:text-white/60 transition-colors">Termos</a>
            <span className="w-1 h-1 bg-slate-300 dark:bg-white/10 rounded-full transition-colors duration-500"></span>
            <a href="#" className="hover:text-slate-800 dark:hover:text-white/60 transition-colors">Privacidade</a>
            <span className="w-1 h-1 bg-slate-300 dark:bg-white/10 rounded-full transition-colors duration-500"></span>
            <span>&copy; {new Date().getFullYear()} Lab Livre</span>
          </div>
          
        </div>
      </div>
    </div>
  );
}
