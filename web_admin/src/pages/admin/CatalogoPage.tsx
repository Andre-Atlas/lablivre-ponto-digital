import React, { useEffect, useState } from 'react';
import { ListChecks, Plus } from 'lucide-react';
import type { LearningOutcome } from '../../services/api';
import { createLearningOutcome, listLearningOutcomes, updateLearningOutcome } from '../../services/api';
import { PageHeader, Card, Input, Button, Alert, EmptyState } from '../../components/ui';

export function CatalogoPage() {
  const [los, setLos] = useState<LearningOutcome[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [numero, setNumero] = useState('');
  const [nome, setNome] = useState('');
  const [saving, setSaving] = useState(false);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      setLos(await listLearningOutcomes(true));
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!numero || !nome) return;
    setSaving(true);
    setError(null);
    try {
      await createLearningOutcome(Number(numero), nome);
      setNumero('');
      setNome('');
      await load();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  };

  const toggleAtivo = async (lo: LearningOutcome) => {
    setError(null);
    try {
      await updateLearningOutcome(lo.id, { ativo: !lo.ativo });
      await load();
    } catch (e: any) {
      setError(e.message);
    }
  };

  return (
    <>
      <PageHeader eyebrow="Cadastro" title="Catálogo de LOs" description="Cadastre e organize os objetivos de aprendizagem (LOs) avaliados na turma." />

      <Card className="mt-8">
        {error && <Alert tone="danger" className="mb-4">{error}</Alert>}

        <form onSubmit={handleAdd} className="mb-6 flex flex-wrap items-end gap-3 rounded-card border border-border/60 p-4">
          <Input label="Nº" type="number" min={1} value={numero} onChange={(e) => setNumero(e.target.value)} wrapperClassName="w-20" />
          <Input label="Nome do objetivo" placeholder="Ex: Versionamento com Git" value={nome} onChange={(e) => setNome(e.target.value)} wrapperClassName="min-w-[10rem] flex-1" />
          <Button type="submit" loading={saving} disabled={!numero || !nome} iconLeft={<Plus size={14} />}>Adicionar LO</Button>
        </form>

        {loading ? (
          <div className="space-y-2" aria-hidden="true">
            {[0, 1, 2].map((i) => <div key={i} className="h-10 animate-pulse rounded-lg bg-ink/5" />)}
          </div>
        ) : los.length === 0 ? (
          <EmptyState icon={<ListChecks size={22} />} title="Nenhum LO cadastrado" description="Adicione o primeiro objetivo de aprendizagem no formulário acima." />
        ) : (
          <ul className="space-y-2">
            {los.map((lo) => (
              <li key={lo.id} className="flex items-center justify-between gap-3 rounded-lg border border-border/60 p-3">
                <span className={`text-sm ${lo.ativo ? 'text-text' : 'text-muted line-through'}`}>
                  <span className="mr-1 text-muted">LO{lo.numero}</span> {lo.nome}
                </span>
                <Button size="sm" variant="ghost" onClick={() => toggleAtivo(lo)}>{lo.ativo ? 'Desativar' : 'Reativar'}</Button>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </>
  );
}
