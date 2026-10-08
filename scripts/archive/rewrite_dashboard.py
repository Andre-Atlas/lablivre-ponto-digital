import re

with open('web_admin/src/pages/Dashboard.tsx', 'r') as f:
    content = f.read()

# Add new icons
content = content.replace(
    "import { LogOut, Download, Plus, Search, Trash2, Shield, User, Monitor, Eye, EyeOff, Calendar } from 'lucide-react';",
    "import { LogOut, Download, Plus, Search, Trash2, Shield, User, Monitor, Eye, EyeOff, Calendar, Edit3, CheckSquare } from 'lucide-react';"
)

# Add selectedUsers state
content = content.replace(
    "const [showPassword, setShowPassword] = useState(false);",
    "const [showPassword, setShowPassword] = useState(false);\n  const [selectedUsers, setSelectedUsers] = useState<Set<string>>(new Set());\n  const [showEditUser, setShowEditUser] = useState<any>(null);"
)

# Add handleBulkAprovar and Justificar
bulk_actions = """
  const handleBulkAprovar = async () => {
    if (selectedUsers.size === 0) return;
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API_URL}/api/v1/admin/usuarios/bulk-aprovar`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_ids: Array.from(selectedUsers) })
      });
      if (!res.ok) throw new Error('Falha ao aprovar');
      fetchUsers();
      setSelectedUsers(new Set());
    } catch (e) {
      console.error(e);
      alert('Erro ao aprovar usuários');
    }
  };

  const handleEditUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!showEditUser) return;
    setIsSubmitting(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API_URL}/api/v1/admin/usuarios/${showEditUser.id}`, {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          turma_ou_equipe: showEditUser.turma_ou_equipe,
          patrimonio: showEditUser.patrimonio,
          tipo: showEditUser.tipo
        })
      });
      if (!res.ok) throw new Error('Falha ao editar');
      fetchUsers();
      setShowEditUser(null);
    } catch (e) {
      console.error(e);
      alert('Erro ao editar usuário');
    } finally {
      setIsSubmitting(false);
    }
  };
"""
content = content.replace("const handleJustificar = async (e: React.FormEvent) => {", bulk_actions + "\n  const handleJustificar = async (e: React.FormEvent) => {")

# Justificar was for 1 user, we need to adapt it to handle bulk
content = content.replace(
    "const handleJustificar = async (e: React.FormEvent) => {",
    "const handleJustificar = async (e: React.FormEvent) => {\n    e.preventDefault();\n    setIsSubmitting(true);\n    try {\n      const token = localStorage.getItem('token');\n      const userIds = showJustificar.userId ? [showJustificar.userId] : Array.from(selectedUsers);\n      const res = await fetch(`${API_URL}/api/v1/admin/usuarios/bulk-justificar`, {\n        method: 'POST',\n        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },\n        body: JSON.stringify({ user_ids: userIds, data: showJustificar.data, turno: showJustificar.turno })\n      });\n      if (!res.ok) throw new Error('Falha ao justificar');\n      setShowJustificar({ visible: false, userId: null, data: '', turno: 'MANHA' });\n      setSelectedUsers(new Set());\n    } catch (err) {\n      console.error(err);\n    } finally {\n      setIsSubmitting(false);\n    }\n  };\n  // "
)

# Bulk Action Bar
bulk_bar = """
        {selectedUsers.size > 0 && (
          <div className="mb-6 p-4 bg-[#00B9DE]/10 border border-[#00B9DE]/20 rounded-2xl flex items-center justify-between">
            <span className="text-sm font-medium text-[#00B9DE] flex items-center gap-2">
              <CheckSquare size={18} /> {selectedUsers.size} usuários selecionados
            </span>
            <div className="flex gap-3">
              <button onClick={handleBulkAprovar} className="px-4 py-2 bg-[#00B9DE] text-white text-xs font-semibold rounded-xl hover:bg-[#009bb8] transition">Autorizar Selecionados</button>
              <button onClick={() => setShowJustificar({ visible: true, userId: null, data: '', turno: 'MANHA' })} className="px-4 py-2 bg-emerald-500 text-white text-xs font-semibold rounded-xl hover:bg-emerald-600 transition">Justificar Selecionados</button>
            </div>
          </div>
        )}
"""

content = content.replace(
    '<div className="overflow-x-auto">',
    bulk_bar + '\n        <div className="overflow-x-auto">'
)

# Table headers
th_replace = """
                <th className="py-4 px-6 text-left font-medium text-[10px] uppercase tracking-widest text-slate-400 dark:text-white/30 whitespace-nowrap">
                  <input type="checkbox" onChange={(e) => {
                    if (e.target.checked) setSelectedUsers(new Set(filteredUsers.map(u => u.id)));
                    else setSelectedUsers(new Set());
                  }} checked={selectedUsers.size > 0 && selectedUsers.size === filteredUsers.length} className="rounded border-slate-300" />
                </th>
                <th className="py-4 px-6 text-left font-medium text-[10px] uppercase tracking-widest text-slate-400 dark:text-white/30 whitespace-nowrap">
"""
content = content.replace(
    '<th className="py-4 px-6 text-left font-medium text-[10px] uppercase tracking-widest text-slate-400 dark:text-white/30 whitespace-nowrap">',
    th_replace,
    1
)

