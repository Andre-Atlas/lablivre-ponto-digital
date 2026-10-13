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

// ─────────────────────────── Avaliação de LOs ───────────────────────────

export interface LearningOutcome {
  id: string;
  numero: number;
  nome: string;
  descricao?: string | null;
  ativo: boolean;
  ordem: number;
}

export interface ProgramConfig {
  data_inicio: string | null;
  num_semanas: number;
  semana_atual: number | null;
}

export interface EvaluationLevel {
  lo_id: string;
  numero?: number | null;
  nome?: string | null;
  nivel: number;
  mentor_id?: string | null;
}

export interface EvaluationComment {
  mentor_id?: string | null;
  mentor_nome: string;
  texto: string;
}

export interface Evaluation {
  user_id: string;
  user_nome?: string | null;
  semana: number;
  turma: string;
  niveis: EvaluationLevel[];
  comentarios: EvaluationComment[];
}

export interface DashboardData {
  turma: string;
  semana: number;
  total_alunos: number;
  avaliados: number;
  pendentes: { user_id: string; nome: string }[];
  por_mentor: { mentor_nome: string; alunos_avaliados: number }[];
  heatmap: { lo_id: string; numero: number; nome: string; contagem: number[] }[];
  regressoes: {
    user_id: string; nome: string; lo_id: string; numero: number;
    nivel_atual: number; nivel_anterior: number;
  }[];
}

const authHeaderJson = (): Record<string, string> => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem('token')}`,
});

const parseError = async (res: Response, fallback: string): Promise<string> => {
  const data = await res.json().catch(() => ({}));
  if (typeof data.detail === 'string') return data.detail;
  if (Array.isArray(data.detail)) return data.detail.map((d: any) => d.msg).join(', ');
  return fallback;
};

export const listLearningOutcomes = async (incluirInativos = false): Promise<LearningOutcome[]> => {
  const res = await fetch(`${API_URL}/admin/los?incluir_inativos=${incluirInativos}`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  });
  if (!res.ok) throw new Error(await parseError(res, 'Falha ao listar LOs'));
  return res.json();
};

export const createLearningOutcome = async (
  numero: number, nome: string, descricao?: string,
): Promise<LearningOutcome> => {
  const res = await fetch(`${API_URL}/admin/los`, {
    method: 'POST', headers: authHeaderJson(),
    body: JSON.stringify({ numero, nome, descricao: descricao ?? null }),
  });
  if (!res.ok) throw new Error(await parseError(res, 'Falha ao criar LO'));
  return res.json();
};

export const updateLearningOutcome = async (
  id: string, patch: Partial<Pick<LearningOutcome, 'nome' | 'descricao' | 'ativo' | 'ordem'>>,
): Promise<LearningOutcome> => {
  const res = await fetch(`${API_URL}/admin/los/${id}`, {
    method: 'PUT', headers: authHeaderJson(), body: JSON.stringify(patch),
  });
  if (!res.ok) throw new Error(await parseError(res, 'Falha ao atualizar LO'));
  return res.json();
};

export const getProgramConfig = async (): Promise<ProgramConfig> => {
  const res = await fetch(`${API_URL}/admin/avaliacoes/config`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  });
  if (!res.ok) throw new Error(await parseError(res, 'Falha ao carregar configuração'));
  return res.json();
};

export const getPrefill = async (userId: string, semana: number): Promise<Record<string, number>> => {
  const res = await fetch(`${API_URL}/admin/avaliacoes/prefill?user_id=${userId}&semana=${semana}`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  });
  if (!res.ok) throw new Error(await parseError(res, 'Falha ao carregar níveis anteriores'));
  return (await res.json()).niveis;
};

export const getEvaluation = async (userId: string, semana: number): Promise<Evaluation> => {
  const res = await fetch(`${API_URL}/admin/avaliacoes?user_id=${userId}&semana=${semana}`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  });
  if (!res.ok) throw new Error(await parseError(res, 'Falha ao carregar avaliação'));
  return res.json();
};

export const submitEvaluation = async (
  userId: string, semana: number, niveis: Record<string, number>, comentario?: string,
): Promise<Evaluation> => {
  const res = await fetch(`${API_URL}/admin/avaliacoes`, {
    method: 'POST', headers: authHeaderJson(),
    body: JSON.stringify({ user_id: userId, semana, niveis, comentario: comentario ?? null }),
  });
  if (!res.ok) throw new Error(await parseError(res, 'Falha ao salvar avaliação'));
  return res.json();
};

export const getDashboard = async (turma: string, semana: number): Promise<DashboardData> => {
  const res = await fetch(
    `${API_URL}/admin/avaliacoes/dashboard?turma=${encodeURIComponent(turma)}&semana=${semana}`,
    { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } },
  );
  if (!res.ok) throw new Error(await parseError(res, 'Falha ao carregar dashboard'));
  return res.json();
};

export const exportWeeklyReport = async (
  turma: string, semana: number, formato: 'csv' | 'excel' = 'excel',
): Promise<void> => {
  const res = await fetch(
    `${API_URL}/admin/avaliacoes/export?turma=${encodeURIComponent(turma)}&semana=${semana}&format=${formato}`,
    { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } },
  );
  if (!res.ok) throw new Error(await parseError(res, 'Falha ao exportar'));
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `avaliacoes_${turma}_s${semana}.${formato === 'excel' ? 'xlsx' : 'csv'}`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};
