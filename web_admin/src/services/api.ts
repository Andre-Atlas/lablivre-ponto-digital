export const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1';

export interface User {
  id: string | number;
  nome: string;
  email: string;
  tipo: string;
  role?: string;
  admin_aprovado: boolean;
}

export const fetchUsers = async (): Promise<User[]> => {
  const res = await fetch(`${API_URL}/admin/usuarios`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
  });
  if (!res.ok) throw new Error('Failed to fetch users');
  return res.json();
};

export const approveUser = async (id: string | number): Promise<void> => {
  const res = await fetch(`${API_URL}/admin/usuarios/${id}/aprovar`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
  });
  if (!res.ok) throw new Error('Failed to approve user');
};

export const adminLogin = async (email: string, password: string): Promise<{ access_token: string }> => {
  const res = await fetch(`${API_URL}/auth/admin-login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  if (!res.ok) throw new Error('Login failed');
  return res.json();
};

export const createAdmin = async (nome: string, email: string, senha: string, role: string = "STAFF"): Promise<void> => {
  const res = await fetch(`${API_URL}/admin/usuarios`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}` 
    },
    body: JSON.stringify({ nome, email, senha, role })
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const errorMessage = typeof data.detail === 'string' ? data.detail : (Array.isArray(data.detail) ? data.detail.map((d: any) => d.msg).join(', ') : 'Failed to create admin');
    throw new Error(errorMessage);
  }
};

export const deleteUser = async (id: string | number): Promise<void> => {
  const res = await fetch(`${API_URL}/admin/usuarios/${id}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || 'Failed to delete user');
  }
};

export const updateRole = async (id: string | number, role: string): Promise<void> => {
  const res = await fetch(`${API_URL}/admin/usuarios/${id}/role`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
    body: JSON.stringify({ role })
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || 'Failed to update role');
  }
};

export const justificarFalta = async (id: string | number, data: string, turno: string): Promise<void> => {
  const res = await fetch(`${API_URL}/admin/usuarios/${id}/justificar`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}` 
    },
    body: JSON.stringify({ data, turno })
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || 'Falha ao justificar falta');
  }
};
