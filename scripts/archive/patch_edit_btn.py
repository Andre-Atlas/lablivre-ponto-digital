import re

with open('web_admin/src/pages/Dashboard.tsx', 'r') as f:
    content = f.read()

btn_edit = """
                          <button onClick={() => setShowEditUser(user)} className="text-slate-400 hover:text-blue-500 dark:text-white/20 dark:hover:text-blue-400 transition-colors" title="Editar Usuário">
                            <Edit3 size={16} />
                          </button>
                          <button 
"""

content = content.replace(
    '<button \n                            onClick={() => handleDelete(user.id)}',
    btn_edit + '                            onClick={() => handleDelete(user.id)}'
)
with open('web_admin/src/pages/Dashboard.tsx', 'w') as f:
    f.write(content)
