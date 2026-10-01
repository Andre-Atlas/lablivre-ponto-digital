import React, { useState } from 'react';
import { Mail, Lock, ChevronRight, Eye, EyeOff, User, Users, Monitor } from 'lucide-react';
import { LabLivreLogo } from '../components/LabLivreLogo';
import { API_URL } from '../services/api';
import { ThemeToggle } from '../components/ThemeToggle';

export function Login({ onLogin, isDark, toggleTheme }: { onLogin: (tipo: string) => void, isDark: boolean, toggleTheme: () => void }) {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [turma, setTurma] = useState('');
  const [numeroMaquina, setNumeroMaquina] = useState('');
  
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsLoading(true);
      setError('');
      setSuccess('');
      
      if (mode === 'login') {
        const res = await fetch(`${API_URL}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, senha })
        });
        
        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.detail || 'Falha no login. Verifique suas credenciais.');
        }
        
        const data = await res.json();
        localStorage.setItem('token', data.access_token);
        onLogin(data.tipo || 'ALUNO');
      } else {
        const res = await fetch(`${API_URL}/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            nome, 
            email, 
            senha, 
            turma, 
            numero_maquina: parseInt(numeroMaquina, 10) || 0 
          })
        });
        
        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.detail || 'Falha no cadastro. Verifique os dados.');
        }
        
        setSuccess('Cadastro realizado com sucesso! Faça login.');
        setMode('login');
        setSenha('');
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-[100dvh] flex flex-col lg:flex-row text-slate-900 dark:text-white relative overflow-x-hidden overflow-y-auto lg:overflow-hidden bg-[#F0F2F5] dark:bg-[#0A0A0A] font-sans transition-colors duration-500">
      
      <div className="absolute top-6 right-6 sm:top-8 sm:right-8 z-50">
        <ThemeToggle isDark={isDark} toggle={toggleTheme} />
      </div>

      <div className="absolute top-[-20%] left-[-10%] w-[60vw] h-[60vw] rounded-full blur-[140px] opacity-30 dark:opacity-20 pointer-events-none mix-blend-multiply dark:mix-blend-screen bg-gradient-to-br from-[#D12A6A] to-[#FF4D4D] transition-opacity duration-500"></div>
      <div className="absolute bottom-[-20%] right-[-10%] w-[50vw] h-[50vw] rounded-full blur-[140px] opacity-20 dark:opacity-15 pointer-events-none mix-blend-multiply dark:mix-blend-screen bg-gradient-to-tr from-[#00B9DE] to-[#9333EA] transition-opacity duration-500"></div>
      <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.03] dark:opacity-20 mix-blend-overlay pointer-events-none transition-opacity duration-500"></div>

      <div className="w-full lg:flex-1 flex flex-col justify-center px-6 sm:px-12 lg:px-24 pt-16 lg:pt-0 pb-8 lg:pb-0 relative z-10 selection:bg-[#D12A6A] selection:text-white">
        <div className="max-w-xl mx-auto lg:mx-0 w-full text-center lg:text-left">
          <LabLivreLogo className="w-48 sm:w-56 lg:w-64 mb-8 lg:mb-12 mx-auto lg:mx-0 drop-shadow-xl" />
          
          <h1 className="text-4xl sm:text-5xl md:text-6xl tracking-tighter leading-[1.1] mb-6 lg:mb-8 font-medium">
            O hub central de<br className="hidden lg:block"/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#D12A6A] to-[#F39200]">
              controle e acesso.
            </span>
          </h1>
          
          <p className="text-base sm:text-lg text-slate-600 dark:text-white/50 font-light leading-relaxed max-w-[45ch] mx-auto lg:mx-0 transition-colors duration-500 mb-8 lg:mb-12">
            Gerencie credenciais, realize seu check-in e monitore o fluxo de ponto do Lab Livre em tempo real.
          </p>
        </div>
      </div>

      <div className="w-full lg:flex-1 flex items-center justify-center p-6 sm:p-12 pb-16 lg:py-0 relative z-10">
        <div className="w-full max-w-md">
          
          <div className="backdrop-blur-[40px] bg-white/70 dark:bg-white/[0.02] border border-white dark:border-white/[0.08] shadow-[0_24px_48px_rgba(0,0,0,0.05)] dark:shadow-[inset_0_1px_0_rgba(255,255,255,0.1),0_24px_48px_rgba(0,0,0,0.4)] rounded-[2rem] p-8 sm:p-10 relative overflow-hidden transition-all duration-500">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-3/4 h-[1px] bg-gradient-to-r from-transparent via-[#D12A6A]/30 dark:via-[#D12A6A]/50 to-transparent"></div>
            
            {/* Tabs for Login / Register */}
            <div className="flex bg-slate-200/50 dark:bg-black/30 p-1 rounded-xl mb-8">
              <button
                type="button"
                onClick={() => { setMode('login'); setError(''); setSuccess(''); }}
                className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all ${mode === 'login' ? 'bg-white dark:bg-white/10 text-slate-900 dark:text-white shadow-sm' : 'text-slate-500 dark:text-white/40 hover:text-slate-700 dark:hover:text-white/60'}`}
              >
                Login
              </button>
              <button
                type="button"
                onClick={() => { setMode('register'); setError(''); setSuccess(''); }}
                className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all ${mode === 'register' ? 'bg-white dark:bg-white/10 text-slate-900 dark:text-white shadow-sm' : 'text-slate-500 dark:text-white/40 hover:text-slate-700 dark:hover:text-white/60'}`}
              >
                Cadastrar
              </button>
            </div>

            <h2 className="text-2xl font-medium tracking-tight mb-2">
              {mode === 'login' ? 'Entrar na plataforma' : 'Criar uma conta'}
            </h2>
            <p className="text-slate-500 dark:text-white/40 text-sm font-light mb-6 transition-colors duration-500">
              {mode === 'login' ? 'Insira suas credenciais corporativas.' : 'Preencha seus dados para acesso.'}
            </p>
            
            {error && (
              <div className="mb-6 p-4 backdrop-blur-md bg-red-500/10 border border-red-500/20 rounded-xl text-red-600 dark:text-red-200 text-sm flex items-start gap-3 shadow-sm transition-colors duration-500">
                <div className="w-1.5 h-1.5 bg-red-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span className="leading-snug">{error}</span>
              </div>
            )}

            {success && (
              <div className="mb-6 p-4 backdrop-blur-md bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-600 dark:text-emerald-200 text-sm flex items-start gap-3 shadow-sm transition-colors duration-500">
                <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span className="leading-snug">{success}</span>
              </div>
            )}
            
            <form onSubmit={handleSubmit} className="space-y-4">
              
              {mode === 'register' && (
                <div className="space-y-2">
                  <label className="text-[11px] font-medium text-slate-500 dark:text-white/50 tracking-[0.1em] uppercase ml-1">Nome Completo</label>
                  <div className="relative group">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <User size={16} className="text-slate-400 dark:text-white/30 group-focus-within:text-[#D12A6A]" />
                    </div>
                    <input 
                      type="text" 
                      required 
                      placeholder="Seu nome"
                      value={nome}
                      onChange={e => setNome(e.target.value)}
                      className="w-full bg-white/50 dark:bg-black/20 border border-slate-200 dark:border-white/[0.08] rounded-xl pl-11 pr-4 py-3 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-white/20 text-sm outline-none focus:border-[#D12A6A]/50 focus:bg-white dark:focus:bg-black/40 transition-all" 
                    />
                  </div>
                </div>
              )}

              <div className="space-y-2">
                <label className="text-[11px] font-medium text-slate-500 dark:text-white/50 tracking-[0.1em] uppercase ml-1">Email</label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Mail size={16} className="text-slate-400 dark:text-white/30 group-focus-within:text-[#D12A6A]" />
                  </div>
                  <input 
                    type="email" 
                    required 
                    placeholder="nome@lablivre.com"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    className="w-full bg-white/50 dark:bg-black/20 border border-slate-200 dark:border-white/[0.08] rounded-xl pl-11 pr-4 py-3 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-white/20 text-sm outline-none focus:border-[#D12A6A]/50 focus:bg-white dark:focus:bg-black/40 transition-all" 
                  />
                </div>
              </div>

              {mode === 'register' && (
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-[11px] font-medium text-slate-500 dark:text-white/50 tracking-[0.1em] uppercase ml-1">Turma</label>
                    <div className="relative group">
                      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <Users size={16} className="text-slate-400 dark:text-white/30 group-focus-within:text-[#D12A6A]" />
                      </div>
                      <select
                        required
                        value={turma}
                        onChange={e => setTurma(e.target.value)}
                        className="w-full bg-white/50 dark:bg-black/20 border border-slate-200 dark:border-white/[0.08] rounded-xl pl-11 pr-4 py-3 text-slate-900 dark:text-white text-sm outline-none focus:border-[#D12A6A]/50 focus:bg-white dark:focus:bg-black/40 transition-all appearance-none"
                      >
                        <option value="" disabled className="dark:bg-slate-900">Selecione</option>
                        <option value="Turma 1" className="dark:bg-slate-900">Turma 1</option>
                        <option value="Turma 2" className="dark:bg-slate-900">Turma 2</option>
                      </select>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-[11px] font-medium text-slate-500 dark:text-white/50 tracking-[0.1em] uppercase ml-1">Máquina</label>
                    <div className="relative group">
                      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <Monitor size={16} className="text-slate-400 dark:text-white/30 group-focus-within:text-[#D12A6A]" />
                      </div>
                      <input 
                        type="number" 
                        required 
                        placeholder="Nº"
                        value={numeroMaquina}
                        onChange={e => setNumeroMaquina(e.target.value)}
                        className="w-full bg-white/50 dark:bg-black/20 border border-slate-200 dark:border-white/[0.08] rounded-xl pl-11 pr-4 py-3 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-white/20 text-sm outline-none focus:border-[#D12A6A]/50 focus:bg-white dark:focus:bg-black/40 transition-all" 
                      />
                    </div>
                  </div>
                </div>
              )}
              
              <div className="space-y-2">
                <div className="flex items-center justify-between ml-1">
                  <label className="text-[11px] font-medium text-slate-500 dark:text-white/50 tracking-[0.1em] uppercase">Senha</label>
                  {mode === 'login' && <a href="#" className="text-[11px] text-[#D12A6A] hover:text-[#F39200] transition-colors">Esqueceu?</a>}
                </div>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Lock size={16} className="text-slate-400 dark:text-white/30 group-focus-within:text-[#D12A6A]" />
                  </div>
                  <input 
                    type={showPassword ? "text" : "password"}
                    required 
                    placeholder="••••••••"
                    value={senha}
                    onChange={e => setSenha(e.target.value)}
                    className="w-full bg-white/50 dark:bg-black/20 border border-slate-200 dark:border-white/[0.08] rounded-xl pl-11 pr-12 py-3 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-white/20 text-sm outline-none focus:border-[#D12A6A]/50 focus:bg-white dark:focus:bg-black/40 transition-all" 
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-4 flex items-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>
              
              <button 
                type="submit" 
                disabled={isLoading} 
                className="w-full mt-4 group relative flex items-center justify-center gap-2 py-3.5 px-4 bg-gradient-to-r from-[#D12A6A] to-[#B01E55] hover:from-[#D12A6A] hover:to-[#F39200] text-white font-medium rounded-xl transition-all active:scale-[0.98] active:translate-y-[1px] disabled:opacity-50 shadow-[0_4px_14px_rgba(209,42,106,0.3)] hover:shadow-[0_6px_20px_rgba(209,42,106,0.4)] border border-[#D12A6A]/50"
              >
                {isLoading ? (
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>
                    <span className="tracking-wide text-sm">{mode === 'login' ? 'Acessar' : 'Cadastrar'}</span>
                    <ChevronRight size={16} className="group-hover:translate-x-0.5 transition-transform" />
                  </>
                )}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
