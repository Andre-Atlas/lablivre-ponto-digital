import re

with open("web_admin/src/pages/Dashboard.tsx", "r") as f:
    content = f.read()

# Add download helper functions inside the Dashboard component
# Just before the handleApprove definition
helper_funcs = """
  const handleExport = async (endpoint: string, filename: string) => {
    try {
      const res = await fetch(`${API_URL}/admin/export/${endpoint}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!res.ok) throw new Error('Falha ao exportar');
      
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert("Erro ao exportar arquivo.");
    }
  };

  const handleApprove"""

content = content.replace("  const handleApprove", helper_funcs)

# Replace the anchor tags with buttons
content = content.replace(
    """<a 
                href={`${API_URL}/admin/export/checkins`}
                target="_blank"
                rel="noreferrer"
                className="flex-1 sm:flex-none inline-flex items-center justify-center gap-2 px-3 py-2.5 bg-white/50 hover:bg-white dark:bg-white/[0.03] dark:hover:bg-white/[0.08] text-slate-600 dark:text-white/70 hover:text-slate-900 dark:hover:text-white font-medium tracking-wide text-[11px] uppercase rounded-xl border border-slate-200 dark:border-white/[0.08] shadow-sm transition-all active:scale-95"
                title="Exportar Pontos (CSV)"
              >""",
    """<button 
                onClick={() => handleExport('checkins', 'pontos_lablivre.csv')}
                className="flex-1 sm:flex-none inline-flex items-center justify-center gap-2 px-3 py-2.5 bg-white/50 hover:bg-white dark:bg-white/[0.03] dark:hover:bg-white/[0.08] text-slate-600 dark:text-white/70 hover:text-slate-900 dark:hover:text-white font-medium tracking-wide text-[11px] uppercase rounded-xl border border-slate-200 dark:border-white/[0.08] shadow-sm transition-all active:scale-95"
                title="Exportar Pontos (CSV)"
              >"""
)
content = content.replace("</button> // replacing old </a> for checkins below", "")

# We need a precise regex or simple replace for the closing tags.
# Actually, let's just do a string replace for the whole <a> block for checkins
old_checkins_a = """<a 
                href={`${API_URL}/admin/export/checkins`}
                target="_blank"
                rel="noreferrer"
                className="flex-1 sm:flex-none inline-flex items-center justify-center gap-2 px-3 py-2.5 bg-white/50 hover:bg-white dark:bg-white/[0.03] dark:hover:bg-white/[0.08] text-slate-600 dark:text-white/70 hover:text-slate-900 dark:hover:text-white font-medium tracking-wide text-[11px] uppercase rounded-xl border border-slate-200 dark:border-white/[0.08] shadow-sm transition-all active:scale-95"
                title="Exportar Pontos (CSV)"
              >
                <Download size={14} />
                <span className="hidden sm:inline">Pontos</span>
              </a>"""

new_checkins_btn = """<button 
                onClick={() => handleExport('checkins', 'pontos_lablivre.csv')}
                className="flex-1 sm:flex-none inline-flex items-center justify-center gap-2 px-3 py-2.5 bg-white/50 hover:bg-white dark:bg-white/[0.03] dark:hover:bg-white/[0.08] text-slate-600 dark:text-white/70 hover:text-slate-900 dark:hover:text-white font-medium tracking-wide text-[11px] uppercase rounded-xl border border-slate-200 dark:border-white/[0.08] shadow-sm transition-all active:scale-95"
                title="Exportar Pontos (CSV)"
              >
                <Download size={14} />
                <span className="hidden sm:inline">Pontos</span>
              </button>"""

old_usuarios_a = """<a 
                href={`${API_URL}/admin/export/usuarios`}
                target="_blank"
                rel="noreferrer"
                className="flex-1 sm:flex-none inline-flex items-center justify-center gap-2 px-3 py-2.5 bg-white/50 hover:bg-white dark:bg-white/[0.03] dark:hover:bg-white/[0.08] text-slate-600 dark:text-white/70 hover:text-slate-900 dark:hover:text-white font-medium tracking-wide text-[11px] uppercase rounded-xl border border-slate-200 dark:border-white/[0.08] shadow-sm transition-all active:scale-95"
                title="Exportar Usuários (CSV)"
              >
                <Download size={14} />
                <span className="hidden sm:inline">Usuários</span>
              </a>"""

new_usuarios_btn = """<button 
                onClick={() => handleExport('usuarios', 'usuarios_lablivre.csv')}
                className="flex-1 sm:flex-none inline-flex items-center justify-center gap-2 px-3 py-2.5 bg-white/50 hover:bg-white dark:bg-white/[0.03] dark:hover:bg-white/[0.08] text-slate-600 dark:text-white/70 hover:text-slate-900 dark:hover:text-white font-medium tracking-wide text-[11px] uppercase rounded-xl border border-slate-200 dark:border-white/[0.08] shadow-sm transition-all active:scale-95"
                title="Exportar Usuários (CSV)"
              >
                <Download size={14} />
                <span className="hidden sm:inline">Usuários</span>
              </button>"""

content = content.replace(old_checkins_a, new_checkins_btn)
content = content.replace(old_usuarios_a, new_usuarios_btn)

with open("web_admin/src/pages/Dashboard.tsx", "w") as f:
    f.write(content)
