import re

with open("web_admin/src/pages/Dashboard.tsx", "r") as f:
    content = f.read()

# 1. Add viewTab state
if "viewTab" not in content:
    content = content.replace("const [search, setSearch] = useState('');", "const [search, setSearch] = useState('');\n  const [viewTab, setViewTab] = useState<'STAFF' | 'ALUNO'>('STAFF');")

# 2. Update filteredUsers
old_filter = """  const filteredUsers = users.filter(u => 
    u.nome.toLowerCase().includes(search.toLowerCase()) || 
    u.email.toLowerCase().includes(search.toLowerCase())
  );"""
new_filter = """  const filteredUsers = users.filter(u => {
    const isAluno = u.tipo === 'ALUNO';
    const matchTab = viewTab === 'ALUNO' ? isAluno : !isAluno;
    const matchSearch = u.nome.toLowerCase().includes(search.toLowerCase()) || u.email.toLowerCase().includes(search.toLowerCase());
    return matchTab && matchSearch;
  });"""
content = content.replace(old_filter, new_filter)

# 3. Add GraduationCap and Briefcase to imports
if "GraduationCap" not in content:
    content = content.replace("EyeOff, Calendar }", "EyeOff, Calendar, GraduationCap, Briefcase }")
elif "GraduationCap" not in content.split("from 'lucide-react'")[0]:
    content = content.replace("EyeOff, Calendar", "EyeOff, Calendar, GraduationCap, Briefcase")

# 4. Add Tab Buttons in UI
tabs_html = """
            <div className="flex bg-white/50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.08] rounded-xl p-1 backdrop-blur-md shadow-[inset_0_1px_3px_rgba(0,0,0,0.02)] dark:shadow-[inset_0_1px_3px_rgba(0,0,0,0.1)] w-full sm:w-auto">
              <button
                onClick={() => setViewTab('STAFF')}
                className={`flex-1 sm:flex-none flex items-center justify-center gap-2 px-4 py-1.5 rounded-lg text-xs font-medium tracking-wide transition-all ${viewTab === 'STAFF' ? 'bg-white dark:bg-white/10 text-slate-800 dark:text-white shadow-sm' : 'text-slate-500 dark:text-white/40 hover:text-slate-700 dark:hover:text-white/70'}`}
              >
                <Briefcase size={14} /> Staff / Admin
              </button>
              <button
                onClick={() => setViewTab('ALUNO')}
                className={`flex-1 sm:flex-none flex items-center justify-center gap-2 px-4 py-1.5 rounded-lg text-xs font-medium tracking-wide transition-all ${viewTab === 'ALUNO' ? 'bg-white dark:bg-white/10 text-slate-800 dark:text-white shadow-sm' : 'text-slate-500 dark:text-white/40 hover:text-slate-700 dark:hover:text-white/70'}`}
              >
                <GraduationCap size={14} /> Alunos
              </button>
            </div>
"""
if "Briefcase size=" not in content:
    content = content.replace('<div className="relative group w-full sm:w-64">', tabs_html + '\n            <div className="relative group w-full sm:w-64">')

# 5. Fix badge for function (indicator visual)
# We want to replace `{user.tipo}` with `{user.tipo !== 'ALUNO' ? user.role || 'STAFF' : 'ALUNO'}`
# Wait, let's use a nice styled badge
old_badge = """                        <span className="inline-flex items-center px-2.5 py-1 rounded-md bg-slate-100 dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.05] text-slate-600 dark:text-white/60 text-[10px] font-medium tracking-wider uppercase transition-colors">
                          {user.tipo}
                        </span>"""

new_badge = """                        {user.tipo === 'ALUNO' ? (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-200 dark:border-indigo-500/20 text-indigo-700 dark:text-indigo-400 text-[10px] font-medium tracking-wider uppercase transition-colors">
                            <GraduationCap size={12} /> ALUNO
                          </span>
                        ) : (user.role === 'SUPER_ADMIN' ? (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 text-amber-700 dark:text-amber-400 text-[10px] font-medium tracking-wider uppercase transition-colors">
                            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                            SUPER ADMIN
                          </span>
                        ) : (user.role === 'ADMIN' ? (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/20 text-blue-700 dark:text-blue-400 text-[10px] font-medium tracking-wider uppercase transition-colors">
                            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                            ADMIN
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-100 dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.05] text-slate-600 dark:text-white/60 text-[10px] font-medium tracking-wider uppercase transition-colors">
                            <Briefcase size={12} /> STAFF
                          </span>
                        )))}"""
content = content.replace(old_badge, new_badge)

# 6. Hide "Promover" from ALUNO
# Actually, if the user list is filtered to ALUNO, they won't see it anyway?
# Wait, the promote button was injected like this:
old_prom_btn = """                        <button
                          onClick={() => handlePromote(user.id, user.role || 'STAFF')}
                          className="p-2 text-indigo-500 hover:bg-indigo-50 dark:hover:bg-indigo-500/10 rounded-xl transition-colors"
                          title="Alterar Cargo (Promover/Rebaixar)"
                        >"""
# Wait, no. I injected:
# className="text-slate-400 hover:text-[#00B9DE] dark:text-white/20 dark:hover:text-[#00B9DE] transition-colors mr-3"
old_prom_btn_2 = """                        <button
                          onClick={() => handlePromote(user.id, user.role || 'STAFF')}
                          className="text-slate-400 hover:text-[#00B9DE] dark:text-white/20 dark:hover:text-[#00B9DE] transition-colors mr-3"
                          title="Alterar Cargo (Promover/Rebaixar)"
                        >"""

new_prom_btn_2 = """                        {user.tipo !== 'ALUNO' && (
                          <button
                            onClick={() => handlePromote(user.id, user.role || 'STAFF')}
                            className="text-slate-400 hover:text-[#00B9DE] dark:text-white/20 dark:hover:text-[#00B9DE] transition-colors mr-3"
                            title="Alterar Cargo (Promover/Rebaixar)"
                          >
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m16 16 4-4-4-4"/><path d="M20 12H4"/></svg>
                          </button>
                        )}
"""
# Replace the button block (since I just want to wrap it)
content = re.sub(r'(<button\s*onClick=\{\(\) => handlePromote\(user.id, user.role \|\| \'STAFF\'\)\}\s*className="text-slate-400 [^>]+>\s*<svg[^>]+><path[^>]+/><path[^>]+/></svg>\s*</button>)', 
    r"{user.tipo !== 'ALUNO' && (\n\1\n)}", content)

with open("web_admin/src/pages/Dashboard.tsx", "w") as f:
    f.write(content)
