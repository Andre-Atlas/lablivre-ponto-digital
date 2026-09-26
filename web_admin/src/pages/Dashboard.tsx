import { useEffect, useState } from 'react';
import { Users, CheckCircle, Clock, Search, LogOut, Trash2, Monitor, Download } from 'lucide-react';
import type { User } from "../services/api";
import { fetchUsers, approveUser, deleteUser } from '../services/api';

const getRoleBadge = (tipo: string) => {
  const role = tipo.toUpperCase();
  switch (role) {
    case 'SUPER_ADMIN':
      return <span className="inline-flex items-center px-2 py-1 rounded-md bg-purple-100 text-purple-700 text-xs font-semibold tracking-wide">SUPER ADMIN</span>;
    case 'ADMIN':
      return <span className="inline-flex items-center px-2 py-1 rounded-md bg-indigo-100 text-indigo-700 text-xs font-semibold tracking-wide">ADMIN</span>;
    case 'STAFF':
      return <span className="inline-flex items-center px-2 py-1 rounded-md bg-blue-100 text-blue-700 text-xs font-semibold tracking-wide">STAFF</span>;
    case 'ALUNO':
      return <span className="inline-flex items-center px-2 py-1 rounded-md bg-zinc-100 text-zinc-700 text-xs font-semibold tracking-wide">ALUNO</span>;
    default:
      return <span className="inline-flex items-center px-2 py-1 rounded-md bg-gray-100 text-gray-700 text-xs font-semibold tracking-wide">{tipo}</span>;
  }
};

