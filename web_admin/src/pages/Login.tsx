import React, { useState } from 'react';
import { ChevronRight, Eye, EyeOff } from 'lucide-react';
import { QRCodeSVG } from 'qrcode.react';
import { LabLivreLogo } from '../components/LabLivreLogo';
import { API_URL } from '../services/api';
import { Button, Input, Select, Alert, Blob } from '../components/ui';

export function Login({ onLogin }: { onLogin: (tipo: string) => void }) {
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
          body: JSON.stringify({ email, senha }),
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
            numero_maquina: parseInt(numeroMaquina, 10) || 0,
          }),
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
            Gerencie credenciais, realize seu check-in e monitore o fluxo de ponto do Lab Livre em tempo real.
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
          <div className="mb-8 flex rounded-lg bg-bg p-1">
            {(['login', 'register'] as const).map((m) => (
              <button
                key={m}
                type="button"
                onClick={() => { setMode(m); setError(''); setSuccess(''); }}
                aria-pressed={mode === m}
                className={`flex-1 rounded-md py-2 text-sm font-semibold transition-colors ${
                  mode === m ? 'bg-surface text-primary shadow-sm' : 'text-muted hover:text-ink'
                }`}
              >
                {m === 'login' ? 'Entrar' : 'Criar conta'}
              </button>
            ))}
          </div>

          <h2 className="mb-1 text-2xl font-bold tracking-tight text-ink">
            {mode === 'login' ? 'Entrar na plataforma' : 'Criar conta'}
          </h2>
          <p className="mb-6 text-sm text-muted">
            {mode === 'login' ? 'Use seu e-mail e senha para continuar.' : 'Preencha seus dados para começar.'}
          </p>

          {error && <Alert tone="danger" className="mb-5">{error}</Alert>}
          {success && <Alert tone="success" className="mb-5">{success}</Alert>}

          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === 'register' && (
              <Input label="Nome completo" required placeholder="Seu nome" value={nome} onChange={(e) => setNome(e.target.value)} />
            )}

            <Input label="E-mail" type="email" required placeholder="nome@lablivre.com" value={email} onChange={(e) => setEmail(e.target.value)} />

            {mode === 'register' && (
              <div className="grid grid-cols-2 gap-4">
                <Select label="Turma" required value={turma} onChange={(e) => setTurma(e.target.value)}>
                  <option value="" disabled>Selecione</option>
                  <option value="Turma 1">Turma 1</option>
                  <option value="Turma 2">Turma 2</option>
                </Select>
                <Input label="Máquina" type="number" required placeholder="Ex: 12" value={numeroMaquina} onChange={(e) => setNumeroMaquina(e.target.value)} />
              </div>
            )}

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
              {mode === 'login' ? 'Entrar' : 'Criar conta'}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
