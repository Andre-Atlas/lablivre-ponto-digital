import re

with open("web_admin/src/pages/Login.tsx", "r") as f:
    login_content = f.read()

# Remove the old absolute positioned buttons
downloads_html_old = r"\{/\* Downloads da Tela Inicial \*/\}.*?</div>"
login_content = re.sub(downloads_html_old, "", login_content, flags=re.DOTALL)

# Add them right after the paragraph
new_downloads = """          <p className="text-lg text-slate-600 dark:text-white/50 font-light leading-relaxed max-w-[45ch] transition-colors duration-500">
            Gerencie credenciais, aprove novos colaboradores e monitore o fluxo de ponto do Lab Livre em tempo real.
          </p>

          {/* Downloads da Tela Inicial (Landing Page) */}
          <div className="mt-8">
            <p className="text-xs font-medium text-slate-500 dark:text-white/40 uppercase tracking-widest mb-4">Downloads dos Clients</p>
            <div className="flex flex-wrap gap-3">
              <a 
                href="https://github.com/Andre-Atlas/lablivre-ponto-digital/releases/latest" 
                target="_blank" 
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center px-5 py-2.5 bg-slate-900 hover:bg-slate-800 dark:bg-white dark:hover:bg-white/90 text-white dark:text-slate-900 font-medium tracking-wide text-xs rounded-xl shadow-lg transition-all"
              >
                Client (Windows)
              </a>
              <a 
                href="https://github.com/Andre-Atlas/lablivre-ponto-digital/releases/latest" 
                target="_blank" 
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center px-5 py-2.5 bg-slate-900 hover:bg-slate-800 dark:bg-white dark:hover:bg-white/90 text-white dark:text-slate-900 font-medium tracking-wide text-xs rounded-xl shadow-lg transition-all"
              >
                Client (Mac)
              </a>
              <a 
                href="https://github.com/Andre-Atlas/lablivre-ponto-digital/releases/latest" 
                target="_blank" 
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center px-5 py-2.5 bg-slate-900 hover:bg-slate-800 dark:bg-white dark:hover:bg-white/90 text-white dark:text-slate-900 font-medium tracking-wide text-xs rounded-xl shadow-lg transition-all"
              >
                Client (Linux)
              </a>
            </div>
          </div>"""

# Safely replace
login_content = login_content.replace("""          <p className="text-lg text-slate-600 dark:text-white/50 font-light leading-relaxed max-w-[45ch] transition-colors duration-500">
            Gerencie credenciais, aprove novos colaboradores e monitore o fluxo de ponto do Lab Livre em tempo real.
          </p>""", new_downloads)

with open("web_admin/src/pages/Login.tsx", "w") as f:
    f.write(login_content)
