with open('web_admin/src/services/api.ts', 'r') as f:
    content = f.read()

old_create_admin = """export const createAdmin = async (nome: string, email: string): Promise<void> => {
  const res = await fetch(`${API_URL}/admin/usuarios`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}` 
    },
    body: JSON.stringify({ nome, email })
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || 'Failed to create admin');
  }
};"""

new_create_admin = """export const createAdmin = async (nome: string, email: string, senha: string): Promise<void> => {
  const res = await fetch(`${API_URL}/admin/usuarios`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}` 
    },
    body: JSON.stringify({ nome, email, senha })
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const errorMessage = typeof data.detail === 'string' ? data.detail : (Array.isArray(data.detail) ? data.detail.map((d: any) => d.msg).join(', ') : 'Failed to create admin');
    throw new Error(errorMessage);
  }
};"""

content = content.replace(old_create_admin, new_create_admin)
with open('web_admin/src/services/api.ts', 'w') as f:
    f.write(content)


with open('web_admin/src/pages/Dashboard.tsx', 'r') as f:
    content2 = f.read()

content2 = content2.replace(
    "await createAdmin(newAdmin.nome, newAdmin.email);",
    "await createAdmin(newAdmin.nome, newAdmin.email, newAdmin.senha);"
)

with open('web_admin/src/pages/Dashboard.tsx', 'w') as f:
    f.write(content2)
