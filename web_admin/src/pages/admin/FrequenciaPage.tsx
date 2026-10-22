import { useEffect, useState } from 'react';
import { Save, Check, X, Eye, Ban, Paperclip, Users } from 'lucide-react';
import type { AlunoFrequencia } from '../../services/api';
import {
  getFrequencia, lancarFrequencia, anexarAtestadoFrequencia,
  removerAtestadoFrequencia, baixarAtestadoFrequencia, getFrequenciaTurmas,
} from '../../services/api';
import { PageHeader, Card, Select, Input, Button, Badge, Alert, EmptyState } from '../../components/ui';

type Marca = 'PRESENTE' | 'FALTA';
const hoje = () => new Date().toISOString().split('T')[0];

export function FrequenciaPage() {
  const [turmas, setTurmas] = useState<string[]>([]);
  const [turma, setTurma] = useState('');
  const [data, setData] = useState(hoje());
  const [turno, setTurno] = useState('MANHA');
  const [rows, setRows] = useState<AlunoFrequencia[]>([]);
  const [marks, setMarks] = useState<Record<string, Marca>>({});
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [okMsg, setOkMsg] = useState<string | null>(null);

  useEffect(() => {
    getFrequenciaTurmas().then((t) => { setTurmas(t); setTurma((c) => c || t[0] || ''); }).catch((e) => setError(e.message));
  }, []);

  const carregar = async () => {
    if (!turma || !data || !turno) return;
    setLoading(true);
    setError(null);
    setOkMsg(null);
    try {
      const r = await getFrequencia(turma, data, turno);
      setRows(r);
      setMarks(Object.fromEntries(r.filter((x) => x.status).map((x) => [x.aluno_id, x.status === 'PRESENTE' ? 'PRESENTE' : 'FALTA'])));
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { carregar(); /* eslint-disable-next-line */ }, [turma, data, turno]);

  const marcar = (id: string, m: Marca) => setMarks((p) => ({ ...p, [id]: m }));

  const salvar = async () => {
    const lancamentos = Object.entries(marks).map(([aluno_id, status]) => ({ aluno_id, status }));
    if (lancamentos.length === 0) return;
    setSaving(true);
    setError(null);
    setOkMsg(null);
    try {
      await lancarFrequencia(turma, data, turno, lancamentos);
      await carregar();
      setOkMsg('Frequência salva.');
    } catch (e: any) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  };

  const anexar = async (freqId: string, file: File | null) => {
    if (!file) return;
    setError(null);
    try {
      await anexarAtestadoFrequencia(freqId, file);
      await carregar();
    } catch (e: any) {
      setError(e.message);
    }
  };

  const remover = async (freqId: string) => {
    setError(null);
    try {
      await removerAtestadoFrequencia(freqId);
      await carregar();
    } catch (e: any) {
      setError(e.message);
    }
  };

  return (
    <>
      <PageHeader
        eyebrow="Frequência"
        title="Lançar frequência"
        description="Marque presença ou falta de cada aluno da turma na data e turno. Faltas podem ter atestado anexado."
        actions={<Button onClick={salvar} loading={saving} disabled={!turma || Object.keys(marks).length === 0} iconLeft={<Save size={14} />}>Salvar frequência</Button>}
      />

      <Card className="mt-8">
        <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <Select label="Turma" value={turma} onChange={(e) => setTurma(e.target.value)}>
            {turmas.length === 0 && <option value="">Nenhuma turma</option>}
            {turmas.map((t) => <option key={t} value={t}>{t}</option>)}
          </Select>
          <Input label="Data" type="date" value={data} onChange={(e) => setData(e.target.value)} />
          <Select label="Turno" value={turno} onChange={(e) => setTurno(e.target.value)}>
            <option value="MANHA">Manhã</option>
            <option value="TARDE">Tarde</option>
          </Select>
        </div>

        {error && <Alert tone="danger" className="mb-4">{error}</Alert>}
        {okMsg && <Alert tone="success" className="mb-4">{okMsg}</Alert>}

        {loading ? (
          <div className="space-y-2" aria-hidden="true">
            {[0, 1, 2].map((i) => <div key={i} className="h-12 animate-pulse rounded-lg bg-ink/5" />)}
          </div>
        ) : rows.length === 0 ? (
          <EmptyState icon={<Users size={22} />} title="Nenhum aluno ativo" description="Não há alunos ativos nesta turma para lançar frequência." />
        ) : (
          <ul className="divide-y divide-border/50">
            {rows.map((r) => {
              const marca = marks[r.aluno_id];
              return (
                <li key={r.aluno_id} className="flex flex-wrap items-center justify-between gap-3 py-3">
                  <span className="min-w-0 flex-1 truncate text-sm font-medium text-ink">{r.aluno_nome}</span>

                  <div className="flex items-center gap-2">
                    {/* Segmented Presente/Falta */}
                    <div className="inline-flex overflow-hidden rounded-lg border border-border">
                      <button
                        type="button"
                        aria-pressed={marca === 'PRESENTE'}
                        onClick={() => marcar(r.aluno_id, 'PRESENTE')}
                        className={`inline-flex items-center gap-1 px-3 py-1.5 text-xs font-semibold transition-colors ${marca === 'PRESENTE' ? 'bg-success text-white' : 'text-muted hover:bg-success/10'}`}
                      >
                        <Check size={13} /> Presente
                      </button>
                      <button
                        type="button"
                        aria-pressed={marca === 'FALTA'}
                        onClick={() => marcar(r.aluno_id, 'FALTA')}
                        className={`inline-flex items-center gap-1 border-l border-border px-3 py-1.5 text-xs font-semibold transition-colors ${marca === 'FALTA' ? 'bg-danger text-white' : 'text-muted hover:bg-danger/10'}`}
                      >
                        <X size={13} /> Falta
                      </button>
                    </div>

                    {/* Estado salvo + atestado (apenas em faltas já lançadas) */}
                    {r.status === 'JUSTIFICADO' && <Badge tone="success">Justificado</Badge>}
                    {r.freq_id && r.status !== 'PRESENTE' && r.status && (
                      r.tem_atestado ? (
                        <div className="flex items-center gap-1">
                          <button type="button" onClick={() => baixarAtestadoFrequencia(r.freq_id!).catch((e) => setError(e.message))} title="Ver atestado" aria-label={`Ver atestado de ${r.aluno_nome}`} className="rounded-lg border border-border/60 p-1.5 text-muted hover:text-primary">
                            <Eye size={14} />
                          </button>
                          <button type="button" onClick={() => remover(r.freq_id!)} title="Remover atestado" aria-label={`Remover atestado de ${r.aluno_nome}`} className="rounded-lg border border-border/60 p-1.5 text-muted hover:text-danger">
                            <Ban size={14} />
                          </button>
                        </div>
                      ) : (
                        <label className="inline-flex cursor-pointer items-center gap-1 rounded-lg border border-border/60 px-2.5 py-1.5 text-xs font-semibold text-muted hover:text-primary" title="Anexar atestado">
                          <Paperclip size={13} /> Atestado
                          <input type="file" accept="application/pdf,image/jpeg,image/png" className="hidden" onChange={(e) => anexar(r.freq_id!, e.target.files?.[0] ?? null)} />
                        </label>
                      )
                    )}
                  </div>
                </li>
              );
            })}
          </ul>
        )}
        {rows.length > 0 && (
          <p className="mt-4 text-xs text-muted">Atestados podem ser anexados às faltas após salvar a frequência.</p>
        )}
      </Card>
    </>
  );
}
