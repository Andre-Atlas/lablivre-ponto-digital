import re

with open("web_admin/src/pages/Dashboard.tsx", "r") as f:
    content = f.read()

# The badge I added earlier starts at:
# {user.tipo === 'ALUNO' ? ( ... ) : (user.role === 'SUPER_ADMIN' ? ( ...
# We want to replace it with the clean version.

old_badge_regex = r"\{user\.tipo === 'ALUNO' \? \([\s\S]*?\)\}\)\)}"
new_badge = """                        <span className="inline-flex items-center px-2.5 py-1 rounded-md bg-slate-100 dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.05] text-slate-600 dark:text-white/60 text-[10px] font-medium tracking-wider uppercase transition-colors">
                          {user.tipo === 'ALUNO' ? 'ALUNO' : (user.role && user.role !== 'STAFF' ? user.role.replace('_', ' ') : 'STAFF')}
                        </span>"""

content = re.sub(old_badge_regex, new_badge, content)

with open("web_admin/src/pages/Dashboard.tsx", "w") as f:
    f.write(content)
