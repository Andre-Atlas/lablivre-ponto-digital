with open("web_admin/src/pages/Dashboard.tsx", "r") as f:
    content = f.read()

# Replace the single Pontos button with two buttons
old_pontos_btn = """<button 
                onClick={() => handleExport('checkins', 'pontos_lablivre.csv')}
                className="flex-1 sm:flex-none inline-flex items-center justify-center gap-2 px-3 py-2.5 bg-white/50 hover:bg-white dark:bg-white/[0.03] dark:hover:bg-white/[0.08] text-slate-600 dark:text-white/70 hover:text-slate-900 dark:hover:text-white font-medium tracking-wide text-[11px] uppercase rounded-xl border border-slate-200 dark:border-white/[0.08] shadow-sm transition-all active:scale-95"
                title="Exportar Pontos (CSV)"
              >
                <Download size={14} />
                <span className="hidden sm:inline">Pontos</span>
              </button>"""

new_pontos_btns = """<button 
                onClick={() => handleExport('checkins?tipo=ALUNO', 'pontos_alunos.csv')}
                className="flex-1 sm:flex-none inline-flex items-center justify-center gap-2 px-3 py-2.5 bg-white/50 hover:bg-white dark:bg-white/[0.03] dark:hover:bg-white/[0.08] text-slate-600 dark:text-white/70 hover:text-slate-900 dark:hover:text-white font-medium tracking-wide text-[11px] uppercase rounded-xl border border-slate-200 dark:border-white/[0.08] shadow-sm transition-all active:scale-95"
                title="Exportar Pontos Alunos"
              >
                <Download size={14} />
                <span className="hidden sm:inline">Pontos (Alunos)</span>
              </button>
              <button 
                onClick={() => handleExport('checkins?tipo=STAFF', 'pontos_staff.csv')}
                className="flex-1 sm:flex-none inline-flex items-center justify-center gap-2 px-3 py-2.5 bg-white/50 hover:bg-white dark:bg-white/[0.03] dark:hover:bg-white/[0.08] text-slate-600 dark:text-white/70 hover:text-slate-900 dark:hover:text-white font-medium tracking-wide text-[11px] uppercase rounded-xl border border-slate-200 dark:border-white/[0.08] shadow-sm transition-all active:scale-95"
                title="Exportar Pontos Staff"
              >
                <Download size={14} />
                <span className="hidden sm:inline">Pontos (Staff)</span>
              </button>"""

content = content.replace(old_pontos_btn, new_pontos_btns)

# Add showPassword state to Dashboard
content = content.replace(
    "const [isSubmitting, setIsSubmitting] = useState(false);",
    "const [isSubmitting, setIsSubmitting] = useState(false);\n  const [showPassword, setShowPassword] = useState(false);"
)

# Add Eye, EyeOff to lucide-react imports if not there
if "Eye" not in content:
    content = content.replace("Trash2, Plus, Download } from 'lucide-react';", "Trash2, Plus, Download, Eye, EyeOff } from 'lucide-react';")

# Fix password input in modal
old_password_input = """<input
                  type="password"
                  value={newAdmin.senha}
                  onChange={e => setNewAdmin({ ...newAdmin, senha: e.target.value })}
                  className="w-full px-4 py-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D12A6A]/50 text-slate-900 dark:text-white placeholder-slate-400"
                  placeholder="••••••••"
                  required
                />"""

new_password_input = """<div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    value={newAdmin.senha}
                    onChange={e => setNewAdmin({ ...newAdmin, senha: e.target.value })}
                    className="w-full px-4 py-3 pr-12 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D12A6A]/50 text-slate-900 dark:text-white placeholder-slate-400"
                    placeholder="••••••••"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-4 flex items-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>"""

content = content.replace(old_password_input, new_password_input)

with open("web_admin/src/pages/Dashboard.tsx", "w") as f:
    f.write(content)
