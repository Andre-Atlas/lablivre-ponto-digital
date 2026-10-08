import re

with open("web_admin/src/pages/Login.tsx", "r") as f:
    content = f.read()

old_class = 'className="inline-flex items-center justify-center px-5 py-2.5 bg-slate-900 hover:bg-slate-800 dark:bg-white dark:hover:bg-white/90 text-white dark:text-slate-900 font-medium tracking-wide text-xs rounded-xl shadow-lg transition-all"'

new_class = 'className="inline-flex items-center justify-center px-5 py-2.5 bg-white/50 hover:bg-white dark:bg-white/[0.03] dark:hover:bg-white/[0.08] text-slate-700 dark:text-white/70 hover:text-[#D12A6A] dark:hover:text-[#D12A6A] border border-slate-200 dark:border-white/[0.08] font-medium tracking-wide text-xs rounded-xl shadow-sm transition-all active:scale-95"'

content = content.replace(old_class, new_class)

with open("web_admin/src/pages/Login.tsx", "w") as f:
    f.write(content)
