import re

with open("web_admin/src/pages/Login.tsx", "r") as f:
    login_content = f.read()

downloads_html = """
        {/* Downloads da Tela Inicial */}
        <div className="absolute top-6 left-1/2 -translate-x-1/2 sm:left-auto sm:-translate-x-0 sm:right-6 flex flex-row gap-3 z-50">
          <a 
            href="https://github.com/Andre-Atlas/lablivre-ponto-digital/releases/latest" 
            target="_blank" 
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center gap-2 px-4 py-2 bg-white/40 hover:bg-white/80 dark:bg-black/20 dark:hover:bg-black/50 backdrop-blur-md text-[#D12A6A] font-medium tracking-wide text-[10px] sm:text-[11px] uppercase rounded-xl border border-[#D12A6A]/20 shadow-sm transition-all"
          >
            Client (Win)
          </a>
          <a 
            href="https://github.com/Andre-Atlas/lablivre-ponto-digital/releases/latest" 
            target="_blank" 
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center gap-2 px-4 py-2 bg-white/40 hover:bg-white/80 dark:bg-black/20 dark:hover:bg-black/50 backdrop-blur-md text-[#D12A6A] font-medium tracking-wide text-[10px] sm:text-[11px] uppercase rounded-xl border border-[#D12A6A]/20 shadow-sm transition-all"
          >
            Client (Mac)
          </a>
          <a 
            href="https://github.com/Andre-Atlas/lablivre-ponto-digital/releases/latest" 
            target="_blank" 
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center gap-2 px-4 py-2 bg-white/40 hover:bg-white/80 dark:bg-black/20 dark:hover:bg-black/50 backdrop-blur-md text-[#D12A6A] font-medium tracking-wide text-[10px] sm:text-[11px] uppercase rounded-xl border border-[#D12A6A]/20 shadow-sm transition-all"
          >
            Client (Linux)
          </a>
        </div>
"""
if "Downloads da Tela Inicial" not in login_content:
    login_content = login_content.replace('<div className="relative min-h-screen flex items-center justify-center overflow-hidden">', '<div className="relative min-h-screen flex items-center justify-center overflow-hidden">\n' + downloads_html)

with open("web_admin/src/pages/Login.tsx", "w") as f:
    f.write(login_content)
