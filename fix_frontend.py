import re

with open("web_admin/src/pages/Dashboard.tsx", "r") as f:
    dash_content = f.read()

promote_button = """
                        <button
                          onClick={() => handlePromote(user.id, user.role || 'STAFF')}
                          className="text-slate-400 hover:text-[#00B9DE] dark:text-white/20 dark:hover:text-[#00B9DE] transition-colors mr-3"
                          title="Alterar Cargo (Promover/Rebaixar)"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m16 16 4-4-4-4"/><path d="M20 12H4"/></svg>
                        </button>
"""
dash_content = dash_content.replace('<button \n                            onClick={() => handleDelete(user.id)}', promote_button + '<button \n                            onClick={() => handleDelete(user.id)}')

with open("web_admin/src/pages/Dashboard.tsx", "w") as f:
    f.write(dash_content)
