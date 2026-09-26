const API_URL = 'http://127.0.0.1:8000/api/v1';

export interface User {
  id: string | number;
  nome: string;
  email: string;
  tipo: string;
  admin_aprovado: boolean;
}

const getAuthHeaders = () => ({
  'Authorization': `Bearer ${localStorage.getItem('token')}`,
  'Content-Type': 'application/json'
});

export const fetchUsers = async (): Promise<User[]> => {
  const res = await fetch(`${API_URL}/admin/usuarios`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error('Failed to fetch users');
  return res.json();
};

export const approveUser = async (id: string | number): Promise<void> => {
  const res = await fetch(`${API_URL}/admin/usuarios/${id}/aprovar`, {
    method: 'POST',
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error('Failed to approve user');
};

export const deleteUser = async (id: string | number): Promise<void> => {
  const res = await fetch(`${API_URL}/admin/usuarios/${id}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error('Failed to delete user');
};
