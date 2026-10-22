import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createStudent, listTurmas } from '../../services/api';
import { PageHeader, Card, Input, Select, Button, Alert } from '../../components/ui';

export function RegistrarAlunoPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ nome: '', email: '', turma: '' });
  const [turmas, setTurmas] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listTurmas()
      .then((t) => {
        setTurmas(t);
        setForm((f) => ({ ...f, turma: f.turma || t[0] || '' }));
      })
      .catch((e) => setError(e.message));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await createStudent(form.nome, form.email, form.turma);
      navigate('/pessoas');
    } catch (err: any) {
      setError(err.message || 'Erro ao registrar aluno');
    } finally {
      setSubmitting(false);
    }
  };

  const noTurmas = turmas.length === 0;

  return (
    <>
      <PageHeader eyebrow="Registrar" title="Registrar aluno" description="O aluno fica vinculado a uma turma e não tem login próprio." />
      <Card className="mt-8 max-w-lg">
        {error && <Alert tone="danger" className="mb-4">{error}</Alert>}
        {noTurmas && (
          <Alert tone="warning" className="mb-4">
            Você ainda não tem turmas. <button type="button" className="font-semibold underline" onClick={() => navigate('/registrar/turma')}>Cadastre uma turma</button> antes de registrar alunos.
          </Alert>
        )}
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input label="Nome" required value={form.nome} onChange={(e) => setForm({ ...form, nome: e.target.value })} />
          <Input label="E-mail" type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <Select label="Turma" required value={form.turma} onChange={(e) => setForm({ ...form, turma: e.target.value })} disabled={noTurmas}>
            {noTurmas && <option value="">Nenhuma turma cadastrada</option>}
            {turmas.map((t) => <option key={t} value={t}>{t}</option>)}
          </Select>
          <div className="flex gap-3 pt-2">
            <Button type="button" variant="ghost" onClick={() => navigate('/pessoas')}>Cancelar</Button>
            <Button type="submit" loading={submitting} disabled={noTurmas || !form.turma}>Registrar aluno</Button>
          </div>
        </form>
      </Card>
    </>
  );
}
