import React, { useState } from 'react';
import { ChevronRight, Eye, EyeOff } from 'lucide-react';
import { QRCodeSVG } from 'qrcode.react';
import { LabLivreLogo } from '../components/LabLivreLogo';
import { API_URL } from '../services/api';
import { Button, Input, Alert, Blob } from '../components/ui';

export function Login({ onLogin }: { onLogin: (tipo: string) => void }) {
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsLoading(true);
      setError('');
      const res = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, senha }),
      });
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Não foi possível entrar. Verifique suas credenciais.');
      }
      const data = await res.json();
      localStorage.setItem('token', data.access_token);
      onLogin(data.tipo || 'STAFF');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-[100dvh] flex-col overflow-x-hidden bg-bg lg:flex-row">
      {/* ── Brand / hero panel ── */}
      <div className="relative flex w-full flex-col justify-center overflow-hidden px-6 pb-8 pt-16 sm:px-12 lg:w-1/2 lg:px-24 lg:py-0">
        <Blob variant="navy" className="pointer-events-none absolute -bottom-56 -right-44 hidden h-[26rem] w-[26rem] opacity-90 lg:block" />
        <Blob variant="purple-ring" ring className="pointer-events-none absolute -left-24 top-6 hidden h-72 w-72 opacity-25 lg:block" />
        <div className="relative z-10 mx-auto w-full max-w-xl text-center lg:mx-0 lg:text-left">
          <LabLivreLogo className="mx-auto mb-10 w-52 lg:mx-0 lg:w-60" />
          <p className="eyebrow mb-3">Ponto Digital</p>
          <h1 className="display">
            O hub central de<br className="hidden lg:block" /> controle e acesso.
          </h1>
          <p className="mx-auto mt-6 max-w-[46ch] text-base leading-relaxed text-text lg:mx-0">
            Lance a frequência, avalie os LOs e acompanhe a evolução das turmas do Lab Livre.
          </p>

          <div className="mt-10 hidden items-center gap-5 lg:flex">
            <div className="rounded-card border border-border/60 bg-surface p-3 text-ink shadow-card">
              <QRCodeSVG
                value={typeof window !== 'undefined' ? window.location.href : 'https://ponto-digital.lablivre.dev'}
                size={84}
                bgColor="transparent"
                fgColor="currentColor"
                title="QR Code de acesso à plataforma"
              />
            </div>
            <div className="text-left text-sm">
              <p className="font-semibold text-ink">Acesse pelo celular</p>
              <p className="text-muted">Escaneie o QR Code para abrir a plataforma no celular.</p>
            </div>
          </div>
        </div>
      </div>

      {/* ── Auth panel ── */}
      <div className="relative z-10 flex w-full items-center justify-center p-6 pb-16 sm:p-12 lg:w-1/2 lg:py-0">
        <div className="w-full max-w-md rounded-card border border-border/60 bg-surface p-8 shadow-pop sm:p-10">
          <h2 className="mb-1 text-2xl font-bold tracking-tight text-ink">Entrar na plataforma</h2>
          <p className="mb-6 text-sm text-muted">Acesso restrito a mentores. Use seu e-mail e senha para continuar.</p>

          {error && <Alert tone="danger" className="mb-5">{error}</Alert>}

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input label="E-mail" type="email" required placeholder="nome@lablivre.com" value={email} onChange={(e) => setEmail(e.target.value)} />

            <div className="relative">
              <Input
                label="Senha"
                type={showPassword ? 'text' : 'password'}
                required
                placeholder="••••••••"
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
                className="pr-11"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
                className="absolute bottom-2.5 right-3 text-muted hover:text-ink"
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>

            <Button type="submit" fullWidth loading={isLoading} iconRight={!isLoading ? <ChevronRight size={16} /> : undefined} className="mt-2">
              Entrar
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