# Table rows
tr_replace = """
                  <td className="py-4 px-6 border-b border-slate-100 dark:border-white/[0.05]">
                    <input type="checkbox" checked={selectedUsers.has(user.id)} onChange={(e) => {
                      const newSet = new Set(selectedUsers);
                      if (e.target.checked) newSet.add(user.id);
                      else newSet.delete(user.id);
                      setSelectedUsers(newSet);
                    }} className="rounded border-slate-300" />
                  </td>
                  <td className="py-4 px-6 border-b border-slate-100 dark:border-white/[0.05]">
"""
content = content.replace(
    '<td className="py-4 px-6 border-b border-slate-100 dark:border-white/[0.05]">',
    tr_replace,
    1 # wait, this replace might apply to the first td of EACH row or just the first row in the string?
      # I need to use re.sub for all rows!
)
# Revert the naive replace and do regex
content = content.replace(tr_replace, '<td className="py-4 px-6 border-b border-slate-100 dark:border-white/[0.05]">')

content = re.sub(
    r'(<tr key=\{user\.id\}[^>]*>\s*)<td',
    r'\1<td className="py-4 px-6 border-b border-slate-100 dark:border-white/[0.05]"><input type="checkbox" checked={selectedUsers.has(user.id)} onChange={(e) => { const newSet = new Set(selectedUsers); if (e.target.checked) newSet.add(user.id); else newSet.delete(user.id); setSelectedUsers(newSet); }} /></td><td',
    content
)

# Add Edit User button next to trash
btn_edit = """
                      <button onClick={() => setShowEditUser(user)} className="p-2 text-slate-400 hover:text-blue-500 hover:bg-blue-50 dark:hover:bg-blue-500/10 rounded-lg transition-colors" title="Editar">
                        <Edit3 size={16} />
                      </button>
                      <button
"""
content = content.replace(
    '<button\n                        onClick={() => handleDeleteUser(user.id)}',
    btn_edit + 'onClick={() => handleDeleteUser(user.id)}'
)
content = content.replace(
    '<button onClick={() => handleDeleteUser(user.id)}',
    btn_edit.strip() + ' onClick={() => handleDeleteUser(user.id)}'
)

# Edit User Modal
edit_modal = """
      {showEditUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-slate-900/40 dark:bg-black/60 backdrop-blur-sm" onClick={() => setShowEditUser(null)}></div>
          <div className="relative w-full max-w-sm bg-white dark:bg-[#0A0A0A] rounded-[2rem] p-8 z-10 border border-slate-200 dark:border-white/[0.08]">
            <h3 className="text-xl font-medium mb-4 dark:text-white">Editar Usuário</h3>
            <form onSubmit={handleEditUser} className="space-y-4">
              <div>
                <label className="block text-xs uppercase text-slate-500 mb-1">Turma</label>
                <input value={showEditUser.turma_ou_equipe || ''} onChange={e => setShowEditUser({...showEditUser, turma_ou_equipe: e.target.value})} className="w-full bg-slate-50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.08] rounded-xl px-4 py-2 dark:text-white" />
              </div>
              <div>
                <label className="block text-xs uppercase text-slate-500 mb-1">Máquina (Patrimônio)</label>
                <input value={showEditUser.patrimonio || ''} onChange={e => setShowEditUser({...showEditUser, patrimonio: e.target.value})} className="w-full bg-slate-50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.08] rounded-xl px-4 py-2 dark:text-white" />
              </div>
              <div>
                <label className="block text-xs uppercase text-slate-500 mb-1">Tipo</label>
                <select value={showEditUser.tipo || 'ALUNO'} onChange={e => setShowEditUser({...showEditUser, tipo: e.target.value})} className="w-full bg-slate-50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.08] rounded-xl px-4 py-2 dark:text-white">
                  <option value="ALUNO">Aluno</option>
                  <option value="STAFF">Staff</option>
                  <option value="ADMIN">Admin</option>
                </select>
              </div>
              <div className="flex gap-3 mt-6">
                <button type="button" onClick={() => setShowEditUser(null)} className="flex-1 py-2 bg-slate-100 dark:bg-white/[0.03] rounded-xl dark:text-white/70">Cancelar</button>
                <button type="submit" disabled={isSubmitting} className="flex-1 py-2 bg-blue-500 text-white rounded-xl">Salvar</button>
              </div>
            </form>
          </div>
        </div>
      )}
"""
content = content.replace('{/* Add Admin Modal */}', edit_modal + '\n      {/* Add Admin Modal */}')


with open('web_admin/src/pages/Dashboard.tsx', 'w') as f:
    f.write(content)
