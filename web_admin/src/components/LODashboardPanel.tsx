import { useEffect, useState } from 'react';
import { BarChart3, X, Download, AlertCircle, TrendingDown } from 'lucide-react';
import type { DashboardData } from '../services/api';
import { exportWeeklyReport, getDashboard, getProgramConfig } from '../services/api';

const NIVEL_COLORS = ['#f87171', '#fbbf24', '#38bdf8', '#34d399']; // 1..4

export function LODashboardPanel({ onClose }: { onClose: () => void }) {
  const [turma, setTurma] = useState<string>('Turma 1');
  const [semana, setSemana] = useState<number>(1);
  const [numSemanas, setNumSemanas] = useState(12);
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getProgramConfig()
      .then((cfg) => {
        setNumSemanas(cfg.num_semanas);
        setSemana(cfg.semana_atual ?? 1);
      })
      .catch((e) => setError(e.message));
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

  const field =
    'bg-white dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.08] rounded-xl px-3 py-2 text-sm text-slate-900 dark:text-white focus:outline-none focus:border-[#D12A6A]/50';
  const card = 'p-4 rounded-2xl border border-slate-200 dark:border-white/[0.06] bg-white/50 dark:bg-white/[0.02]';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" role="dialog" aria-modal="true" aria-label="Dashboard de avaliações">
      <div className="absolute inset-0 bg-slate-900/40 dark:bg-black/60 backdrop-blur-sm" onClick={onClose}></div>
      <div className="relative w-full max-w-3xl max-h-[90vh] overflow-y-auto backdrop-blur-[40px] bg-white/90 dark:bg-[#0A0A0A]/80 border border-slate-200 dark:border-white/[0.08] rounded-[2rem] p-8 shadow-[0_24px_48px_rgba(0,0,0,0.1)]">
        <div className="flex items-start justify-between mb-6">
          <h3 className="text-xl font-medium tracking-tight text-slate-900 dark:text-white flex items-center gap-2">
            <BarChart3 size={18} className="text-[#D12A6A]" /> Dashboard de Avaliações
          </h3>
          <button onClick={onClose} aria-label="Fechar" className="text-slate-400 hover:text-slate-900 dark:text-white/40 dark:hover:text-white">
            <X size={20} />
          </button>
        </div>

        <div className="flex flex-wrap items-end gap-3 mb-6">
          <div className="flex-1 min-w-[8rem]">
            <label className="block text-[10px] uppercase tracking-widest text-slate-500 dark:text-white/40 mb-1" htmlFor="db-turma">Turma</label>
            <input id="db-turma" value={turma} onChange={(e) => setTurma(e.target.value)} className={`w-full ${field}`} placeholder="Ex: Turma 1" />
          </div>
          <div className="w-32">
            <label className="block text-[10px] uppercase tracking-widest text-slate-500 dark:text-white/40 mb-1" htmlFor="db-semana">Semana</label>
            <select id="db-semana" value={semana} onChange={(e) => setSemana(Number(e.target.value))} className={`w-full ${field}`}>
              {Array.from({ length: numSemanas }, (_, i) => i + 1).map((w) => <option key={w} value={w}>Semana {w}</option>)}
            </select>
          </div>
          <button
            onClick={() => exportWeeklyReport(turma, semana, 'excel').catch((e) => setError(e.message))}
            disabled={!turma}
            className="inline-flex items-center gap-1.5 py-2 px-4 bg-white/50 hover:bg-white dark:bg-white/[0.03] dark:hover:bg-white/[0.08] text-slate-600 dark:text-white/70 font-medium rounded-xl border border-slate-200 dark:border-white/[0.08] text-xs active:scale-95 disabled:opacity-50"
          >
            <Download size={14} /> Exportar
          </button>
        </div>

        {error && (
          <div className="mb-4 flex items-center gap-2 text-sm text-red-600 dark:text-red-400 bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-2.5">
            <AlertCircle size={16} /> {error}
          </div>
        )}

        {loading ? (
          <div className="h-40 rounded-2xl bg-slate-200/50 dark:bg-white/[0.04] animate-pulse" aria-hidden="true"></div>
        ) : data ? (
          <div className="space-y-5">
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <div className={card}><p className="text-2xl font-medium text-slate-900 dark:text-white">{data.avaliados}/{data.total_alunos}</p><p className="text-xs text-slate-500 dark:text-white/40">Avaliados</p></div>
              <div className={card}><p className="text-2xl font-medium text-slate-900 dark:text-white">{data.pendentes.length}</p><p className="text-xs text-slate-500 dark:text-white/40">Pendentes</p></div>
              <div className={card}><p className="text-2xl font-medium text-slate-900 dark:text-white">{data.regressoes.length}</p><p className="text-xs text-slate-500 dark:text-white/40">Regressões</p></div>
            </div>

            {data.por_mentor.length > 0 && (
              <div className={card}>
                <p className="text-[11px] uppercase tracking-widest text-slate-500 dark:text-white/40 mb-2">Por mentor</p>
                <ul className="text-sm text-slate-700 dark:text-white/70 space-y-1">
                  {data.por_mentor.map((m) => <li key={m.mentor_nome}>{m.mentor_nome}: <b>{m.alunos_avaliados}</b></li>)}
                </ul>
              </div>
            )}

            <div className={card}>
              <p className="text-[11px] uppercase tracking-widest text-slate-500 dark:text-white/40 mb-3">Heatmap (níveis por LO)</p>
              <div className="space-y-1.5">
                {data.heatmap.map((h) => {
                  const total = h.contagem.reduce((a, b) => a + b, 0) || 1;
                  return (
                    <div key={h.lo_id} className="flex items-center gap-2">
                      <span className="text-xs text-slate-500 dark:text-white/40 w-28 truncate">LO{h.numero} {h.nome}</span>
                      <div className="flex-1 flex h-4 rounded overflow-hidden">
                        {h.contagem.map((c, i) => (
                          <div key={i} style={{ width: `${(c / total) * 100}%`, background: NIVEL_COLORS[i] }} title={`Nível ${i + 1}: ${c}`} />
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {data.regressoes.length > 0 && (
              <div className={card}>
                <p className="text-[11px] uppercase tracking-widest text-slate-500 dark:text-white/40 mb-2 flex items-center gap-1">
                  <TrendingDown size={12} className="text-red-500" /> Regressões
                </p>
                <ul className="text-sm text-slate-700 dark:text-white/70 space-y-1">
                  {data.regressoes.map((r, i) => (
                    <li key={i}>{r.nome} — LO{r.numero}: {r.nivel_anterior} → <b className="text-red-500">{r.nivel_atual}</b></li>
                  ))}
                </ul>
              </div>
            )}

            {data.pendentes.length > 0 && (
              <div className={card}>
                <p className="text-[11px] uppercase tracking-widest text-slate-500 dark:text-white/40 mb-2">Pendentes</p>
                <p className="text-sm text-slate-600 dark:text-white/60">{data.pendentes.map((p) => p.nome).join(', ')}</p>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-8 text-slate-400 dark:text-white/30 text-sm">Selecione uma turma e semana.</div>
        )}
      </div>
    </div>
  );
}
