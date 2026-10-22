import React, { useEffect, useState } from 'react';
import { Users2, Plus, Trash2 } from 'lucide-react';
import { listTurmas, createTurma, deleteTurma } from '../../services/api';
import { PageHeader, Card, Input, Button, Alert, EmptyState } from '../../components/ui';

export function TurmasPage() {
  const [turmas, setTurmas] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [nome, setNome] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      setTurmas(await listTurmas());
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!nome.trim()) return;
    setSaving(true);
    setError(null);
    try {
      setTurmas(await createTurma(nome.trim()));
      setNome('');
    } catch (e: any) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  };

  const handleRemove = async (t: string) => {
    if (!confirm(`Remover a turma "${t}"? Alunos já atrelados a ela não são alterados.`)) return;
    setError(null);
    try {
      setTurmas(await deleteTurma(t));
    } catch (e: any) {
      setError(e.message);
    }
  };

  return (
    <>
      <PageHeader eyebrow="Registrar" title="Turmas" description="Cadastre as turmas. Todo aluno precisa ser vinculado a uma turma já cadastrada." />

      <Card className="mt-8 max-w-xl">
        {error && <Alert tone="danger" className="mb-4">{error}</Alert>}

        <form onSubmit={handleAdd} className="mb-6 flex flex-wrap items-end gap-3 rounded-card border border-border/60 p-4">
          <Input label="Nome da turma" placeholder="Ex: Turma 3" value={nome} onChange={(e) => setNome(e.target.value)} wrapperClassName="min-w-[12rem] flex-1" />
          <Button type="submit" loading={saving} disabled={!nome.trim()} iconLeft={<Plus size={14} />}>Cadastrar turma</Button>
        </form>

        {loading ? (
          <div className="space-y-2" aria-hidden="true">
            {[0, 1].map((i) => <div key={i} className="h-10 animate-pulse rounded-lg bg-ink/5" />)}
          </div>
        ) : turmas.length === 0 ? (
          <EmptyState icon={<Users2 size={22} />} title="Nenhuma turma cadastrada" description="Cadastre a primeira turma acima para poder registrar alunos." />
        ) : (
          <ul className="space-y-2">
            {turmas.map((t) => (
              <li key={t} className="flex items-center justify-between gap-3 rounded-lg border border-border/60 p-3">
                <span className="inline-flex items-center gap-2 text-sm font-medium text-text"><Users2 size={16} className="text-primary" /> {t}</span>
                <button type="button" onClick={() => handleRemove(t)} className="rounded-lg p-2 text-muted transition-colors hover:bg-danger/10 hover:text-danger" title={`Remover ${t}`} aria-label={`Remover ${t}`}>
                  <Trash2 size={15} />
                </button>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </>
  );
}
