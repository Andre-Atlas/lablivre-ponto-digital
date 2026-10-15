import React, { useEffect, useState } from 'react';
import { FileText, Upload, Eye, Ban, Calendar } from 'lucide-react';
import type { Certificate } from '../../services/api';
import { listCertificates, recordCertificate, openCertificateDocument, revokeCertificate } from '../../services/api';
import { useAlunos } from '../../hooks/useAlunos';
import { PageHeader, Card, Select, Input, Button, Badge, Alert, EmptyState } from '../../components/ui';

export function AtestadosPage() {
  const { alunos } = useAlunos();
  const [selected, setSelected] = useState<string>('');
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
    if (!alunoId) { setCerts([]); return; }
    setLoading(true);
    setError(null);
    try {
      setCerts(await listCertificates(alunoId));
    } catch (e: any) {
      setError(e.message || 'Não foi possível carregar atestados');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!selected && alunos[0]) setSelected(String(alunos[0].id));
  }, [alunos, selected]);

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
      setInicio(''); setFim(''); setObservacao(''); setFile(null);
      await loadCerts(selected);
    } catch (e: any) {
      setError(e.message || 'Não foi possível registrar atestado');
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
      setError(e.message || 'Não foi possível revogar atestado');
    } finally {
      setSubmitting(false);
      setRevokingId(null);
    }
  };

  return (
    <>
      <PageHeader eyebrow="Frequência" title="Atestados médicos" description="Anexe o atestado de um aluno para justificar as faltas do período." />

      <Card className="mt-8">
        <Select label="Aluno" value={selected} onChange={(e) => setSelected(e.target.value)} wrapperClassName="mb-6">
          {alunos.length === 0 && <option value="">Nenhum aluno disponível</option>}
          {alunos.map((a) => <option key={String(a.id)} value={String(a.id)}>{a.nome}</option>)}
        </Select>

        {error && <Alert tone="danger" className="mb-4">{error}</Alert>}

        <form onSubmit={handleUpload} className="mb-8 rounded-card border border-border/60 bg-bg/50 p-5">
          <p className="eyebrow mb-4">Novo atestado</p>
          <div className="mb-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Input label="Início" type="date" required value={inicio} onChange={(e) => setInicio(e.target.value)} />
            <Input label="Fim" type="date" required value={fim} onChange={(e) => setFim(e.target.value)} />
          </div>
          <Input label="Observação (opcional)" value={observacao} onChange={(e) => setObservacao(e.target.value)} placeholder="Ex: 5 dias de repouso" wrapperClassName="mb-4" />
          <div className="mb-4 flex flex-col gap-1.5">
            <label htmlFor="cert-file" className="eyebrow">Documento (PDF, JPEG ou PNG — até 10 MB)</label>
            <input
              id="cert-file"
              type="file"
              accept="application/pdf,image/jpeg,image/png"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              className="w-full text-sm text-text file:mr-4 file:rounded-lg file:border-0 file:bg-primary/10 file:px-4 file:py-2 file:text-xs file:font-semibold file:text-primary hover:file:bg-primary/20"
            />
          </div>
          <Button type="submit" loading={submitting} disabled={!selected || !file || !inicio || !fim} iconLeft={<Upload size={14} />}>Registrar atestado</Button>
        </form>

        <div>
          <p className="eyebrow mb-4">Atestados do aluno</p>
          {loading ? (
            <div className="space-y-3" aria-hidden="true">
              {[0, 1].map((i) => <div key={i} className="h-16 animate-pulse rounded-card bg-ink/5" />)}
            </div>
          ) : certs.length === 0 ? (
            <EmptyState icon={<FileText size={22} />} title="Nenhum atestado registrado" description="Os atestados deste aluno aparecerão aqui." />
          ) : (
            <ul className="space-y-3">
              {certs.map((c) => (
                <li key={c.id} className="flex items-center justify-between gap-4 rounded-card border border-border/60 bg-surface p-4">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 text-sm text-ink">
                      <Calendar size={14} className="shrink-0 text-primary" />
                      <span className="truncate">{c.periodo_inicio} → {c.periodo_fim}</span>
                      <Badge tone={c.status === 'ACTIVE' ? 'success' : 'neutral'}>{c.status === 'ACTIVE' ? 'Ativo' : 'Revogado'}</Badge>
                    </div>
                    <p className="mt-1 text-xs text-muted">{c.dias_justificados} dia(s) justificado(s){c.observacao ? ` · ${c.observacao}` : ''}</p>
                  </div>
                  <div className="flex shrink-0 items-center gap-2">
                    <button
                      type="button"
                      onClick={() => openCertificateDocument(c.id).catch((e) => setError(e.message))}
                      title="Ver documento" aria-label="Ver documento"
                      className="rounded-lg border border-border/60 bg-surface p-2 text-muted transition-colors hover:text-primary"
                    >
                      <Eye size={15} />
                    </button>
                    {c.status === 'ACTIVE' && (revokingId === c.id ? (
                      <div className="flex items-center gap-1">
                        <Button size="sm" variant="danger" onClick={() => handleRevoke(c.id)} loading={submitting}>Revogar</Button>
                        <Button size="sm" variant="ghost" onClick={() => setRevokingId(null)}>Cancelar</Button>
                      </div>
                    ) : (
                      <button
                        type="button"
                        onClick={() => setRevokingId(c.id)}
                        title="Revogar atestado" aria-label="Revogar atestado"
                        className="rounded-lg border border-border/60 bg-surface p-2 text-muted transition-colors hover:text-danger"
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
      </Card>
    </>
  );
}