export function Dashboard({ onLogout }: { onLogout: () => void }) {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const data = await fetchUsers();
      setUsers(data);
    } catch (e) {
      console.error(e);
      // Fallback mock data
      setUsers([
        { id: '1', nome: 'Alice Silva', email: 'alice@example.com', tipo: 'SUPER_ADMIN', admin_aprovado: true },
        { id: '2', nome: 'Bruno Costa', email: 'bruno@example.com', tipo: 'STAFF', admin_aprovado: false },
        { id: '3', nome: 'Carlos Souza', email: 'carlos@example.com', tipo: 'ALUNO', admin_aprovado: true },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id: string | number) => {
    setUsers(prev => prev.map(u => u.id === id ? { ...u, admin_aprovado: true } : u));
    try {
      await approveUser(id);
    } catch (e) {
      console.error(e);
      await loadUsers(); // revert
    }
  };

  const handleDelete = async (id: string | number) => {
    if (!window.confirm('Are you sure you want to delete this user?')) return;
    setUsers(prev => prev.filter(u => u.id !== id));
    try {
      await deleteUser(id);
    } catch (e) {
      console.error(e);
      await loadUsers(); // revert
    }
  };

  const filteredUsers = users.filter(u => u.nome.toLowerCase().includes(search.toLowerCase()) || u.email.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="min-h-screen bg-zinc-50/50">
      <header className="bg-white border-b border-zinc-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white shadow-sm">
              <Users size={18} />
            </div>
            <h1 className="font-semibold text-zinc-900">Admin Portal</h1>
          </div>
          <button onClick={onLogout} className="text-zinc-500 hover:text-zinc-900 transition-colors p-2 rounded-lg hover:bg-zinc-100 flex items-center gap-2 text-sm font-medium">
            <LogOut size={16} /> Logout
          </button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        {/* Downloads Banner */}
        <div className="bg-gradient-to-r from-indigo-500 to-indigo-700 rounded-2xl shadow-md overflow-hidden mb-8 p-6 sm:p-8 text-white flex flex-col sm:flex-row sm:items-center justify-between gap-6 border border-indigo-400/20">
          <div>
            <h2 className="text-xl font-semibold flex items-center gap-2">
              <Monitor size={22} className="text-indigo-200" />
              Desktop Client
            </h2>
            <p className="text-indigo-100 mt-2 text-sm max-w-md leading-relaxed">
              Download the official Ponto Digital desktop application to start tracking time and managing your local station securely.
            </p>
          </div>
          <div className="flex flex-col sm:flex-row gap-3">
            <a 
              href="https://github.com/Andre-Atlas/lablivre-ponto-digital/releases/latest" 
              target="_blank" 
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-white/10 hover:bg-white/20 border border-white/20 rounded-xl transition-all font-medium text-sm backdrop-blur-sm"
            >
              <Download size={16} /> Baixar Client (Windows)
            </a>
            <a 
              href="https://github.com/Andre-Atlas/lablivre-ponto-digital/releases/latest" 
              target="_blank" 
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-white/10 hover:bg-white/20 border border-white/20 rounded-xl transition-all font-medium text-sm backdrop-blur-sm"
            >
              <Download size={16} /> Baixar Client (Linux)
            </a>
            <a 
              href="https://github.com/Andre-Atlas/lablivre-ponto-digital/releases/latest" 
              target="_blank" 
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-white text-indigo-700 hover:bg-indigo-50 hover:scale-[1.02] active:scale-[0.98] rounded-xl transition-all font-medium text-sm shadow-sm"
            >
              <Download size={16} /> Baixar Client (Mac)
            </a>
          </div>
        </div>

        {/* Users Section */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4">
          <div>
            <h2 className="text-xl font-semibold text-zinc-900">User Approvals</h2>
            <p className="text-sm text-zinc-500 mt-1">Manage system access and roles.</p>
          </div>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400" size={18} />
            <input 
              type="text" 
              placeholder="Search users..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10 pr-4 py-2 w-full sm:w-64 bg-white border border-zinc-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-sm text-zinc-900 shadow-sm"
            />
          </div>
        </div>

        <div className="bg-white border border-zinc-200 rounded-2xl shadow-sm overflow-hidden">
          {loading ? (
            <div className="p-8 flex justify-center">
              <div className="w-6 h-6 border-2 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
            </div>
          ) : filteredUsers.length === 0 ? (
            <div className="p-12 text-center flex flex-col items-center">
              <div className="w-12 h-12 bg-zinc-100 rounded-full flex items-center justify-center text-zinc-400 mb-3">
                <Users size={24} />
              </div>
              <h3 className="text-zinc-900 font-medium">No users found</h3>
              <p className="text-zinc-500 text-sm mt-1">Try adjusting your search criteria.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm whitespace-nowrap">
                <thead className="bg-zinc-50/50 border-b border-zinc-200 text-zinc-500">
                  <tr>
                    <th className="px-6 py-4 font-medium">Name</th>
                    <th className="px-6 py-4 font-medium">Role</th>
                    <th className="px-6 py-4 font-medium">Status</th>
                    <th className="px-6 py-4 font-medium text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-100">
                  {filteredUsers.map(user => (
                    <tr key={user.id} className="hover:bg-zinc-50/50 transition-colors group">
                      <td className="px-6 py-4">
                        <div className="font-medium text-zinc-900">{user.nome}</div>
                        <div className="text-zinc-500 text-xs mt-0.5">{user.email}</div>
                      </td>
                      <td className="px-6 py-4">
                        {getRoleBadge(user.tipo)}
                      </td>
                      <td className="px-6 py-4">
                        {user.admin_aprovado ? (
                          <span className="inline-flex items-center gap-1.5 text-emerald-600 bg-emerald-50 px-2 py-1 rounded-md text-xs font-medium">
                            <CheckCircle size={14} /> Approved
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1.5 text-amber-600 bg-amber-50 px-2 py-1 rounded-md text-xs font-medium">
                            <Clock size={14} /> Pending
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 focus-within:opacity-100 transition-opacity">
                          {!user.admin_aprovado && (
                            <button 
                              onClick={() => handleApprove(user.id)}
                              className="inline-flex items-center justify-center px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-600 font-medium text-xs rounded-lg transition-colors"
                            >
                              Approve
                            </button>
                          )}
                          <button 
                            onClick={() => handleDelete(user.id)}
                            className="inline-flex items-center justify-center p-1.5 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                            title="Delete user"
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
    </div>
  );
}
