import re

with open('web_admin/src/pages/Checkin.tsx', 'r') as f:
    content = f.read()

# Add Settings icon
content = content.replace(
    "import { MapPin, CheckCircle, XCircle, LogOut } from 'lucide-react';",
    "import { MapPin, CheckCircle, XCircle, LogOut, Settings, User, Lock } from 'lucide-react';"
)

# Add states for profile modal
states = """
  const [showProfile, setShowProfile] = useState(false);
  const [profileTab, setProfileTab] = useState<'nome' | 'senha'>('nome');
  const [newName, setNewName] = useState('');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [profileStatus, setProfileStatus] = useState('');
"""
content = content.replace(
    "const [message, setMessage] = useState('');",
    "const [message, setMessage] = useState('');\n" + states
)

profile_handlers = """
  const handleUpdateName = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileStatus('Atualizando...');
    try {
      const res = await fetch(`${API_URL}/api/v1/auth/me`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },
        body: JSON.stringify({ nome: newName })
      });
      if (!res.ok) throw new Error();
      setProfileStatus('Nome atualizado!');
      setTimeout(() => setProfileStatus(''), 2000);
    } catch {
      setProfileStatus('Erro ao atualizar nome.');
    }
  };

  const handleUpdatePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileStatus('Atualizando...');
    try {
      const res = await fetch(`${API_URL}/api/v1/auth/me/senha`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },
        body: JSON.stringify({ senha_atual: currentPassword, nova_senha: newPassword })
      });
      if (!res.ok) throw new Error();
      setProfileStatus('Senha atualizada!');
      setCurrentPassword('');
      setNewPassword('');
      setTimeout(() => setProfileStatus(''), 2000);
    } catch {
      setProfileStatus('Erro ao atualizar senha (senha atual incorreta?).');
    }
  };
"""
content = content.replace("const handleCheckin = () => {", profile_handlers + "\n  const handleCheckin = () => {")

# Add Settings button to UI
settings_btn = """
        <button
          onClick={() => setShowProfile(true)}
          className="p-2.5 rounded-xl bg-white dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.08] text-slate-400 hover:text-slate-600 dark:hover:text-white/80 transition-all hover:scale-105 active:scale-95 shadow-sm flex items-center justify-center"
          title="Meu Perfil"
        >
          <Settings size={20} strokeWidth={2} />
        </button>
"""
content = content.replace("<ThemeToggle", settings_btn + "        <ThemeToggle")

# Add Profile Modal
profile_modal = """
      {showProfile && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-slate-900/40 dark:bg-black/60 backdrop-blur-sm" onClick={() => setShowProfile(false)}></div>
          <div className="relative w-full max-w-sm bg-white dark:bg-[#0A0A0A] rounded-[2rem] p-8 z-10 border border-slate-200 dark:border-white/[0.08]">
            <h3 className="text-xl font-medium mb-4 dark:text-white flex justify-between items-center">
              Meu Perfil
              <button onClick={() => setShowProfile(false)} className="text-slate-400 hover:text-slate-600 dark:hover:text-white/80"><XCircle size={20} /></button>
            </h3>
            
            <div className="flex gap-2 mb-6 border-b border-slate-100 dark:border-white/10 pb-2">
              <button onClick={() => setProfileTab('nome')} className={`flex items-center gap-1.5 pb-2 px-2 text-sm font-medium transition-colors ${profileTab === 'nome' ? 'text-[#00B9DE] border-b-2 border-[#00B9DE]' : 'text-slate-400'}`}><User size={16} /> Nome</button>
              <button onClick={() => setProfileTab('senha')} className={`flex items-center gap-1.5 pb-2 px-2 text-sm font-medium transition-colors ${profileTab === 'senha' ? 'text-[#00B9DE] border-b-2 border-[#00B9DE]' : 'text-slate-400'}`}><Lock size={16} /> Senha</button>
            </div>

            {profileTab === 'nome' ? (
              <form onSubmit={handleUpdateName} className="space-y-4">
                <div>
                  <label className="block text-xs uppercase tracking-widest text-slate-500 dark:text-white/40 mb-1.5">Novo Nome</label>
                  <input required value={newName} onChange={e => setNewName(e.target.value)} className="w-full bg-slate-50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.08] rounded-xl px-4 py-2 dark:text-white" />
                </div>
                <button type="submit" className="w-full py-2 bg-[#00B9DE] hover:bg-[#009bb8] text-white font-medium rounded-xl text-sm transition-colors">Atualizar Nome</button>
              </form>
            ) : (
              <form onSubmit={handleUpdatePassword} className="space-y-4">
                <div>
                  <label className="block text-xs uppercase tracking-widest text-slate-500 dark:text-white/40 mb-1.5">Senha Atual</label>
                  <input type="password" required value={currentPassword} onChange={e => setCurrentPassword(e.target.value)} className="w-full bg-slate-50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.08] rounded-xl px-4 py-2 dark:text-white" />
                </div>
                <div>
                  <label className="block text-xs uppercase tracking-widest text-slate-500 dark:text-white/40 mb-1.5">Nova Senha</label>
                  <input type="password" required value={newPassword} onChange={e => setNewPassword(e.target.value)} className="w-full bg-slate-50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.08] rounded-xl px-4 py-2 dark:text-white" />
                </div>
                <button type="submit" className="w-full py-2 bg-[#00B9DE] hover:bg-[#009bb8] text-white font-medium rounded-xl text-sm transition-colors">Atualizar Senha</button>
              </form>
            )}
            
            {profileStatus && <p className="mt-4 text-center text-sm font-medium text-emerald-500">{profileStatus}</p>}
          </div>
        </div>
      )}
"""
content = re.sub(r'(</div>\n\s*</div>\n\s*);\n\s*}[^}]*)$', profile_modal + r'\1', content)

with open('web_admin/src/pages/Checkin.tsx', 'w') as f:
    f.write(content)
