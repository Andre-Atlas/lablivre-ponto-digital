import { useEffect, useState } from 'react';
import { Download, TrendingDown } from 'lucide-react';
import type { DashboardData } from '../../services/api';
import { exportWeeklyReport, getDashboard, getProgramConfig, listTurmas } from '../../services/api';
import { PageHeader, Card, Select, Button, StatCallout, Alert } from '../../components/ui';

const LEVEL_VARS = ['var(--lo-level-1)', 'var(--lo-level-2)', 'var(--lo-level-3)', 'var(--lo-level-4)'];
const NIVEL_LEGEND = ['1 · Iniciante', '2 · Básico', '3 · Intermediário', '4 · Avançado'];

export function LODashboardPage() {
  const [turma, setTurma] = useState<string>('');
  const [turmas, setTurmas] = useState<string[]>([]);
  const [semana, setSemana] = useState<number>(1);
  const [numSemanas, setNumSemanas] = useState(12);
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getProgramConfig()
      .then((cfg) => { setNumSemanas(cfg.num_semanas); setSemana(cfg.semana_atual ?? 1); })
      .catch((e) => setError(e.message));
    listTurmas()
      .then((t) => { setTurmas(t); setTurma((cur) => cur || t[t.length - 1] || ''); })
      .catch(() => {});
  }, []);

  const load = async () => {
    if (!turma) return;
    setLoading(true);
    setError(null);
    try {
      setData(await getDashboard(turma, semana));
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [turma, semana]);

  return (
    <>
      <PageHeader
        eyebrow="Avaliação"
        title="Dashboard de LOs"
        description="Evolução da turma por semana: avaliados, mentores, heatmap e regressões."
        actions={
          <Button variant="ghost" onClick={() => exportWeeklyReport(turma, semana, 'excel').catch((e) => setError(e.message))} disabled={!turma} iconLeft={<Download size={14} />}>Exportar</Button>
        }
      />

      <Card className="mt-8">
        <div className="mb-6 flex flex-wrap items-end gap-3">
          <Select label="Turma" value={turma} onChange={(e) => setTurma(e.target.value)} wrapperClassName="min-w-[10rem] flex-1">
            {turmas.length === 0 && <option value="">Nenhuma turma</option>}
            {turmas.map((t) => <option key={t} value={t}>{t}</option>)}
          </Select>
          <Select label="Semana" value={semana} onChange={(e) => setSemana(Number(e.target.value))} wrapperClassName="w-32">
            {Array.from({ length: numSemanas }, (_, i) => i + 1).map((w) => <option key={w} value={w}>Semana {w}</option>)}
          </Select>
        </div>

        {error && <Alert tone="danger" className="mb-4">{error}</Alert>}

        {loading ? (
          <div className="h-40 animate-pulse rounded-card bg-ink/5" aria-hidden="true" />
        ) : data ? (
          <div className="space-y-5">
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              <Card padding="sm"><StatCallout value={`${data.avaliados}/${data.total_alunos}`} label="Avaliados" /></Card>
              <Card padding="sm"><StatCallout value={data.pendentes.length} tone="accent" label="Pendentes" /></Card>
              <Card padding="sm"><StatCallout value={data.regressoes.length} tone="ink" label="Regressões" /></Card>
            </div>

            {data.por_mentor.length > 0 && (
              <Card padding="sm">
                <p className="eyebrow mb-2">Por mentor</p>
                <ul className="space-y-1 text-sm text-text">
                  {data.por_mentor.map((m) => <li key={m.mentor_nome}>{m.mentor_nome}: <b>{m.alunos_avaliados}</b></li>)}
                </ul>
              </Card>
            )}

            <Card padding="sm">
              <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
                <p className="eyebrow">Heatmap · níveis por LO</p>
                <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
                  {NIVEL_LEGEND.map((l, i) => (
                    <span key={i} className="inline-flex items-center gap-1.5 text-[11px] text-muted">
                      <span className="h-2.5 w-2.5 rounded-sm" style={{ background: LEVEL_VARS[i] }} />
                      {l}
                    </span>
                  ))}
                </div>
              </div>
              <div className="space-y-2">
                {data.heatmap.map((h) => {
                  const avaliados = h.contagem.reduce((a, b) => a + b, 0);
                  const total = avaliados || 1;
                  return (
                    <div key={h.lo_id} className="flex items-center gap-3">
                      <span
                        tabIndex={0}
                        className="group relative w-12 shrink-0 cursor-help text-xs font-bold text-ink focus:outline-none"
                      >
                        LO{h.numero}
                        <span
                          role="tooltip"
                          className="pointer-events-none absolute left-full top-1/2 z-20 ml-2 hidden w-64 -translate-y-1/2 rounded-lg bg-ink px-3 py-2 text-[11px] font-normal leading-snug text-white shadow-pop group-hover:block group-focus:block"
                        >
                          {h.nome}
                        </span>
                      </span>
                      <div className="flex h-5 flex-1 overflow-hidden rounded-md border border-border/50 bg-bg">
                        {h.contagem.map((c, i) =>
                          c > 0 ? (
                            <div
                              key={i}
                              style={{ width: `${(c / total) * 100}%`, background: LEVEL_VARS[i] }}
                              title={`${NIVEL_LEGEND[i]} — ${c} aluno${c === 1 ? '' : 's'}`}
                            />
                          ) : null,
                        )}
                      </div>
                      <span className="w-14 shrink-0 text-right text-[11px] text-muted">
                        {avaliados}/{data.total_alunos}
                      </span>
                    </div>
                  );
                })}
              </div>
            </Card>

            {data.regressoes.length > 0 && (
              <Card padding="sm">
                <p className="eyebrow mb-2 flex items-center gap-1"><TrendingDown size={12} className="text-danger" /> Regressões</p>
                <ul className="space-y-1 text-sm text-text">
                  {data.regressoes.map((r, i) => (
                    <li key={i}>{r.nome} — LO{r.numero}: {r.nivel_anterior} → <b className="text-danger">{r.nivel_atual}</b></li>
                  ))}
                </ul>
              </Card>
            )}

            {data.pendentes.length > 0 && (
              <Card padding="sm">
                <p className="eyebrow mb-2">Pendentes</p>
                <p className="text-sm text-text">{data.pendentes.map((p) => p.nome).join(', ')}</p>
              </Card>
            )}
          </div>
        ) : (
          <p className="py-8 text-center text-sm text-muted">Selecione uma turma e semana.</p>
        )}
      </Card>
    </>
  );
}
