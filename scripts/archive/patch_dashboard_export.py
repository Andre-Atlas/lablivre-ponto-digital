import re

with open('web_admin/src/pages/Dashboard.tsx', 'r') as f:
    content = f.read()

# Add states for Export Modal
states = """
  const [showExportModal, setShowExportModal] = useState(false);
  const [exportFilters, setExportFilters] = useState({
    formato: 'excel',
    tipo: 'TODOS',
    data: '',
    turma: '',
    turno: ''
  });
"""
content = content.replace("const [showAddAdmin, setShowAddAdmin] = useState(false);", "const [showAddAdmin, setShowAddAdmin] = useState(false);\n" + states)

# Add Download Custom Handle
new_handle = """
  const handleCustomExport = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      let endpoint = `checkins?format=${exportFilters.formato}`;
      if (exportFilters.tipo !== 'TODOS') endpoint += `&tipo=${exportFilters.tipo}`;
      if (exportFilters.turma) endpoint += `&turma=${encodeURIComponent(exportFilters.turma)}`;
      if (exportFilters.turno) endpoint += `&turno=${encodeURIComponent(exportFilters.turno)}`;
      if (exportFilters.data) {
        const [yyyy, mm, dd] = exportFilters.data.split('-');
        endpoint += `&ano=${yyyy}&mes=${mm}&dia=${dd}`;
      }
      
      const filename = `relatorio_pontos.${exportFilters.formato === 'excel' ? 'xlsx' : 'csv'}`;
      await handleExport(endpoint, filename);
      setShowExportModal(false);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };
"""
content = content.replace("const handleExport = async (endpoint: string, filename: string) => {", new_handle + "\n  const handleExport = async (endpoint: string, filename: string) => {")

# Replace old export buttons with a unified one
old_buttons = """              <button 
                onClick={() => handleExport('checkins?tipo=ALUNO', 'pontos_alunos.csv')}
                className="flex-1 sm:flex-none inline-flex items-center justify-center gap-2 px-3 py-2.5 bg-white/50 hover:bg-white dark:bg-white/[0.03] dark:hover:bg-white/[0.08] text-slate-600 dark:text-white/70 hover:text-slate-900 dark:hover:text-white font-medium tracking-wide text-[11px] uppercase whitespace-nowrap rounded-xl border border-slate-200 dark:border-white/[0.08] shadow-sm transition-all active:scale-95 shrink-0"
                title="Exportar Pontos Alunos"
              >
                <Download size={14} />
                <span className="hidden sm:inline">Pontos (Alunos)</span>
              </button>
              
              <button 
                onClick={() => handleExport('checkins?tipo=STAFF', 'pontos_staff.csv')}
                className="flex-1 sm:flex-none inline-flex items-center justify-center gap-2 px-3 py-2.5 bg-white/50 hover:bg-white dark:bg-white/[0.03] dark:hover:bg-white/[0.08] text-slate-600 dark:text-white/70 hover:text-slate-900 dark:hover:text-white font-medium tracking-wide text-[11px] uppercase whitespace-nowrap rounded-xl border border-slate-200 dark:border-white/[0.08] shadow-sm transition-all active:scale-95 shrink-0"
                title="Exportar Pontos Staff"
              >
                <Download size={14} />
                <span className="hidden sm:inline">Pontos (Staff)</span>
              </button>"""

new_button = """              <button 
                onClick={() => setShowExportModal(true)}
                className="flex-1 sm:flex-none inline-flex items-center justify-center gap-2 px-3 py-2.5 bg-[#00B9DE]/10 hover:bg-[#00B9DE]/20 text-[#00B9DE] font-medium tracking-wide text-[11px] uppercase whitespace-nowrap rounded-xl border border-[#00B9DE]/30 shadow-sm transition-all active:scale-95 shrink-0"
                title="Exportar Planilhas (Filtros)"
              >
                <Download size={14} />
                <span className="hidden sm:inline">Exportar Planilhas</span>
              </button>"""

content = content.replace(old_buttons, new_button)

# Add Export Modal
export_modal = """
      {showExportModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-slate-900/40 dark:bg-black/60 backdrop-blur-sm" onClick={() => setShowExportModal(false)}></div>
          <div className="relative w-full max-w-md bg-white dark:bg-[#0A0A0A] rounded-[2rem] p-8 z-10 border border-slate-200 dark:border-white/[0.08]">
            <h3 className="text-xl font-medium mb-4 dark:text-white">Exportar Planilhas</h3>
            <p className="text-slate-500 text-sm mb-6">Selecione os filtros para gerar o relatório de pontos.</p>
            <form onSubmit={handleCustomExport} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] uppercase tracking-widest text-slate-500 dark:text-white/40 mb-1.5">Formato</label>
                  <select value={exportFilters.formato} onChange={e => setExportFilters({...exportFilters, formato: e.target.value})} className="w-full bg-slate-50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.08] rounded-xl px-4 py-2 dark:text-white">
                    <option value="excel">Excel (.xlsx)</option>
                    <option value="csv">CSV</option>
                  </select>
                </div>
                <div>
                  <label className="block text-[10px] uppercase tracking-widest text-slate-500 dark:text-white/40 mb-1.5">Público</label>
                  <select value={exportFilters.tipo} onChange={e => setExportFilters({...exportFilters, tipo: e.target.value})} className="w-full bg-slate-50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.08] rounded-xl px-4 py-2 dark:text-white">
                    <option value="TODOS">Todos</option>
                    <option value="ALUNO">Apenas Alunos</option>
                    <option value="STAFF">Apenas Staff</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-[10px] uppercase tracking-widest text-slate-500 dark:text-white/40 mb-1.5">Dia Específico (Opcional)</label>
                <input type="date" value={exportFilters.data} onChange={e => setExportFilters({...exportFilters, data: e.target.value})} className="w-full bg-slate-50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.08] rounded-xl px-4 py-2 dark:text-white text-sm" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] uppercase tracking-widest text-slate-500 dark:text-white/40 mb-1.5">Turma (Opcional)</label>
                  <input type="text" placeholder="Ex: Turma A" value={exportFilters.turma} onChange={e => setExportFilters({...exportFilters, turma: e.target.value})} className="w-full bg-slate-50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.08] rounded-xl px-4 py-2 dark:text-white text-sm" />
                </div>
                <div>
                  <label className="block text-[10px] uppercase tracking-widest text-slate-500 dark:text-white/40 mb-1.5">Turno (Opcional)</label>
                  <select value={exportFilters.turno} onChange={e => setExportFilters({...exportFilters, turno: e.target.value})} className="w-full bg-slate-50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.08] rounded-xl px-4 py-2 dark:text-white">
                    <option value="">Todos</option>
                    <option value="MANHA">Manhã</option>
                    <option value="TARDE">Tarde</option>
                    <option value="STAFF">Staff</option>
                  </select>
                </div>
              </div>
              <div className="flex gap-3 mt-6">
                <button type="button" onClick={() => setShowExportModal(false)} className="flex-1 py-2.5 bg-slate-100 dark:bg-white/[0.03] rounded-xl dark:text-white/70 text-xs font-semibold">Cancelar</button>
                <button type="submit" disabled={isSubmitting} className="flex-1 py-2.5 bg-[#00B9DE] text-white rounded-xl text-xs font-semibold">Baixar Planilha</button>
              </div>
            </form>
          </div>
        </div>
      )}
"""
content = content.replace('{/* Add Admin Modal */}', export_modal + '\n      {/* Add Admin Modal */}')

with open('web_admin/src/pages/Dashboard.tsx', 'w') as f:
    f.write(content)
