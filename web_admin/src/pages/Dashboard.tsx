import React, { useEffect, useState } from 'react';
import { Users, CheckCircle, Search, LogOut, Activity, Trash2, Plus, Download } from 'lucide-react';
import type { User } from '../services/api';
import { API_URL, fetchUsers, approveUser, deleteUser, createAdmin } from '../services/api';
import { LabLivreLogo } from '../components/LabLivreLogo';
import { ThemeToggle } from '../components/ThemeToggle';

export function Dashboard({ onLogout, isDark, toggleTheme }: { onLogout: () => void, isDark: boolean, toggleTheme: () => void }) {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showPopup, setShowPopup] = useState<{ visible: boolean; userId: string | number | null; userName: string }>({ visible: false, userId: null, userName: '' });
  const [showAddAdmin, setShowAddAdmin] = useState(false);
  const [newAdmin, setNewAdmin] = useState({ nome: '', email: '', senha: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const loadUsers = async () => {
    try {
      const data = await fetchUsers();
      setUsers(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const confirmApprove = async () => {
    if (!showPopup.userId) return;
    try {
      await approveUser(showPopup.userId);
      setUsers(users.map(u => u.id === showPopup.userId ? { ...u, admin_aprovado: true } : u));
    } catch (err) {
      console.error(err);
    } finally {
      setShowPopup({ visible: false, userId: null, userName: '' });
    }
  };

  const handleDelete = async (id: string | number) => {
    if (!confirm('Tem certeza que deseja excluir este usuário?')) return;
    try {
      await deleteUser(id);
      setUsers(users.filter(u => u.id !== id));
    } catch (err: any) {
      alert(err.message || 'Erro ao excluir usuário');
    }
  };

  const handleAddAdmin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await createAdmin(newAdmin.nome, newAdmin.email);
      await loadUsers();
      setShowAddAdmin(false);
      setNewAdmin({ nome: '', email: '', senha: '' });
    } catch (err: any) {
      alert(err.message || 'Erro ao criar administrador');
    } finally {
      setIsSubmitting(false);
    }
  };

  const filteredUsers = users.filter(u => 
    u.nome.toLowerCase().includes(search.toLowerCase()) || 
    u.email.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-[#F0F2F5] dark:bg-[#0A0A0A] text-slate-900 dark:text-white font-sans overflow-x-hidden selection:bg-[#D12A6A] selection:text-white transition-colors duration-500">
      
      {/* Background Gradients */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        <div className="absolute top-[-20%] left-[-10%] w-[60%] h-[60%] rounded-full bg-gradient-to-br from-[#D12A6A]/10 to-transparent blur-[120px] mix-blend-multiply dark:mix-blend-screen transition-opacity duration-500"></div>
        <div className="absolute bottom-[-20%] right-[-10%] w-[60%] h-[60%] rounded-full bg-gradient-to-tl from-[#00B9DE]/10 to-transparent blur-[120px] mix-blend-multiply dark:mix-blend-screen transition-opacity duration-500"></div>
      </div>
      <div className="fixed inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0IiBoZWlnaHQ9IjQiPgo8cmVjdCB3aWR0aD0iNCIgaGVpZ2h0PSI0IiBmaWxsPSIjZmZmIiBmaWxsLW9wYWNpdHk9IjAuMDIiLz4KPC9zdmc+')] opacity-0 dark:opacity-30 z-0 pointer-events-none transition-opacity duration-500"></div>

      {/* Header */}
      <header className="sticky top-0 z-30 backdrop-blur-[20px] bg-white/40 dark:bg-[#0A0A0A]/40 border-b border-slate-200 dark:border-white/[0.05] transition-colors duration-500">
        <div className="max-w-6xl mx-auto px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-5">
            <LabLivreLogo className="w-28 drop-shadow-sm dark:drop-shadow-md" />
            <div className="h-4 w-px bg-slate-300 dark:bg-white/10 hidden sm:block transition-colors"></div>
            <div className="hidden sm:flex items-center gap-2">
              <Activity size={14} className="text-[#00B9DE]" />
              <span className="text-slate-500 dark:text-white/40 text-[10px] uppercase tracking-widest font-medium transition-colors">System Online</span>
            </div>
          </div>
          <div className="flex items-center gap-6">
            <ThemeToggle isDark={isDark} toggle={toggleTheme} />
            <button 
              onClick={onLogout}
              className="group flex items-center gap-2 text-slate-500 hover:text-slate-900 dark:text-white/50 dark:hover:text-white transition-colors"
            >
              <span className="text-xs font-medium tracking-wide">Sair</span>
              <LogOut size={16} className="group-hover:translate-x-0.5 transition-transform" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 lg:px-8 py-12 relative z-10">
        
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.05] mb-4 shadow-sm dark:shadow-none transition-colors">
              <span className="w-2 h-2 rounded-full bg-[#00B9DE] shadow-[0_0_8px_rgba(0,185,222,0.5)]"></span>
              <span className="text-[10px] uppercase tracking-wider font-medium text-slate-600 dark:text-white/60 transition-colors">Controle de Acesso</span>
            </div>
            <h1 className="text-3xl md:text-4xl font-medium tracking-tight mb-2">Painel Administrativo</h1>
            <p className="text-slate-500 dark:text-white/40 font-light text-sm max-w-xl transition-colors">
              Monitore credenciais, gerencie administradores e libere o acesso ao sistema.
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row items-center gap-4 w-full md:w-auto">
            <div className="relative group w-full sm:w-64">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                <Search className="text-slate-400 dark:text-white/30 group-focus-within:text-[#D12A6A] dark:group-focus-within:text-[#D12A6A] transition-colors" size={16} />
              </div>
              <input 
                type="text" 
                placeholder="Buscar usuário..." 
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full bg-white/50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.08] rounded-xl pl-10 pr-4 py-2.5 focus:outline-none focus:border-[#D12A6A]/50 focus:bg-white dark:focus:bg-white/[0.05] transition-all font-light text-sm text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-white/30 backdrop-blur-md shadow-[inset_0_1px_3px_rgba(0,0,0,0.02)] dark:shadow-[inset_0_1px_3px_rgba(0,0,0,0.1)]"
              />
            </div>
            
            <div className="flex gap-2 w-full sm:w-auto">
              <a 
                href={`${API_URL}/admin/export/checkins`}
                target="_blank"
                rel="noreferrer"
                className="flex-1 sm:flex-none inline-flex items-center justify-center gap-2 px-3 py-2.5 bg-white/50 hover:bg-white dark:bg-white/[0.03] dark:hover:bg-white/[0.08] text-slate-600 dark:text-white/70 hover:text-slate-900 dark:hover:text-white font-medium tracking-wide text-[11px] uppercase rounded-xl border border-slate-200 dark:border-white/[0.08] shadow-sm transition-all active:scale-95"
                title="Exportar Pontos (CSV)"
              >
                <Download size={14} />
                <span className="hidden sm:inline">Pontos</span>
              </a>
              <a 
                href={`${API_URL}/admin/export/usuarios`}
                target="_blank"
                rel="noreferrer"
                className="flex-1 sm:flex-none inline-flex items-center justify-center gap-2 px-3 py-2.5 bg-white/50 hover:bg-white dark:bg-white/[0.03] dark:hover:bg-white/[0.08] text-slate-600 dark:text-white/70 hover:text-slate-900 dark:hover:text-white font-medium tracking-wide text-[11px] uppercase rounded-xl border border-slate-200 dark:border-white/[0.08] shadow-sm transition-all active:scale-95"
                title="Exportar Usuários (CSV)"
              >
                <Download size={14} />
                <span className="hidden sm:inline">Usuários</span>
              </a>
            </div>

            <button 
              onClick={() => setShowAddAdmin(true)}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-[#D12A6A] to-[#B01E55] hover:from-[#D12A6A] hover:to-[#F39200] text-white font-medium tracking-wide text-xs rounded-xl shadow-[0_4px_14px_rgba(209,42,106,0.3)] hover:shadow-[0_6px_20px_rgba(209,42,106,0.4)] transition-all active:scale-95 border border-[#D12A6A]/50"
            >
              <Plus size={16} />
              Novo Admin
            </button>
          </div>
        </div>

        {/* Data Board */}
        <div className="backdrop-blur-[40px] bg-white/70 dark:bg-white/[0.02] border border-slate-200 dark:border-white/[0.05] rounded-[1.5rem] shadow-[0_24px_48px_rgba(0,0,0,0.05)] dark:shadow-[inset_0_1px_0_rgba(255,255,255,0.05),0_12px_24px_rgba(0,0,0,0.2)] overflow-hidden relative transition-colors duration-500">
          
          {/* Subtle top edge highlight */}
          <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-slate-300 dark:via-white/10 to-transparent transition-colors"></div>

          {loading ? (
            <div className="p-32 flex justify-center items-center">
              <div className="w-8 h-8 border-2 border-slate-200 dark:border-white/10 border-t-[#D12A6A] rounded-full animate-spin" />
            </div>
          ) : filteredUsers.length === 0 ? (
            <div className="py-32 px-6 text-center flex flex-col items-center">
              <div className="w-16 h-16 bg-white dark:bg-white/[0.02] border border-slate-200 dark:border-white/[0.05] rounded-full flex items-center justify-center text-slate-400 dark:text-white/20 mb-5 shadow-sm dark:shadow-inner transition-colors">
                <Users size={24} strokeWidth={1.5} />
              </div>
              <h3 className="text-slate-800 dark:text-white/80 font-medium tracking-tight text-lg mb-1 transition-colors">Nenhum registro</h3>
              <p className="text-slate-500 dark:text-white/40 font-light text-sm transition-colors">Não há colaboradores correspondentes à sua busca.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left whitespace-nowrap">
                <thead className="border-b border-slate-200 dark:border-white/[0.05] bg-white/50 dark:bg-white/[0.01] transition-colors">
                  <tr>
                    <th className="px-8 py-5 text-[10px] font-medium text-slate-500 dark:text-white/30 uppercase tracking-[0.15em] transition-colors">Colaborador</th>
                    <th className="px-8 py-5 text-[10px] font-medium text-slate-500 dark:text-white/30 uppercase tracking-[0.15em] transition-colors">Função</th>
                    <th className="px-8 py-5 text-[10px] font-medium text-slate-500 dark:text-white/30 uppercase tracking-[0.15em] transition-colors">Status</th>
                    <th className="px-8 py-5 text-right text-[10px] font-medium text-slate-500 dark:text-white/30 uppercase tracking-[0.15em] transition-colors">Ação</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-white/[0.03] transition-colors">
                  {filteredUsers.map(user => (
                    <tr key={user.id} className="hover:bg-white dark:hover:bg-white/[0.02] transition-colors group">
                      <td className="px-8 py-5">
                        <div className="font-medium text-slate-900 dark:text-white/90 text-sm mb-0.5 transition-colors">{user.nome}</div>
                        <div className="text-slate-500 dark:text-white/40 text-xs font-light transition-colors">{user.email}</div>
                      </td>
                      <td className="px-8 py-5">
                        <span className="inline-flex items-center px-2.5 py-1 rounded-md bg-slate-100 dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.05] text-slate-600 dark:text-white/60 text-[10px] font-medium tracking-wider uppercase transition-colors">
                          {user.tipo}
                        </span>
                      </td>
                      <td className="px-8 py-5">
                        {user.admin_aprovado ? (
                          <div className="flex items-center gap-2">
                            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
                            <span className="text-emerald-600 dark:text-emerald-400/90 text-[11px] font-medium tracking-wide transition-colors">Aprovado</span>
                          </div>
                        ) : (
                          <div className="flex items-center gap-2">
                            <div className="w-1.5 h-1.5 rounded-full bg-[#F39200] shadow-[0_0_8px_rgba(243,146,0,0.5)]"></div>
                            <span className="text-[#F39200] dark:text-[#F39200]/90 text-[11px] font-medium tracking-wide transition-colors">Pendente</span>
                          </div>
                        )}
                      </td>
                      <td className="px-8 py-5 text-right">
                        <div className="flex items-center justify-end gap-3">
                          {!user.admin_aprovado && (
                            <button 
                              onClick={() => setShowPopup({ visible: true, userId: user.id, userName: user.nome })}
                              className="inline-flex items-center justify-center px-4 py-1.5 bg-[#D12A6A]/10 hover:bg-[#D12A6A] text-[#D12A6A] hover:text-white font-medium tracking-wide text-xs rounded-lg transition-all border border-[#D12A6A]/20 hover:border-[#D12A6A] active:scale-95"
                            >
                              Autorizar
                            </button>
                          )}
                          <button 
                            onClick={() => handleDelete(user.id)}
                            className="text-slate-400 hover:text-red-500 dark:text-white/20 dark:hover:text-red-400 transition-colors"
                            title="Excluir Usuário"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>

      {/* Approve Modal */}
      {showPopup.visible && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-slate-900/40 dark:bg-black/60 backdrop-blur-sm transition-opacity" onClick={() => setShowPopup({ visible: false, userId: null, userName: '' })}></div>
          
          <div className="relative w-full max-w-sm backdrop-blur-[40px] bg-white/90 dark:bg-[#0A0A0A]/80 border border-slate-200 dark:border-white/[0.08] rounded-[2rem] p-8 shadow-[0_24px_48px_rgba(0,0,0,0.1)] dark:shadow-[inset_0_1px_0_rgba(255,255,255,0.1),0_24px_48px_rgba(0,0,0,0.6)] overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            <div className="absolute -top-24 -right-24 w-48 h-48 bg-[#D12A6A]/10 dark:bg-[#D12A6A]/20 rounded-full blur-[60px] pointer-events-none mix-blend-multiply dark:mix-blend-screen"></div>
            
            <div className="relative z-10">
              <div className="w-12 h-12 rounded-[1rem] bg-[#D12A6A]/10 border border-[#D12A6A]/20 flex items-center justify-center mb-5 text-[#D12A6A] shadow-inner">
                <CheckCircle size={22} strokeWidth={2} />
              </div>
              
              <h3 className="text-xl font-medium tracking-tight mb-2 text-slate-900 dark:text-white">Autorizar Acesso</h3>
              <p className="text-slate-600 dark:text-white/50 font-light text-sm mb-8 leading-relaxed">
                Você está concedendo permissão de acesso ao ponto para <span className="text-slate-900 dark:text-white font-medium">{showPopup.userName}</span>.
              </p>
              
              <div className="flex gap-3">
                <button 
                  onClick={() => setShowPopup({ visible: false, userId: null, userName: '' })}
                  className="flex-1 py-2.5 px-4 bg-slate-100 hover:bg-slate-200 dark:bg-white/[0.03] dark:hover:bg-white/[0.08] border border-slate-200 dark:border-white/[0.08] text-slate-700 dark:text-white/70 font-medium rounded-xl transition-all tracking-wide text-xs active:scale-95"
                >
                  Cancelar
                </button>
                <button 
                  onClick={confirmApprove}
                  className="flex-1 py-2.5 px-4 bg-[#D12A6A] hover:bg-[#B01E55] text-white font-medium rounded-xl shadow-[0_4px_14px_rgba(209,42,106,0.3)] hover:shadow-[0_6px_20px_rgba(209,42,106,0.4)] transition-all tracking-wide text-xs active:scale-95 border border-[#D12A6A]"
                >
                  Confirmar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add Admin Modal */}
      {showAddAdmin && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-slate-900/40 dark:bg-black/60 backdrop-blur-sm transition-opacity" onClick={() => setShowAddAdmin(false)}></div>
          
          <div className="relative w-full max-w-sm backdrop-blur-[40px] bg-white/90 dark:bg-[#0A0A0A]/80 border border-slate-200 dark:border-white/[0.08] rounded-[2rem] p-8 shadow-[0_24px_48px_rgba(0,0,0,0.1)] dark:shadow-[inset_0_1px_0_rgba(255,255,255,0.1),0_24px_48px_rgba(0,0,0,0.6)] overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            <div className="absolute -top-24 -left-24 w-48 h-48 bg-[#00B9DE]/10 dark:bg-[#00B9DE]/20 rounded-full blur-[60px] pointer-events-none mix-blend-multiply dark:mix-blend-screen"></div>
            
            <div className="relative z-10">
              <h3 className="text-xl font-medium tracking-tight mb-2 text-slate-900 dark:text-white">Novo Administrador</h3>
              <p className="text-slate-600 dark:text-white/50 font-light text-sm mb-6 leading-relaxed">
                Adicione um novo usuário STAFF com acesso ao painel.
              </p>
              
              <form onSubmit={handleAddAdmin} className="space-y-4 mb-8">
                <div>
                  <label className="block text-[10px] uppercase tracking-widest text-slate-500 dark:text-white/40 mb-1.5 ml-1">Nome</label>
                  <input 
                    type="text" 
                    required
                    value={newAdmin.nome}
                    onChange={e => setNewAdmin({...newAdmin, nome: e.target.value})}
                    className="w-full bg-white dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.08] rounded-xl px-4 py-2.5 focus:outline-none focus:border-[#00B9DE]/50 focus:bg-white dark:focus:bg-white/[0.05] transition-all font-light text-sm text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-white/30 shadow-[inset_0_2px_4px_rgba(0,0,0,0.02)]"
                    placeholder="João Silva"
                  />
                </div>
                <div>
                  <label className="block text-[10px] uppercase tracking-widest text-slate-500 dark:text-white/40 mb-1.5 ml-1">E-mail</label>
                  <input 
                    type="email" 
                    required
                    value={newAdmin.email}
                    onChange={e => setNewAdmin({...newAdmin, email: e.target.value})}
                    className="w-full bg-white dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.08] rounded-xl px-4 py-2.5 focus:outline-none focus:border-[#00B9DE]/50 focus:bg-white dark:focus:bg-white/[0.05] transition-all font-light text-sm text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-white/30 shadow-[inset_0_2px_4px_rgba(0,0,0,0.02)]"
                    placeholder="joao@lablivre.com"
                  />
                </div>
                <div>
                  <label className="block text-[10px] uppercase tracking-widest text-slate-500 dark:text-white/40 mb-1.5 ml-1">Senha Provisória</label>
                  <input 
                    type="password" 
                    required
                    value={newAdmin.senha}
                    onChange={e => setNewAdmin({...newAdmin, senha: e.target.value})}
                    className="w-full bg-white dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.08] rounded-xl px-4 py-2.5 focus:outline-none focus:border-[#00B9DE]/50 focus:bg-white dark:focus:bg-white/[0.05] transition-all font-light text-sm text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-white/30 shadow-[inset_0_2px_4px_rgba(0,0,0,0.02)]"
                    placeholder="••••••••"
                  />
                </div>
                <button type="submit" className="hidden"></button>
              </form>
              
              <div className="flex gap-3">
                <button 
                  onClick={() => setShowAddAdmin(false)}
                  className="flex-1 py-2.5 px-4 bg-slate-100 hover:bg-slate-200 dark:bg-white/[0.03] dark:hover:bg-white/[0.08] border border-slate-200 dark:border-white/[0.08] text-slate-700 dark:text-white/70 font-medium rounded-xl transition-all tracking-wide text-xs active:scale-95"
                >
                  Cancelar
                </button>
                <button 
                  onClick={handleAddAdmin}
                  disabled={isSubmitting || !newAdmin.nome || !newAdmin.email || !newAdmin.senha}
                  className="flex-1 py-2.5 px-4 bg-[#00B9DE] hover:bg-[#009bb8] text-white font-medium rounded-xl shadow-[0_4px_14px_rgba(0,185,222,0.3)] hover:shadow-[0_6px_20px_rgba(0,185,222,0.4)] transition-all tracking-wide text-xs active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed border border-[#00B9DE]"
                >
                  {isSubmitting ? 'Adicionando...' : 'Adicionar'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
