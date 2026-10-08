with open("web_admin/src/pages/Dashboard.tsx", "r") as f:
    content = f.read()

start_str = "                        {user.tipo === 'ALUNO' ? ("
end_str = "                        )))}"

if start_str in content and end_str in content:
    start_idx = content.find(start_str)
    end_idx = content.find(end_str) + len(end_str)
    
    new_badge = """                        <span className="inline-flex items-center px-2.5 py-1 rounded-md bg-slate-100 dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.05] text-slate-600 dark:text-white/60 text-[10px] font-medium tracking-wider uppercase transition-colors">
                          {user.tipo === 'ALUNO' ? 'ALUNO' : (user.role && user.role !== 'STAFF' ? user.role.replace('_', ' ') : 'STAFF')}
                        </span>"""
    
    content = content[:start_idx] + new_badge + content[end_idx:]

with open("web_admin/src/pages/Dashboard.tsx", "w") as f:
    f.write(content)
