import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createAdmin } from '../../services/api';
import { PageHeader, Card, Input, Select, Button, Alert } from '../../components/ui';

export function RegistrarAdminPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ nome: '', email: '', senha: '', role: 'STAFF' });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await createAdmin(form.nome, form.email, form.senha, form.role);
      navigate('/pessoas');
    } catch (err: any) {
      setError(err.message || 'Erro ao criar administrador');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <PageHeader eyebrow="Registrar" title="Novo administrador" description="Crie um acesso ao painel para um membro da equipe (staff ou admin)." />
      <Card className="mt-8 max-w-lg">
        {error && <Alert tone="danger" className="mb-4">{error}</Alert>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input label="Nome" required placeholder="João Silva" value={form.nome} onChange={(e) => setForm({ ...form, nome: e.target.value })} />
          <Input label="E-mail" type="email" required placeholder="joao@lablivre.com" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <Select label="Cargo" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
            <option value="STAFF">Staff — apenas registrar ponto</option>
            <option value="ADMIN">Admin — exportar e editar</option>
            <option value="SUPER_ADMIN">Super admin — todos os privilégios</option>
          </Select>
          <Input label="Senha provisória" type="password" required placeholder="••••••••" value={form.senha} onChange={(e) => setForm({ ...form, senha: e.target.value })} />
          <div className="flex gap-3 pt-2">
            <Button type="button" variant="ghost" onClick={() => navigate('/pessoas')}>Cancelar</Button>
            <Button type="submit" loading={submitting} disabled={!form.nome || !form.email || !form.senha}>Criar acesso</Button>
          </div>
        </form>
      </Card>
    </>
  );
}
