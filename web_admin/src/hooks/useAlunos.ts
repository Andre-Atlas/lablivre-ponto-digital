import { useEffect, useState } from 'react';
import { fetchUsers } from '../services/api';

export interface AlunoOption {
  id: string | number;
  nome: string;
  turma?: string;
}

/** Fetches the user list and returns just the students (ALUNO), for dropdowns. */
export function useAlunos(): { alunos: AlunoOption[]; loading: boolean; error: string | null } {
  const [alunos, setAlunos] = useState<AlunoOption[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    fetchUsers()
      .then((users) => {
        if (!active) return;
        setAlunos(users.filter((u) => u.tipo === 'ALUNO').map((u) => ({ id: u.id, nome: u.nome, turma: u.turma_ou_equipe })));
      })
      .catch((e) => active && setError(e.message || 'Não foi possível carregar alunos'))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, []);

  return { alunos, loading, error };
}
