import re

# 1. Update api.ts
with open("web_admin/src/services/api.ts", "r") as f:
    api_content = f.read()

justificar_fn = """
export const justificarFalta = async (id: string | number, data: string, turno: string): Promise<void> => {
  const res = await fetch(`${API_URL}/admin/usuarios/${id}/justificar`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}` 
    },
    body: JSON.stringify({ data, turno })
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || 'Falha ao justificar falta');
  }
};
"""
if "justificarFalta" not in api_content:
    api_content += justificar_fn

with open("web_admin/src/services/api.ts", "w") as f:
    f.write(api_content)

# 2. Update Dashboard.tsx
with open("web_admin/src/pages/Dashboard.tsx", "r") as f:
    dash = f.read()

# Add to imports
if "justificarFalta" not in dash:
    dash = dash.replace("createAdmin, updateRole", "createAdmin, updateRole, justificarFalta")
if "Calendar" not in dash:
    dash = dash.replace("Trash2, Plus, Download, Eye, EyeOff", "Trash2, Plus, Download, Eye, EyeOff, Calendar")

# Add state
if "showJustificar" not in dash:
    dash = dash.replace(
        "const [showAddAdmin, setShowAddAdmin] = useState(false);",
        "const [showAddAdmin, setShowAddAdmin] = useState(false);\n  const [showJustificar, setShowJustificar] = useState({ visible: false, userId: null as string | number | null, userName: '', data: '', turno: 'MANHA' });"
    )

# Add handler
handler = """
  const handleJustificar = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!showJustificar.userId || !showJustificar.data) return;
    setIsSubmitting(true);
    try {
      await justificarFalta(showJustificar.userId, showJustificar.data, showJustificar.turno);
      alert('Falta justificada com sucesso!');
      setShowJustificar({ visible: false, userId: null, userName: '', data: '', turno: 'MANHA' });
      loadUsers();
    } catch(err: any) {
      alert(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };
"""
if "handleJustificar" not in dash:
    dash = dash.replace("const handleAddAdmin", handler + "\n  const handleAddAdmin")

# Add button
btn = """
                        <button
                          onClick={() => setShowJustificar({ visible: true, userId: user.id, userName: user.nome, data: new Date().toISOString().split('T')[0], turno: 'MANHA' })}
                          className="p-2 text-emerald-500 hover:bg-emerald-50 dark:hover:bg-emerald-500/10 rounded-xl transition-colors mr-1"
                          title="Justificar Falta"
                        >
                          <Calendar size={16} />
                        </button>
"""
if "Justificar Falta" not in dash:
    dash = re.sub(r'(<button\s*onClick=\{\(\) => handlePromote)', btn + r'\1', dash)

# Add modal
modal = """
      {/* Justificar Modal */}
      {showJustificar.visible && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-slate-900/40 dark:bg-black/60 backdrop-blur-sm transition-opacity" onClick={() => setShowJustificar({ ...showJustificar, visible: false })}></div>
          
          <div className="relative w-full max-w-sm backdrop-blur-[40px] bg-white/90 dark:bg-[#0A0A0A]/80 border border-slate-200 dark:border-white/[0.08] rounded-[2rem] p-8 shadow-[0_24px_48px_rgba(0,0,0,0.1)] dark:shadow-[inset_0_1px_0_rgba(255,255,255,0.1),0_24px_48px_rgba(0,0,0,0.6)] overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            <div className="absolute -top-24 -right-24 w-48 h-48 bg-emerald-500/10 dark:bg-emerald-500/20 rounded-full blur-[60px] pointer-events-none mix-blend-multiply dark:mix-blend-screen"></div>
            
            <div className="relative z-10">
              <h3 className="text-xl font-medium tracking-tight mb-2 text-slate-900 dark:text-white">Justificar Falta</h3>
              <p className="text-slate-600 dark:text-white/50 font-light text-sm mb-6 leading-relaxed">
                Adicione uma justificativa de falta para <span className="text-slate-900 dark:text-white font-medium">{showJustificar.userName}</span>.
              </p>
              
              <form onSubmit={handleJustificar} className="space-y-4 mb-8">
                <div>
                  <label className="block text-[10px] uppercase tracking-widest text-slate-500 dark:text-white/40 mb-1.5 ml-1">Data (YYYY-MM-DD)</label>
                  <input 
                    type="date" 
                    required
                    value={showJustificar.data}
                    onChange={e => setShowJustificar({...showJustificar, data: e.target.value})}
                    className="w-full bg-white dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.08] rounded-xl px-4 py-2.5 focus:outline-none focus:border-emerald-500/50 focus:bg-white dark:focus:bg-white/[0.05] transition-all font-light text-sm text-slate-900 dark:text-white shadow-[inset_0_2px_4px_rgba(0,0,0,0.02)]"
                  />
                </div>
                <div>
                  <label className="block text-[10px] uppercase tracking-widest text-slate-500 dark:text-white/40 mb-1.5 ml-1">Turno</label>
                  <select
                    value={showJustificar.turno}
                    onChange={e => setShowJustificar({...showJustificar, turno: e.target.value})}
                    className="w-full bg-white dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.08] rounded-xl px-4 py-2.5 focus:outline-none focus:border-emerald-500/50 focus:bg-white dark:focus:bg-white/[0.05] transition-all font-light text-sm text-slate-900 dark:text-white shadow-[inset_0_2px_4px_rgba(0,0,0,0.02)]"
                  >
                    <option value="MANHA">Manhã</option>
                    <option value="TARDE">Tarde</option>
                  </select>
                </div>
                <button type="submit" className="hidden"></button>
              </form>
              
              <div className="flex gap-3">
                <button 
                  onClick={() => setShowJustificar({ ...showJustificar, visible: false })}
                  className="flex-1 py-2.5 px-4 bg-slate-100 hover:bg-slate-200 dark:bg-white/[0.03] dark:hover:bg-white/[0.08] border border-slate-200 dark:border-white/[0.08] text-slate-700 dark:text-white/70 font-medium rounded-xl transition-all tracking-wide text-xs active:scale-95"
                >
                  Cancelar
                </button>
                <button 
                  onClick={handleJustificar}
                  disabled={isSubmitting || !showJustificar.data}
                  className="flex-1 py-2.5 px-4 bg-emerald-500 hover:bg-emerald-600 text-white font-medium rounded-xl shadow-[0_4px_14px_rgba(16,185,129,0.3)] hover:shadow-[0_6px_20px_rgba(16,185,129,0.4)] transition-all tracking-wide text-xs active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed border border-emerald-500"
                >
                  {isSubmitting ? 'Salvando...' : 'Confirmar'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
"""
if "Justificar Modal" not in dash:
    dash = dash.replace("{/* Add Admin Modal */}", modal + "\n      {/* Add Admin Modal */}")

with open("web_admin/src/pages/Dashboard.tsx", "w") as f:
    f.write(dash)
