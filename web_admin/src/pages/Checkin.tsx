import { useState } from 'react';
import { MapPin, CheckCircle, XCircle, LogOut, Settings, User, Lock } from 'lucide-react';
import { API_URL } from '../services/api';
import { LabLivreLogo } from '../components/LabLivreLogo';
import { Button, Input, Modal, Tabs, Alert, Blob } from '../components/ui';

export function Checkin({ onLogout }: { onLogout: () => void }) {
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  const [showProfile, setShowProfile] = useState(false);
  const [newName, setNewName] = useState('');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [profileStatus, setProfileStatus] = useState('');

  const handleUpdateName = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileStatus('Atualizando...');
    try {
      const res = await fetch(`${API_URL}/api/v1/auth/me`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
        body: JSON.stringify({ nome: newName }),
      });
      if (!res.ok) throw new Error();
      setProfileStatus('Nome atualizado!');
      setTimeout(() => setProfileStatus(''), 2000);
    } catch {
      setProfileStatus('Não foi possível atualizar o nome.');
    }
  };

  const handleUpdatePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileStatus('Atualizando...');
    try {
      const res = await fetch(`${API_URL}/api/v1/auth/me/senha`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
        body: JSON.stringify({ senha_atual: currentPassword, nova_senha: newPassword }),
      });
      if (!res.ok) throw new Error();
      setProfileStatus('Senha atualizada!');
      setCurrentPassword('');
      setNewPassword('');
      setTimeout(() => setProfileStatus(''), 2000);
    } catch {
      setProfileStatus('Não foi possível atualizar a senha. Verifique a senha atual.');
    }
  };

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
            headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
            body: JSON.stringify({ lat: latitude, lng: longitude }),
          });

          if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.detail || 'Não foi possível registrar ponto. Tente novamente.');
          }

          setStatus('success');
          setMessage('Presença registrada! Bom trabalho. 👋');
          setTimeout(() => { setStatus('idle'); setMessage(''); }, 4000);
        } catch (err: any) {
          setStatus('error');
          setMessage(err.message || 'Erro ao registrar ponto.');
        }
      },
      () => {
        setStatus('error');
        setMessage('Permissão de GPS negada ou indisponível.');
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 },
    );
  };

  const btnTone =
    status === 'success' ? 'bg-success border-success text-white'
    : status === 'error' ? 'bg-danger border-danger text-white'
    : 'bg-surface border-primary/30 text-primary hover:border-primary';

  return (
    <div className="relative flex min-h-[100dvh] flex-col overflow-hidden bg-bg">
      <header className="relative z-20 flex items-center justify-between px-6 py-4 sm:px-10">
        <LabLivreLogo className="w-20" />
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setShowProfile(true)}
            title="Meu Perfil"
            aria-label="Meu Perfil"
            className="rounded-lg border border-border/60 bg-surface p-2.5 text-muted shadow-sm transition-colors hover:text-primary"
          >
            <Settings size={20} />
          </button>
          <button
            type="button"
            onClick={onLogout}
            title="Sair"
            aria-label="Sair"
            className="rounded-lg border border-border/60 bg-surface p-2.5 text-muted shadow-sm transition-colors hover:text-danger"
          >
            <LogOut size={20} />
          </button>
        </div>
      </header>

      <Blob variant="purple-ring" ring className="pointer-events-none absolute -left-24 top-10 h-80 w-80 opacity-30" />
      <Blob variant="green" className="pointer-events-none absolute -right-24 bottom-0 h-96 w-96 opacity-20" />

      <main className="relative z-10 flex flex-1 flex-col items-center justify-center px-6 py-10">
        <div className="mb-14 text-center">
          <p className="eyebrow mb-3">Lab Livre · Presença</p>
          <h1 className="display">Ponto Digital</h1>
          <p className="mx-auto mt-4 max-w-md text-text">
            Confirme sua localização para registrar a presença no Lab Livre.
          </p>
        </div>

        <button
          onClick={handleCheckin}
          disabled={status === 'loading'}
          className={`flex h-56 w-56 items-center justify-center rounded-full border-4 shadow-pop transition-all duration-300 active:scale-95 disabled:opacity-80 ${btnTone}`}
        >
          <div className="flex flex-col items-center gap-4">
            {status === 'loading' ? (
              <span className="h-14 w-14 animate-spin rounded-full border-4 border-current border-t-transparent" />
            ) : status === 'success' ? (
              <CheckCircle size={56} />
            ) : status === 'error' ? (
              <XCircle size={56} />
            ) : (
              <MapPin size={56} />
            )}
            <span className="text-sm font-bold uppercase tracking-widest">
              {status === 'loading' ? 'Registrando...' : status === 'success' ? 'Presença confirmada' : status === 'error' ? 'Tentar novamente' : 'Bater ponto'}
            </span>
          </div>
        </button>

        <div className="mt-12 h-12">
          {status !== 'idle' && message && (
            <Alert tone={status === 'success' ? 'success' : status === 'error' ? 'danger' : 'info'}>{message}</Alert>
          )}
        </div>
      </main>

      <Modal open={showProfile} onClose={() => setShowProfile(false)} title="Meu perfil" size="sm">
        <Tabs
          tabs={[
            {
              id: 'nome',
              label: <span className="inline-flex items-center gap-1.5"><User size={16} /> Nome</span>,
              content: (
                <form onSubmit={handleUpdateName} className="space-y-4">
                  <Input label="Novo nome" required value={newName} onChange={(e) => setNewName(e.target.value)} />
                  <Button type="submit" fullWidth>Atualizar nome</Button>
                </form>
              ),
            },
            {
              id: 'senha',
              label: <span className="inline-flex items-center gap-1.5"><Lock size={16} /> Senha</span>,
              content: (
                <form onSubmit={handleUpdatePassword} className="space-y-4">
                  <Input label="Senha atual" type="password" required value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} />
                  <Input label="Nova senha" type="password" required value={newPassword} onChange={(e) => setNewPassword(e.target.value)} />
                  <Button type="submit" fullWidth>Atualizar senha</Button>
                </form>
              ),
            },
          ]}
        />
        {profileStatus && <p className="mt-4 text-center text-sm font-semibold text-success-dark">{profileStatus}</p>}
      </Modal>
    </div>
  );
}
