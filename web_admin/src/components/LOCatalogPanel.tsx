import React, { useEffect, useState } from 'react';
import { ListChecks, X, Plus, AlertCircle } from 'lucide-react';
import type { LearningOutcome } from '../services/api';
import { createLearningOutcome, listLearningOutcomes, updateLearningOutcome } from '../services/api';

export function LOCatalogPanel({ onClose }: { onClose: () => void }) {
  const [los, setLos] = useState<LearningOutcome[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [numero, setNumero] = useState('');
  const [nome, setNome] = useState('');
  const [descricao, setDescricao] = useState('');
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

  useEffect(() => {
    load();
  }, []);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!numero || !nome) return;
    setSaving(true);
    setError(null);
    try {
      await createLearningOutcome(Number(numero), nome, descricao || undefined);
      setNumero('');
      setNome('');
      setDescricao('');
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

  const field =
    'bg-white dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.08] rounded-xl px-3 py-2 text-sm text-slate-900 dark:text-white focus:outline-none focus:border-[#D12A6A]/50';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" role="dialog" aria-modal="true" aria-label="Catálogo de LOs">
      <div className="absolute inset-0 bg-slate-900/40 dark:bg-black/60 backdrop-blur-sm" onClick={onClose}></div>
      <div className="relative w-full max-w-xl max-h-[90vh] overflow-y-auto backdrop-blur-[40px] bg-white/90 dark:bg-[#0A0A0A]/80 border border-slate-200 dark:border-white/[0.08] rounded-[2rem] p-8 shadow-[0_24px_48px_rgba(0,0,0,0.1)]">
        <div className="flex items-start justify-between mb-6">
          <h3 className="text-xl font-medium tracking-tight text-slate-900 dark:text-white flex items-center gap-2">
            <ListChecks size={18} className="text-[#00B9DE]" /> Catálogo de Learning Outcomes
          </h3>
          <button onClick={onClose} aria-label="Fechar" className="text-slate-400 hover:text-slate-900 dark:text-white/40 dark:hover:text-white">
            <X size={20} />
          </button>
        </div>

        {error && (
          <div className="mb-4 flex items-center gap-2 text-sm text-red-600 dark:text-red-400 bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-2.5">
            <AlertCircle size={16} /> {error}
          </div>
        )}

        <form onSubmit={handleAdd} className="flex flex-wrap items-end gap-2 mb-6 p-4 rounded-2xl border border-slate-200 dark:border-white/[0.08]">
          <div className="w-16">
            <label className="block text-[10px] uppercase tracking-widest text-slate-500 dark:text-white/40 mb-1" htmlFor="lo-num">Nº</label>
            <input id="lo-num" type="number" min={1} value={numero} onChange={(e) => setNumero(e.target.value)} className={`w-full ${field}`} />
          </div>
          <div className="flex-1 min-w-[10rem]">
            <label className="block text-[10px] uppercase tracking-widest text-slate-500 dark:text-white/40 mb-1" htmlFor="lo-nome">Nome</label>
            <input id="lo-nome" value={nome} onChange={(e) => setNome(e.target.value)} className={`w-full ${field}`} />
          </div>
          <button type="submit" disabled={saving || !numero || !nome} className="inline-flex items-center gap-1.5 py-2 px-4 bg-[#00B9DE] hover:bg-[#009bbd] text-white font-medium rounded-xl text-xs active:scale-95 disabled:opacity-50">
            <Plus size={14} /> Adicionar
          </button>
        </form>

        {loading ? (
          <div className="space-y-2" aria-hidden="true">
            {[0, 1, 2].map((i) => <div key={i} className="h-10 rounded-xl bg-slate-200/50 dark:bg-white/[0.04] animate-pulse"></div>)}
          </div>
        ) : los.length === 0 ? (
          <div className="text-center py-8 text-slate-400 dark:text-white/30 text-sm">Nenhum LO cadastrado.</div>
        ) : (
          <ul className="space-y-2">
            {los.map((lo) => (
              <li key={lo.id} className="flex items-center justify-between gap-3 p-3 rounded-xl border border-slate-200 dark:border-white/[0.06]">
                <span className={`text-sm ${lo.ativo ? 'text-slate-800 dark:text-white/80' : 'text-slate-400 dark:text-white/30 line-through'}`}>
                  <span className="text-slate-400 dark:text-white/30 mr-1">LO{lo.numero}</span> {lo.nome}
                </span>
                <button
                  onClick={() => toggleAtivo(lo)}
                  className="text-[11px] px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-white/[0.08] text-slate-600 dark:text-white/60 hover:text-[#D12A6A]"
                >
                  {lo.ativo ? 'Desativar' : 'Reativar'}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
