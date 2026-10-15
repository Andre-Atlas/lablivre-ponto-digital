import { useEffect, useState } from 'react';
import { Save, ClipboardList } from 'lucide-react';
import type { LearningOutcome } from '../../services/api';
import { getPrefill, getProgramConfig, listLearningOutcomes, submitEvaluation } from '../../services/api';
import { useAlunos } from '../../hooks/useAlunos';
import { PageHeader, Card, Select, Textarea, Button, Alert, EmptyState } from '../../components/ui';

const NIVEIS = [1, 2, 3, 4];
const NIVEL_LABEL: Record<number, string> = {
  1: '1 · Iniciante', 2: '2 · Básico', 3: '3 · Intermediário', 4: '4 · Avançado',
};

export function AvaliarPage() {
  const { alunos } = useAlunos();
  const [los, setLos] = useState<LearningOutcome[]>([]);
  const [numSemanas, setNumSemanas] = useState(12);
  const [selected, setSelected] = useState<string>('');
  const [semana, setSemana] = useState<number>(1);
  const [niveis, setNiveis] = useState<Record<string, number>>({});
  const [comentario, setComentario] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [okMsg, setOkMsg] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const [cfg, loList] = await Promise.all([getProgramConfig(), listLearningOutcomes()]);
        setNumSemanas(cfg.num_semanas);
        setSemana(cfg.semana_atual ?? 1);
        setLos(loList);
      } catch (e: any) {
        setError(e.message || 'Não foi possível carregar');
      }
    })();
  }, []);

  // Default the student once the list loads.
  useEffect(() => {
    if (!selected && alunos[0]) setSelected(String(alunos[0].id));
  }, [alunos, selected]);

  useEffect(() => {
    if (!selected) return;
    setLoading(true);
    setError(null);
    setOkMsg(null);
    getPrefill(selected, semana)
      .then((n) => setNiveis({ ...n }))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [selected, semana]);

  const setNivel = (loId: string, nivel: number) => setNiveis((prev) => ({ ...prev, [loId]: nivel }));

  const handleSave = async () => {
    if (!selected) return;
    setSaving(true);
    setError(null);
    setOkMsg(null);
    try {
      await submitEvaluation(selected, semana, niveis, comentario || undefined);
      setOkMsg('Avaliação salva.');
      setComentario('');
    } catch (e: any) {
      setError(e.message || 'Não foi possível salvar');
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <PageHeader
        eyebrow="Avaliação"
        title="Avaliar LOs"
        description="Dê uma nota de 1 a 4 em cada objetivo de aprendizagem (LO) do aluno na semana selecionada."
        actions={<Button onClick={handleSave} loading={saving} disabled={!selected || los.length === 0} iconLeft={<Save size={14} />}>Salvar avaliação</Button>}
      />

      <Card className="mt-8">
        <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Select label="Aluno" value={selected} onChange={(e) => setSelected(e.target.value)}>
            {alunos.length === 0 && <option value="">Nenhum aluno</option>}
            {alunos.map((a) => <option key={String(a.id)} value={String(a.id)}>{a.nome}</option>)}
          </Select>
          <Select label="Semana" value={semana} onChange={(e) => setSemana(Number(e.target.value))}>
            {Array.from({ length: numSemanas }, (_, i) => i + 1).map((w) => <option key={w} value={w}>Semana {w}</option>)}
          </Select>
        </div>

        {error && <Alert tone="danger" className="mb-4">{error}</Alert>}
        {okMsg && <Alert tone="success" className="mb-4">{okMsg}</Alert>}

        {loading ? (
          <div className="space-y-2" aria-hidden="true">
            {[0, 1, 2].map((i) => <div key={i} className="h-10 animate-pulse rounded-lg bg-ink/5" />)}
          </div>
        ) : los.length === 0 ? (
          <EmptyState icon={<ClipboardList size={22} />} title="Nenhum LO para avaliar" description="Cadastre objetivos de aprendizagem em Cadastro › LOs antes de avaliar." />
        ) : (
          <div className="mb-6 space-y-2">
            {los.map((lo) => (
              <div key={lo.id} className="flex items-center justify-between gap-3 rounded-lg border border-border/60 p-2.5">
                <span className="truncate text-sm text-text"><span className="mr-1 text-muted">LO{lo.numero}</span> {lo.nome}</span>
                <select
                  aria-label={`Nível de ${lo.nome}`}
                  value={niveis[lo.id] ?? ''}
                  onChange={(e) => setNivel(lo.id, Number(e.target.value))}
                  className="rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text focus:border-primary focus:outline-none"
                >
                  <option value="">—</option>
                  {NIVEIS.map((n) => <option key={n} value={n}>{NIVEL_LABEL[n]}</option>)}
                </select>
              </div>
            ))}
          </div>
        )}

        <Textarea label="Comentário (opcional)" value={comentario} onChange={(e) => setComentario(e.target.value)} rows={3} placeholder="Ex: evoluiu bem em análise de dados, precisa praticar versionamento." />
      </Card>
    </>
  );
}
