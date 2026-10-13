import React, { useEffect, useState } from 'react';
import { FileText, X, Upload, Eye, Ban, Calendar, AlertCircle } from 'lucide-react';
import type { Certificate } from '../services/api';
import {
  listCertificates,
  recordCertificate,
  openCertificateDocument,
  revokeCertificate,
} from '../services/api';

interface AlunoOption {
  id: string | number;
  nome: string;
}

export function CertificadosPanel({
  onClose,
  alunos,
}: {
  onClose: () => void;
  alunos: AlunoOption[];
}) {
  const [selected, setSelected] = useState<string>(alunos[0] ? String(alunos[0].id) : '');
  const [certs, setCerts] = useState<Certificate[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [revokingId, setRevokingId] = useState<string | null>(null);
  const [inicio, setInicio] = useState('');
  const [fim, setFim] = useState('');
  const [observacao, setObservacao] = useState('');
  const [file, setFile] = useState<File | null>(null);

  const loadCerts = async (alunoId: string) => {
    if (!alunoId) {
      setCerts([]);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      setCerts(await listCertificates(alunoId));
    } catch (e: any) {
      setError(e.message || 'Falha ao carregar atestados');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCerts(selected);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selected]);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selected || !file || !inicio || !fim) return;
    setSubmitting(true);
    setError(null);
    try {
      await recordCertificate(selected, inicio, fim, file, observacao || undefined);
      setInicio('');
      setFim('');
      setObservacao('');
      setFile(null);
      await loadCerts(selected);
    } catch (e: any) {
      setError(e.message || 'Falha ao registrar atestado');
    } finally {
      setSubmitting(false);
    }
  };

  const handleRevoke = async (id: string) => {
    setSubmitting(true);
    setError(null);
    try {
      await revokeCertificate(id);
      await loadCerts(selected);
    } catch (e: any) {
      setError(e.message || 'Falha ao revogar atestado');
    } finally {
      setSubmitting(false);
      setRevokingId(null);
    }
  };

  const fieldCls =
    'w-full bg-white dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.08] rounded-xl px-4 py-2.5 focus:outline-none focus:border-[#D12A6A]/50 focus:bg-white dark:focus:bg-white/[0.05] transition-all font-light text-sm text-slate-900 dark:text-white';
  const labelCls =
    'block text-[10px] uppercase tracking-widest text-slate-500 dark:text-white/40 mb-1.5 ml-1';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" role="dialog" aria-modal="true" aria-label="Atestados médicos">
      <div
        className="absolute inset-0 bg-slate-900/40 dark:bg-black/60 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      ></div>

      <div className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto backdrop-blur-[40px] bg-white/90 dark:bg-[#0A0A0A]/80 border border-slate-200 dark:border-white/[0.08] rounded-[2rem] p-8 shadow-[0_24px_48px_rgba(0,0,0,0.1)] dark:shadow-[inset_0_1px_0_rgba(255,255,255,0.1),0_24px_48px_rgba(0,0,0,0.6)] animate-in fade-in zoom-in-95 duration-200">
        <div className="absolute -top-24 -right-24 w-48 h-48 bg-[#00B9DE]/10 dark:bg-[#00B9DE]/20 rounded-full blur-[60px] pointer-events-none mix-blend-multiply dark:mix-blend-screen"></div>

        <div className="relative z-10">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h3 className="text-xl font-medium tracking-tight text-slate-900 dark:text-white flex items-center gap-2">
                <FileText size={18} className="text-[#D12A6A]" /> Atestados Médicos
              </h3>
              <p className="text-slate-600 dark:text-white/50 font-light text-sm mt-1">
                Registre atestados e justifique faltas de um aluno.
              </p>
            </div>
            <button
              onClick={onClose}
              aria-label="Fechar"
              className="text-slate-400 hover:text-slate-900 dark:text-white/40 dark:hover:text-white transition-colors"
            >
              <X size={20} />
            </button>
          </div>

          <div className="mb-6">
            <label className={labelCls} htmlFor="aluno-select">Aluno</label>
            <select
              id="aluno-select"
              value={selected}
              onChange={(e) => setSelected(e.target.value)}
              className={fieldCls}
            >
              {alunos.length === 0 && <option value="">Nenhum aluno disponível</option>}
              {alunos.map((a) => (
                <option key={String(a.id)} value={String(a.id)}>
                  {a.nome}
                </option>
              ))}
            </select>
          </div>

          {error && (
            <div className="mb-4 flex items-center gap-2 text-sm text-red-600 dark:text-red-400 bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-2.5">
              <AlertCircle size={16} /> {error}
            </div>
          )}

          {/* Novo atestado */}
          <form onSubmit={handleUpload} className="mb-8 p-5 rounded-2xl border border-slate-200 dark:border-white/[0.08] bg-white/40 dark:bg-white/[0.02]">
            <p className="text-[11px] uppercase tracking-widest text-slate-500 dark:text-white/40 mb-4">Novo Atestado</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
              <div>
                <label className={labelCls} htmlFor="cert-inicio">Início</label>
                <input id="cert-inicio" type="date" required value={inicio} onChange={(e) => setInicio(e.target.value)} className={fieldCls} />
              </div>
              <div>
                <label className={labelCls} htmlFor="cert-fim">Fim</label>
                <input id="cert-fim" type="date" required value={fim} onChange={(e) => setFim(e.target.value)} className={fieldCls} />
              </div>
            </div>
            <div className="mb-4">
              <label className={labelCls} htmlFor="cert-obs">Observação (opcional)</label>
              <input id="cert-obs" type="text" value={observacao} onChange={(e) => setObservacao(e.target.value)} className={fieldCls} placeholder="Ex: 5 dias de repouso" />
            </div>
            <div className="mb-4">
              <label className={labelCls} htmlFor="cert-file">Documento (PDF, JPEG ou PNG — até 10 MB)</label>
              <input
                id="cert-file"
                type="file"
                accept="application/pdf,image/jpeg,image/png"
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                className="w-full text-sm text-slate-600 dark:text-white/60 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-medium file:bg-[#D12A6A]/10 file:text-[#D12A6A] hover:file:bg-[#D12A6A]/20"
              />
            </div>
            <button
              type="submit"
              disabled={submitting || !selected || !file || !inicio || !fim}
              className="inline-flex items-center justify-center gap-2 py-2.5 px-5 bg-[#D12A6A] hover:bg-[#b02259] text-white font-medium rounded-xl shadow-[0_4px_14px_rgba(209,42,106,0.3)] transition-all tracking-wide text-xs active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Upload size={14} /> {submitting ? 'Enviando...' : 'Registrar Atestado'}
            </button>
          </form>

          {/* Lista de atestados */}
          <div>
            <p className="text-[11px] uppercase tracking-widest text-slate-500 dark:text-white/40 mb-4">Atestados do Aluno</p>
            {loading ? (
              <div className="space-y-3" aria-hidden="true">
                {[0, 1].map((i) => (
                  <div key={i} className="h-16 rounded-2xl bg-slate-200/50 dark:bg-white/[0.04] animate-pulse"></div>
                ))}
              </div>
            ) : certs.length === 0 ? (
              <div className="text-center py-8 text-slate-400 dark:text-white/30 text-sm">
                <FileText size={28} className="mx-auto mb-2 opacity-40" />
                Nenhum atestado registrado para este aluno.
              </div>
            ) : (
              <ul className="space-y-3">
                {certs.map((c) => (
                  <li
                    key={c.id}
                    className="flex items-center justify-between gap-4 p-4 rounded-2xl border border-slate-200 dark:border-white/[0.08] bg-white/50 dark:bg-white/[0.02]"
                  >
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 text-sm text-slate-900 dark:text-white">
                        <Calendar size={14} className="text-[#00B9DE] shrink-0" />
                        <span className="truncate">
                          {c.periodo_inicio} → {c.periodo_fim}
                        </span>
                        <span
                          className={`text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full ${
                            c.status === 'ACTIVE'
                              ? 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400'
                              : 'bg-slate-500/15 text-slate-500 dark:text-white/40'
                          }`}
                        >
                          {c.status === 'ACTIVE' ? 'Ativo' : 'Revogado'}
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 dark:text-white/40 mt-1">
                        {c.dias_justificados} dia(s) justificado(s)
                        {c.observacao ? ` · ${c.observacao}` : ''}
                      </p>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <button
                        onClick={() => openCertificateDocument(c.id).catch((e) => setError(e.message))}
                        title="Ver documento"
                        aria-label="Ver documento"
                        className="p-2 rounded-lg bg-white/60 dark:bg-white/[0.04] border border-slate-200 dark:border-white/[0.08] text-slate-600 dark:text-white/60 hover:text-[#00B9DE] transition-colors"
                      >
                        <Eye size={15} />
                      </button>
                      {c.status === 'ACTIVE' &&
                        (revokingId === c.id ? (
                          <div className="flex items-center gap-1">
                            <button
                              onClick={() => handleRevoke(c.id)}
                              disabled={submitting}
                              className="text-[11px] px-2 py-1.5 rounded-lg bg-red-500 text-white disabled:opacity-50"
                            >
                              Confirmar
                            </button>
                            <button
                              onClick={() => setRevokingId(null)}
                              className="text-[11px] px-2 py-1.5 rounded-lg bg-slate-100 dark:bg-white/[0.06] text-slate-600 dark:text-white/60"
                            >
                              Não
                            </button>
                          </div>
                        ) : (
                          <button
                            onClick={() => setRevokingId(c.id)}
                            title="Revogar atestado"
                            aria-label="Revogar atestado"
                            className="p-2 rounded-lg bg-white/60 dark:bg-white/[0.04] border border-slate-200 dark:border-white/[0.08] text-slate-600 dark:text-white/60 hover:text-red-500 transition-colors"
                          >
                            <Ban size={15} />
                          </button>
                        ))}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
