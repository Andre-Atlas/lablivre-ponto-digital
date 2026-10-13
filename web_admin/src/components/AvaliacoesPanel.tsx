import { useEffect, useState } from 'react';
import { ClipboardList, X, Save, AlertCircle } from 'lucide-react';
import type { LearningOutcome } from '../services/api';
import {
  getPrefill,
  getProgramConfig,
  listLearningOutcomes,
  submitEvaluation,
} from '../services/api';

interface AlunoOption {
  id: string | number;
  nome: string;
}

const NIVEIS = [1, 2, 3, 4];
const NIVEL_LABEL: Record<number, string> = {
  1: '1 · Iniciante',
  2: '2 · Básico',
  3: '3 · Intermediário',
  4: '4 · Avançado',
};

export function AvaliacoesPanel({ onClose, alunos }: { onClose: () => void; alunos: AlunoOption[] }) {
  const [los, setLos] = useState<LearningOutcome[]>([]);
  const [numSemanas, setNumSemanas] = useState(12);
  const [selected, setSelected] = useState<string>(alunos[0] ? String(alunos[0].id) : '');
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
        setError(e.message || 'Falha ao carregar');
      }
    })();
  }, []);

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

  const setNivel = (loId: string, nivel: number) =>
    setNiveis((prev) => ({ ...prev, [loId]: nivel }));

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
      setError(e.message || 'Falha ao salvar');
    } finally {
      setSaving(false);
    }
  };

  const field =
    'bg-white dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.08] rounded-xl px-3 py-2 text-sm text-slate-900 dark:text-white focus:outline-none focus:border-[#D12A6A]/50';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" role="dialog" aria-modal="true" aria-label="Avaliação de LOs">
      <div className="absolute inset-0 bg-slate-900/40 dark:bg-black/60 backdrop-blur-sm" onClick={onClose}></div>
      <div className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto backdrop-blur-[40px] bg-white/90 dark:bg-[#0A0A0A]/80 border border-slate-200 dark:border-white/[0.08] rounded-[2rem] p-8 shadow-[0_24px_48px_rgba(0,0,0,0.1)]">
        <div className="relative z-10">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h3 className="text-xl font-medium tracking-tight text-slate-900 dark:text-white flex items-center gap-2">
                <ClipboardList size={18} className="text-[#D12A6A]" /> Avaliação Semanal de LOs
              </h3>
              <p className="text-slate-600 dark:text-white/50 font-light text-sm mt-1">
                Atribua um nível (1–4) por objetivo de aprendizagem para o aluno na semana.
              </p>
            </div>
            <button onClick={onClose} aria-label="Fechar" className="text-slate-400 hover:text-slate-900 dark:text-white/40 dark:hover:text-white">
              <X size={20} />
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-[10px] uppercase tracking-widest text-slate-500 dark:text-white/40 mb-1.5 ml-1" htmlFor="av-aluno">Aluno</label>
              <select id="av-aluno" value={selected} onChange={(e) => setSelected(e.target.value)} className={`w-full ${field}`}>
                {alunos.length === 0 && <option value="">Nenhum aluno</option>}
                {alunos.map((a) => (
                  <option key={String(a.id)} value={String(a.id)}>{a.nome}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-[10px] uppercase tracking-widest text-slate-500 dark:text-white/40 mb-1.5 ml-1" htmlFor="av-semana">Semana</label>
              <select id="av-semana" value={semana} onChange={(e) => setSemana(Number(e.target.value))} className={`w-full ${field}`}>
                {Array.from({ length: numSemanas }, (_, i) => i + 1).map((w) => (
                  <option key={w} value={w}>Semana {w}</option>
                ))}
              </select>
            </div>
          </div>

          {error && (
            <div className="mb-4 flex items-center gap-2 text-sm text-red-600 dark:text-red-400 bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-2.5">
              <AlertCircle size={16} /> {error}
            </div>
          )}
          {okMsg && (
            <div className="mb-4 text-sm text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 rounded-xl px-4 py-2.5">
              {okMsg}
            </div>
          )}

          {loading ? (
            <div className="space-y-2" aria-hidden="true">
              {[0, 1, 2].map((i) => (
                <div key={i} className="h-10 rounded-xl bg-slate-200/50 dark:bg-white/[0.04] animate-pulse"></div>
              ))}
            </div>
          ) : los.length === 0 ? (
            <div className="text-center py-8 text-slate-400 dark:text-white/30 text-sm">
              Nenhum LO cadastrado. Peça a um administrador para cadastrar no Catálogo de LOs.
            </div>
          ) : (
            <div className="space-y-2 mb-6">
              {los.map((lo) => (
                <div key={lo.id} className="flex items-center justify-between gap-3 p-2.5 rounded-xl border border-slate-200 dark:border-white/[0.06]">
                  <span className="text-sm text-slate-800 dark:text-white/80 truncate">
                    <span className="text-slate-400 dark:text-white/30 mr-1">LO{lo.numero}</span> {lo.nome}
                  </span>
                  <select
                    aria-label={`Nível de ${lo.nome}`}
                    value={niveis[lo.id] ?? ''}
                    onChange={(e) => setNivel(lo.id, Number(e.target.value))}
                    className={field}
                  >
                    <option value="">—</option>
                    {NIVEIS.map((n) => (
                      <option key={n} value={n}>{NIVEL_LABEL[n]}</option>
                    ))}
                  </select>
                </div>
              ))}
            </div>
          )}

          <div className="mb-6">
            <label className="block text-[10px] uppercase tracking-widest text-slate-500 dark:text-white/40 mb-1.5 ml-1" htmlFor="av-coment">Comentário (opcional)</label>
            <textarea id="av-coment" value={comentario} onChange={(e) => setComentario(e.target.value)} rows={3} className={`w-full ${field}`} placeholder="Observações qualitativas da semana" />
          </div>

          <button
            onClick={handleSave}
            disabled={saving || !selected || los.length === 0}
            className="inline-flex items-center justify-center gap-2 py-2.5 px-5 bg-[#D12A6A] hover:bg-[#b02259] text-white font-medium rounded-xl shadow-[0_4px_14px_rgba(209,42,106,0.3)] transition-all tracking-wide text-xs active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Save size={14} /> {saving ? 'Salvando...' : 'Salvar Avaliação'}
          </button>
        </div>
      </div>
    </div>
  );
}
