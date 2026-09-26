import re

# 1. Update Login.tsx to add the download buttons
with open("web_admin/src/pages/Login.tsx", "r") as f:
    login_content = f.read()

downloads_html = """
        {/* Downloads da Tela Inicial */}
        <div className="absolute top-6 right-6 flex flex-col sm:flex-row gap-3 z-50">
          <a 
            href="https://github.com/Andre-Atlas/lablivre-ponto-digital/releases/latest" 
            target="_blank" 
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center gap-2 px-3 py-2 bg-white/40 hover:bg-white/80 backdrop-blur-md text-[#D12A6A] font-medium tracking-wide text-[11px] uppercase rounded-lg border border-[#D12A6A]/20 shadow-sm transition-all"
          >
            Baixar Client (Windows)
          </a>
          <a 
            href="https://github.com/Andre-Atlas/lablivre-ponto-digital/releases/latest" 
            target="_blank" 
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center gap-2 px-3 py-2 bg-white/40 hover:bg-white/80 backdrop-blur-md text-[#D12A6A] font-medium tracking-wide text-[11px] uppercase rounded-lg border border-[#D12A6A]/20 shadow-sm transition-all"
          >
            Baixar Client (Mac)
          </a>
          <a 
            href="https://github.com/Andre-Atlas/lablivre-ponto-digital/releases/latest" 
            target="_blank" 
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center gap-2 px-3 py-2 bg-white/40 hover:bg-white/80 backdrop-blur-md text-[#D12A6A] font-medium tracking-wide text-[11px] uppercase rounded-lg border border-[#D12A6A]/20 shadow-sm transition-all"
          >
            Baixar Client (Linux)
          </a>
        </div>
"""

login_content = login_content.replace('<div className="relative min-h-screen flex items-center justify-center overflow-hidden">', '<div className="relative min-h-screen flex items-center justify-center overflow-hidden">\n' + downloads_html)

with open("web_admin/src/pages/Login.tsx", "w") as f:
    f.write(login_content)

# 2. Update api.ts to include the new CreateAdmin signature and put updateRole
with open("web_admin/src/services/api.ts", "r") as f:
    api_content = f.read()

api_content = api_content.replace('export const createAdmin = async (nome: string, email: string, senha: string): Promise<void> => {', 'export const createAdmin = async (nome: string, email: string, senha: string, role: string = "STAFF"): Promise<void> => {')
api_content = api_content.replace('body: JSON.stringify({ nome, email, senha })', 'body: JSON.stringify({ nome, email, senha, role })')

api_update_role = """
export const updateRole = async (id: string | number, role: string): Promise<void> => {
  const res = await fetch(`${API_URL}/admin/usuarios/${id}/role`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify({ role })
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || 'Failed to update role');
  }
};
"""
api_content += api_update_role

# Add role field to User interface
api_content = api_content.replace('tipo: string;', 'tipo: string;\n  role?: string;')

with open("web_admin/src/services/api.ts", "w") as f:
    f.write(api_content)

# 3. Update Dashboard.tsx
with open("web_admin/src/pages/Dashboard.tsx", "r") as f:
    dash_content = f.read()

dash_content = dash_content.replace('const [newAdmin, setNewAdmin] = useState({ nome: \'\', email: \'\', senha: \'\' });', 'const [newAdmin, setNewAdmin] = useState({ nome: \'\', email: \'\', senha: \'\', role: \'STAFF\' });')

dash_content = dash_content.replace('import { API_URL, fetchUsers, approveUser, deleteUser, createAdmin }', 'import { API_URL, fetchUsers, approveUser, deleteUser, createAdmin, updateRole }')

# Add handlePromote function
promote_fn = """
  const handlePromote = async (id: string | number, currentRole: string) => {
    const newRole = currentRole === 'SUPER_ADMIN' ? 'ADMIN' : (currentRole === 'ADMIN' ? 'SUPER_ADMIN' : 'ADMIN');
    if (!window.confirm(`Tem certeza que deseja alterar o cargo deste usuário para ${newRole}?`)) return;
    try {
      await updateRole(id, newRole);
      loadUsers();
    } catch(e: any) {
      alert(e.message);
    }
  };
"""
dash_content = dash_content.replace('const handleApprove = async () => {', promote_fn + '\n  const handleApprove = async () => {')

# Add the Promote button in the UI next to delete
promote_button = """
                        <button
                          onClick={() => handlePromote(user.id, user.role || 'STAFF')}
                          className="p-2 text-indigo-500 hover:bg-indigo-50 dark:hover:bg-indigo-500/10 rounded-xl transition-colors"
                          title="Alterar Cargo (Promover/Rebaixar)"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m16 16 4-4-4-4"/><path d="M20 12H4"/></svg>
                        </button>
"""
dash_content = dash_content.replace('<button \n                          onClick={() => setDeleteConfirm(user.id)}', promote_button + '\n                        <button \n                          onClick={() => setDeleteConfirm(user.id)}')

# Add select field for role in Add Admin Modal
select_field = """
                <div>
                  <label className="block text-[10px] uppercase tracking-widest text-slate-500 dark:text-white/40 mb-1.5 ml-1">Cargo</label>
                  <select
                    value={newAdmin.role}
                    onChange={e => setNewAdmin({...newAdmin, role: e.target.value})}
                    className="w-full bg-white dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.08] rounded-xl px-4 py-2.5 focus:outline-none focus:border-[#00B9DE]/50 focus:bg-white dark:focus:bg-white/[0.05] transition-all font-light text-sm text-slate-900 dark:text-white shadow-[inset_0_2px_4px_rgba(0,0,0,0.02)]"
                  >
                    <option value="STAFF">Staff (Apenas Ponto)</option>
                    <option value="ADMIN">Admin (Exportar e Editar)</option>
                    <option value="SUPER_ADMIN">Super Admin (Todos os privilégios)</option>
                  </select>
                </div>
"""
dash_content = dash_content.replace('<div>\n                  <label className="block text-[10px] uppercase tracking-widest text-slate-500 dark:text-white/40 mb-1.5 ml-1">Senha Provisória</label>', select_field + '<div>\n                  <label className="block text-[10px] uppercase tracking-widest text-slate-500 dark:text-white/40 mb-1.5 ml-1">Senha Provisória</label>')

# Update handleAddAdmin
dash_content = dash_content.replace('await createAdmin(newAdmin.nome, newAdmin.email, newAdmin.senha);', 'await createAdmin(newAdmin.nome, newAdmin.email, newAdmin.senha, newAdmin.role);')

with open("web_admin/src/pages/Dashboard.tsx", "w") as f:
    f.write(dash_content)
