with open("web_admin/src/pages/Dashboard.tsx", "r") as f:
    content = f.read()

old_usuarios_btn = 'className="flex-1 sm:flex-none inline-flex items-center justify-center gap-2 px-3 py-2.5 bg-white/50 hover:bg-white dark:bg-white/[0.03] dark:hover:bg-white/[0.08] text-slate-600 dark:text-white/70 hover:text-slate-900 dark:hover:text-white font-medium tracking-wide text-[11px] uppercase rounded-xl border border-slate-200 dark:border-white/[0.08] shadow-sm transition-all active:scale-95"'
new_usuarios_btn = 'className="flex-1 sm:flex-none inline-flex items-center justify-center gap-2 px-3 py-2.5 bg-white/50 hover:bg-white dark:bg-white/[0.03] dark:hover:bg-white/[0.08] text-slate-600 dark:text-white/70 hover:text-slate-900 dark:hover:text-white font-medium tracking-wide text-[11px] uppercase whitespace-nowrap rounded-xl border border-slate-200 dark:border-white/[0.08] shadow-sm transition-all active:scale-95 shrink-0"'

content = content.replace(old_usuarios_btn, new_usuarios_btn)

with open("web_admin/src/pages/Dashboard.tsx", "w") as f:
    f.write(content)
