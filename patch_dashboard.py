with open("web_admin/src/pages/Dashboard.tsx", "r") as f:
    content = f.read()

download_buttons = """
          {/* Client Downloads */}
          <div className="flex gap-2 w-full mt-4 sm:w-auto">
            <a 
              href="https://github.com/Andre-Atlas/lablivre-ponto-digital/releases/latest" 
              target="_blank" 
              rel="noopener noreferrer"
              className="flex-1 sm:flex-none inline-flex items-center justify-center gap-2 px-3 py-2 bg-white/50 hover:bg-white dark:bg-white/[0.03] dark:hover:bg-white/[0.08] text-slate-600 dark:text-white/70 hover:text-[#00B9DE] dark:hover:text-[#00B9DE] font-medium tracking-wide text-[10px] uppercase rounded-lg border border-slate-200 dark:border-white/[0.08] shadow-sm transition-all active:scale-95 shrink-0"
              title="Baixar para Windows"
            >
              Baixar Client (Windows)
            </a>
            <a 
              href="https://github.com/Andre-Atlas/lablivre-ponto-digital/releases/latest" 
              target="_blank" 
              rel="noopener noreferrer"
              className="flex-1 sm:flex-none inline-flex items-center justify-center gap-2 px-3 py-2 bg-white/50 hover:bg-white dark:bg-white/[0.03] dark:hover:bg-white/[0.08] text-slate-600 dark:text-white/70 hover:text-[#00B9DE] dark:hover:text-[#00B9DE] font-medium tracking-wide text-[10px] uppercase rounded-lg border border-slate-200 dark:border-white/[0.08] shadow-sm transition-all active:scale-95 shrink-0"
              title="Baixar para macOS"
            >
              Baixar Client (Mac)
            </a>
            <a 
              href="https://github.com/Andre-Atlas/lablivre-ponto-digital/releases/latest" 
              target="_blank" 
              rel="noopener noreferrer"
              className="flex-1 sm:flex-none inline-flex items-center justify-center gap-2 px-3 py-2 bg-white/50 hover:bg-white dark:bg-white/[0.03] dark:hover:bg-white/[0.08] text-slate-600 dark:text-white/70 hover:text-[#00B9DE] dark:hover:text-[#00B9DE] font-medium tracking-wide text-[10px] uppercase rounded-lg border border-slate-200 dark:border-white/[0.08] shadow-sm transition-all active:scale-95 shrink-0"
              title="Baixar para Linux"
            >
              Baixar Client (Linux)
            </a>
          </div>
"""

content = content.replace("</p>\n          </div>\n          \n          <div className=\"flex flex-col xl:flex-row", "</p>\n" + download_buttons + "\n          </div>\n          \n          <div className=\"flex flex-col xl:flex-row")

with open("web_admin/src/pages/Dashboard.tsx", "w") as f:
    f.write(content)
