with open("web_admin/src/pages/Dashboard.tsx", "r") as f:
    content = f.read()

linux_button = """
            <a 
              href="https://github.com/Andre-Atlas/lablivre-ponto-digital/releases/latest" 
              target="_blank" 
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-white/10 hover:bg-white/20 border border-white/20 rounded-xl transition-all font-medium text-sm backdrop-blur-sm"
            >
              <Download size={16} /> Baixar Client (Linux)
            </a>"""
            
if "Baixar Client (Linux)" not in content:
    content = content.replace("Baixar Client (Windows)\n            </a>", "Baixar Client (Windows)\n            </a>" + linux_button)

with open("web_admin/src/pages/Dashboard.tsx", "w") as f:
    f.write(content)
