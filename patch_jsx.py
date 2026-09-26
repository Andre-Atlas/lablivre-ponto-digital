with open("web_admin/src/pages/Dashboard.tsx", "r") as f:
    content = f.read()

content = content.replace(
    '<span className="hidden sm:inline">Pontos</span>\n              </a>',
    '<span className="hidden sm:inline">Pontos</span>\n              </button>'
)

with open("web_admin/src/pages/Dashboard.tsx", "w") as f:
    f.write(content)
