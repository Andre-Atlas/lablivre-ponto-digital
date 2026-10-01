import { useState } from 'react';
import { MapPin, CheckCircle, XCircle, LogOut } from 'lucide-react';
import { ThemeToggle } from '../components/ThemeToggle';
import { API_URL } from '../services/api';

export function Checkin({ onLogout, isDark, toggleTheme }: { onLogout: () => void, isDark: boolean, toggleTheme: () => void }) {
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  const handleCheckin = () => {
    setStatus('loading');
    setMessage('Obtendo localização...');

    if (!navigator.geolocation) {
      setStatus('error');
      setMessage('Geolocalização não suportada pelo seu navegador.');
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        try {
          const { latitude, longitude } = position.coords;
          setMessage('Registrando ponto...');
          
          const res = await fetch(`${API_URL}/checkin/`, {
            method: 'POST',
            headers: { 
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ lat: latitude, lng: longitude })
          });

          if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.detail || 'Falha ao registrar ponto. Tente novamente.');
          }
          
          setStatus('success');
          setMessage('Ponto registrado com sucesso!');
          
          setTimeout(() => {
            setStatus('idle');
            setMessage('');
          }, 4000);
        } catch (err: any) {
          setStatus('error');
          setMessage(err.message || 'Erro ao registrar ponto.');
        }
      },
      (_error) => {
        setStatus('error');
        setMessage('Permissão de GPS negada ou indisponível.');
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
  };

  return (
    <div className="min-h-[100dvh] flex flex-col items-center justify-center text-slate-900 dark:text-white relative overflow-hidden bg-[#F0F2F5] dark:bg-[#0A0A0A] font-sans transition-colors duration-500">
      
      <div className="absolute top-6 right-6 sm:top-8 sm:right-8 z-50 flex items-center gap-4">
        <ThemeToggle isDark={isDark} toggle={toggleTheme} />
        <button 
          onClick={onLogout}
          className="p-2.5 rounded-full bg-white/50 dark:bg-white/[0.03] hover:bg-white dark:hover:bg-white/[0.08] text-slate-700 dark:text-white/70 hover:text-red-500 dark:hover:text-red-400 transition-all shadow-sm backdrop-blur-md border border-slate-200 dark:border-white/[0.08]"
          title="Sair"
        >
          <LogOut size={20} />
        </button>
      </div>

      {/* Engineered Atmosphere */}
      <div className="absolute top-[-20%] left-[-10%] w-[60vw] h-[60vw] rounded-full blur-[140px] opacity-30 dark:opacity-20 pointer-events-none mix-blend-multiply dark:mix-blend-screen bg-gradient-to-br from-[#10B981] to-[#047857] transition-opacity duration-500"></div>
      <div className="absolute bottom-[-20%] right-[-10%] w-[50vw] h-[50vw] rounded-full blur-[140px] opacity-20 dark:opacity-15 pointer-events-none mix-blend-multiply dark:mix-blend-screen bg-gradient-to-tr from-[#00B9DE] to-[#3B82F6] transition-opacity duration-500"></div>
      <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.03] dark:opacity-20 mix-blend-overlay pointer-events-none transition-opacity duration-500"></div>

      <div className="relative z-10 w-full max-w-md px-6 flex flex-col items-center">
        
        <div className="text-center mb-16">
          <h1 className="text-4xl sm:text-5xl font-medium tracking-tight mb-4">Ponto Digital</h1>
          <p className="text-slate-500 dark:text-white/50 text-base font-light">
            Confirme sua localização para registrar a presença no Lab Livre.
          </p>
        </div>

        {/* Central Action Button with Glowing Pulse Effects */}
        <div className="relative group mb-12">
          <div className={`absolute inset-0 rounded-full blur-2xl transition-all duration-500 ${
            status === 'success' ? 'bg-emerald-500/60 opacity-100 scale-110' : 
            status === 'error' ? 'bg-red-500/60 opacity-100 scale-110' : 
            'bg-[#00B9DE]/40 opacity-50 group-hover:opacity-100 group-hover:scale-110'
          }`}></div>
          
          <button
            onClick={handleCheckin}
            disabled={status === 'loading'}
            className={`relative flex items-center justify-center w-56 h-56 rounded-full shadow-[0_8px_32px_rgba(0,0,0,0.1)] dark:shadow-[inset_0_1px_0_rgba(255,255,255,0.2),0_8px_32px_rgba(0,0,0,0.5)] border-4 transition-all duration-500 active:scale-95 ${
              status === 'success' ? 'bg-emerald-500 border-emerald-400 text-white' :
              status === 'error' ? 'bg-red-500 border-red-400 text-white' :
              'bg-gradient-to-b from-white to-slate-50 dark:from-white/10 dark:to-white/5 border-white dark:border-white/20 text-[#00B9DE] dark:text-white backdrop-blur-xl group-hover:border-[#00B9DE]/50'
            }`}
          >
            <div className="flex flex-col items-center gap-4">
              {status === 'loading' ? (
                <div className="w-14 h-14 border-4 border-current/30 border-t-current rounded-full animate-spin" />
              ) : status === 'success' ? (
                <CheckCircle size={56} className="animate-[bounce_0.5s_ease-out]" />
              ) : status === 'error' ? (
                <XCircle size={56} className="animate-[pulse_0.5s_ease-out]" />
              ) : (
                <MapPin size={56} className="group-hover:scale-110 transition-transform duration-300 group-hover:-translate-y-1" />
              )}
              <span className="font-medium tracking-widest text-sm uppercase">
                {status === 'loading' ? 'Processando' : 
                 status === 'success' ? 'Registrado' : 
                 status === 'error' ? 'Tentar Novamente' : 
                 'Bater Ponto'}
              </span>
            </div>
          </button>
        </div>

        {/* Status Message Display */}
        <div className={`h-14 flex items-center justify-center text-center px-8 rounded-2xl backdrop-blur-md transition-all duration-500 ${
          status === 'idle' ? 'opacity-0 translate-y-4 scale-95' : 'opacity-100 translate-y-0 scale-100'
        } ${
          status === 'loading' ? 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20' :
          status === 'success' ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20' :
          status === 'error' ? 'bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/20' : ''
        }`}>
          <span className="text-sm font-medium">{message}</span>
        </div>

      </div>
    </div>
  );
}
