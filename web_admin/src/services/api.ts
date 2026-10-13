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

// ─────────────────────────── Atestados Médicos ───────────────────────────

export interface JustifiedDay {
  data: string;
  turno: string;
  turno_referencia: string;
  ativo: boolean;
}

export interface Certificate {
  id: string;
  user_id: string;
  user_nome?: string | null;
  periodo_inicio: string;
  periodo_fim: string;
  status: 'ACTIVE' | 'REVOKED';
  dias_justificados: number;
  documento_filename: string;
  documento_content_type: string;
  criado_em: string;
  observacao?: string | null;
  registrado_por?: string | null;
  revogado_por?: string | null;
  revogado_em?: string | null;
  motivo_revogacao?: string | null;
  dias?: JustifiedDay[];
}

const authHeader = (): Record<string, string> => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`,
});

const parseError = async (res: Response, fallback: string): Promise<string> => {
  const data = await res.json().catch(() => ({}));
  if (typeof data.detail === 'string') return data.detail;
  if (Array.isArray(data.detail)) return data.detail.map((d: any) => d.msg).join(', ');
  return fallback;
};

export const recordCertificate = async (
  userId: string,
  periodoInicio: string,
  periodoFim: string,
  documento: File,
  observacao?: string,
): Promise<Certificate> => {
  const form = new FormData();
  form.append('user_id', userId);
  form.append('periodo_inicio', periodoInicio);
  form.append('periodo_fim', periodoFim);
  if (observacao) form.append('observacao', observacao);
  form.append('documento', documento);
  const res = await fetch(`${API_URL}/admin/certificados`, {
    method: 'POST',
    headers: authHeader(),
    body: form,
  });
  if (!res.ok) throw new Error(await parseError(res, 'Falha ao registrar atestado'));
  return res.json();
};

export const listCertificates = async (
  userId?: string,
  status?: 'ACTIVE' | 'REVOKED',
): Promise<Certificate[]> => {
  const params = new URLSearchParams();
  if (userId) params.append('user_id', userId);
  if (status) params.append('status', status);
  const qs = params.toString();
  const res = await fetch(`${API_URL}/admin/certificados${qs ? `?${qs}` : ''}`, {
    headers: authHeader(),
  });
  if (!res.ok) throw new Error(await parseError(res, 'Falha ao listar atestados'));
  return res.json();
};

export const getCertificate = async (id: string): Promise<Certificate> => {
  const res = await fetch(`${API_URL}/admin/certificados/${id}`, { headers: authHeader() });
  if (!res.ok) throw new Error(await parseError(res, 'Falha ao carregar atestado'));
  return res.json();
};

export const openCertificateDocument = async (id: string): Promise<void> => {
  const res = await fetch(`${API_URL}/admin/certificados/${id}/documento`, {
    headers: authHeader(),
  });
  if (!res.ok) throw new Error(await parseError(res, 'Falha ao abrir documento'));
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  window.open(url, '_blank', 'noopener');
  setTimeout(() => URL.revokeObjectURL(url), 60_000);
};

export const revokeCertificate = async (id: string, motivo?: string): Promise<Certificate> => {
  const res = await fetch(`${API_URL}/admin/certificados/${id}/revogar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeader() },
    body: JSON.stringify({ motivo: motivo ?? null }),
  });
  if (!res.ok) throw new Error(await parseError(res, 'Falha ao revogar atestado'));
  return res.json();
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
