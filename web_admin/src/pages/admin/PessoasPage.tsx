import React, { useEffect, useState } from 'react';
import { Users, Search, Trash2, Briefcase, GraduationCap, CheckSquare, Edit3, ArrowRightLeft, UserMinus, UserCheck } from 'lucide-react';
import type { User } from '../../services/api';
import {
  API_URL, fetchUsers, approveUser, deleteUser, updateRole,
  listTurmas, getMentorTurmas, setMentorTurmas as apiSetMentorTurmas, setAlunoStatus,
} from '../../services/api';
import { PageHeader, Card, Badge, Table, Modal, Button, Input, Select, EmptyState } from '../../components/ui';

export function PessoasPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [viewTab, setViewTab] = useState<'STAFF' | 'ALUNO'>('STAFF');
  const [showPopup, setShowPopup] = useState<{ visible: boolean; userId: string | number | null; userName: string }>({ visible: false, userId: null, userName: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedUsers, setSelectedUsers] = useState<Set<any>>(new Set());
  const [showEditUser, setShowEditUser] = useState<any>(null);
  const [allTurmas, setAllTurmas] = useState<string[]>([]);
  const [mentorTurmasSel, setMentorTurmasSel] = useState<string[]>([]);

  useEffect(() => {
    if (showEditUser && showEditUser.tipo !== 'ALUNO') {
      listTurmas().then(setAllTurmas).catch(() => {});
      getMentorTurmas(showEditUser.id).then(setMentorTurmasSel).catch(() => setMentorTurmasSel([]));
    }
  }, [showEditUser]);

  const loadUsers = async () => {
    try {
      setUsers(await fetchUsers());
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadUsers(); }, []);

  const handlePromote = async (id: string | number, currentRole: string) => {
    const newRole = currentRole === 'SUPER_ADMIN' ? 'ADMIN' : (currentRole === 'ADMIN' ? 'SUPER_ADMIN' : 'ADMIN');
    if (!window.confirm(`Alterar o cargo desta pessoa para ${newRole}?`)) return;
    try {
      await updateRole(id, newRole);
      loadUsers();
    } catch (e: any) {
      alert(e.message);
    }
  };

  const confirmApprove = async () => {
    if (!showPopup.userId) return;
    try {
      await approveUser(showPopup.userId);
      setUsers(users.map((u) => (u.id === showPopup.userId ? { ...u, admin_aprovado: true } : u)));
    } catch (err) {
      console.error(err);
    } finally {
      setShowPopup({ visible: false, userId: null, userName: '' });
    }
  };

  const handleToggleStatus = async (u: User) => {
    const novo = u.status === 'DESLIGADO' ? 'ATIVO' : 'DESLIGADO';
    try {
      await setAlunoStatus(u.id, novo);
      loadUsers();
    } catch (e: any) {
      alert(e.message);
    }
  };

  const handleDelete = async (id: string | number, nome: string) => {
    if (!confirm(`Excluir ${nome}? Esta ação não pode ser desfeita.`)) return;
    try {
      await deleteUser(id);
      setUsers(users.filter((u) => u.id !== id));
    } catch (err: any) {
      alert(err.message || 'Não foi possível excluir a pessoa.');
    }
  };

  const handleBulkAprovar = async () => {
    if (selectedUsers.size === 0) return;
    setIsSubmitting(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API_URL}/api/v1/admin/usuarios/bulk-aprovar`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_ids: Array.from(selectedUsers) }),
      });
      if (!res.ok) throw new Error('Não foi possível aprovar');
      fetchUsers();
      setSelectedUsers(new Set());
    } catch (e) {
      console.error(e);
      alert('Não foi possível autorizar as pessoas selecionadas.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEditUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!showEditUser) return;
    setIsSubmitting(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API_URL}/api/v1/admin/usuarios/${showEditUser.id}`, {
        method: 'PUT',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ turma_ou_equipe: showEditUser.turma_ou_equipe, patrimonio: showEditUser.patrimonio, tipo: showEditUser.tipo }),
      });
      if (!res.ok) throw new Error('Não foi possível editar');
      if (showEditUser.tipo !== 'ALUNO') {
        await apiSetMentorTurmas(showEditUser.id, mentorTurmasSel);
      }
      await loadUsers();
      setShowEditUser(null);
    } catch (e) {
      console.error(e);
      alert('Não foi possível salvar as alterações.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const filteredUsers = users.filter((u) => {
    const isAluno = u.tipo === 'ALUNO';
    const matchTab = viewTab === 'ALUNO' ? isAluno : !isAluno;
    const matchSearch = u.nome.toLowerCase().includes(search.toLowerCase()) || u.email.toLowerCase().includes(search.toLowerCase());
    return matchTab && matchSearch;
  });

  const allSelected = selectedUsers.size > 0 && selectedUsers.size === filteredUsers.length;
  const toggleRow = (id: any, checked: boolean) => {
    const next = new Set(selectedUsers);
    if (checked) next.add(id); else next.delete(id);
    setSelectedUsers(next);
  };

  return (
    <>
      <PageHeader eyebrow="Controle de acesso" title="Pessoas" description="Libere acessos e gerencie a equipe e os alunos." />

      {/* Toolbar */}
      <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="inline-flex rounded-lg border border-border/60 bg-surface p-1">
          <button type="button" onClick={() => setViewTab('STAFF')} aria-pressed={viewTab === 'STAFF'}
            className={`inline-flex items-center gap-1.5 rounded-md px-4 py-1.5 text-xs font-semibold transition-colors ${viewTab === 'STAFF' ? 'bg-primary text-white' : 'text-muted hover:text-ink'}`}>
            <Briefcase size={14} /> Staff / Admin
          </button>
          <button type="button" onClick={() => setViewTab('ALUNO')} aria-pressed={viewTab === 'ALUNO'}
            className={`inline-flex items-center gap-1.5 rounded-md px-4 py-1.5 text-xs font-semibold transition-colors ${viewTab === 'ALUNO' ? 'bg-primary text-white' : 'text-muted hover:text-ink'}`}>
            <GraduationCap size={14} /> Alunos
          </button>
        </div>
        <div className="relative w-full sm:w-64">
          <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted" size={16} />
          <input type="text" aria-label="Buscar por nome ou e-mail" placeholder="Buscar por nome ou e-mail..." value={search} onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-lg border border-border bg-surface py-2.5 pl-10 pr-4 text-sm text-text placeholder-muted transition-colors focus:border-primary focus:outline-none" />
        </div>
      </div>

      {/* Bulk bar */}
      {selectedUsers.size > 0 && (
        <div className="mt-6 flex flex-col items-start justify-between gap-3 rounded-card border border-primary/20 bg-primary/5 p-4 sm:flex-row sm:items-center">
          <span className="inline-flex items-center gap-2 text-sm font-semibold text-primary">
            <CheckSquare size={18} /> {selectedUsers.size} {selectedUsers.size === 1 ? 'pessoa selecionada' : 'pessoas selecionadas'}
          </span>
          <div className="flex gap-3">
            <Button size="sm" onClick={handleBulkAprovar} loading={isSubmitting}>Autorizar selecionadas</Button>
          </div>
        </div>
      )}

      <Card padding="none" className="mt-6 overflow-hidden">
        {loading ? (
          <div className="flex justify-center py-32"><span className="h-8 w-8 animate-spin rounded-full border-2 border-border border-t-primary" /></div>
        ) : (
          <Table
            columns={[
              {
                key: 'select', width: '3rem',
                header: <input type="checkbox" aria-label="Selecionar todos" checked={allSelected}
                  onChange={(e) => setSelectedUsers(e.target.checked ? new Set(filteredUsers.map((u) => u.id)) : new Set())} className="accent-primary" />,
                render: (u) => <input type="checkbox" aria-label={`Selecionar ${u.nome}`} checked={selectedUsers.has(u.id)} onChange={(e) => toggleRow(u.id, e.target.checked)} className="accent-primary" />,
              },
              { key: 'colaborador', header: 'Colaborador', render: (u) => (<div><div className="font-semibold text-ink">{u.nome}</div><div className="text-xs text-muted">{u.email}</div></div>) },
              { key: 'funcao', header: 'Função', render: (u) => <Badge tone={u.tipo === 'ALUNO' ? 'primary' : 'neutral'}>{u.tipo === 'ALUNO' ? 'ALUNO' : (u.role && u.role !== 'STAFF' ? u.role.replace('_', ' ') : 'STAFF')}</Badge> },
              {
                key: 'status', header: 'Status',
                render: (u) => (u.tipo === 'ALUNO'
                  ? (u.status === 'DESLIGADO' ? <Badge tone="neutral">Desligado</Badge> : <Badge tone="success">Ativo</Badge>)
                  : (u.admin_aprovado ? <Badge tone="success">Aprovado</Badge> : <Badge tone="accent">Pendente</Badge>)),
              },
              {
                key: 'acao', header: 'Ações', align: 'right',
                render: (u) => (
                  <div className="flex items-center justify-end gap-1.5">
                    {!u.admin_aprovado && <Button size="sm" variant="ghost" onClick={() => setShowPopup({ visible: true, userId: u.id, userName: u.nome })}>Autorizar</Button>}
                    {u.tipo !== 'ALUNO' && <button type="button" onClick={() => handlePromote(u.id, u.role || 'STAFF')} className="rounded-lg p-2 text-muted transition-colors hover:bg-primary/10 hover:text-primary" title="Alterar cargo" aria-label={`Alterar cargo de ${u.nome}`}><ArrowRightLeft size={16} /></button>}
                    {u.tipo === 'ALUNO' && (
                      <button type="button" onClick={() => handleToggleStatus(u)}
                        className={`rounded-lg p-2 transition-colors ${u.status === 'DESLIGADO' ? 'text-success-dark hover:bg-success/10' : 'text-muted hover:bg-accent/10 hover:text-accent-darker'}`}
                        title={u.status === 'DESLIGADO' ? 'Reativar aluno' : 'Desligar aluno'}
                        aria-label={`${u.status === 'DESLIGADO' ? 'Reativar' : 'Desligar'} ${u.nome}`}>
                        {u.status === 'DESLIGADO' ? <UserCheck size={16} /> : <UserMinus size={16} />}
                      </button>
                    )}
                    <button type="button" onClick={() => setShowEditUser(u)} className="rounded-lg p-2 text-muted transition-colors hover:bg-primary/10 hover:text-primary" title="Editar" aria-label={`Editar ${u.nome}`}><Edit3 size={16} /></button>
                    <button type="button" onClick={() => handleDelete(u.id, u.nome)} className="rounded-lg p-2 text-muted transition-colors hover:bg-danger/10 hover:text-danger" title="Excluir" aria-label={`Excluir ${u.nome}`}><Trash2 size={16} /></button>
                  </div>
                ),
              },
            ]}
            data={filteredUsers}
            rowKey={(u) => u.id}
            stickyHeader
            empty={<EmptyState icon={<Users size={22} />} title="Nenhuma pessoa encontrada" description="Ajuste a busca ou troque o filtro entre equipe e alunos." />}
          />
        )}
      </Card>

      {/* Approve */}
      <Modal open={showPopup.visible} onClose={() => setShowPopup({ visible: false, userId: null, userName: '' })} title="Autorizar acesso" size="sm"
        footer={<><Button variant="ghost" onClick={() => setShowPopup({ visible: false, userId: null, userName: '' })}>Cancelar</Button><Button onClick={confirmApprove}>Autorizar</Button></>}>
        <p className="text-sm text-text"><span className="font-semibold text-ink">{showPopup.userName}</span> poderá registrar ponto após a autorização.</p>
      </Modal>

      {/* Editar */}
      <Modal open={!!showEditUser} onClose={() => setShowEditUser(null)} title="Editar pessoa" size="sm"
        footer={<><Button variant="ghost" onClick={() => setShowEditUser(null)}>Cancelar</Button><Button form="form-edit-user" type="submit" loading={isSubmitting}>Salvar</Button></>}>
        {showEditUser && (
          <form id="form-edit-user" onSubmit={handleEditUser} className="space-y-4">
            <Input label="Turma" value={showEditUser.turma_ou_equipe || ''} onChange={(e) => setShowEditUser({ ...showEditUser, turma_ou_equipe: e.target.value })} />
            <Input label="Máquina (patrimônio)" value={showEditUser.patrimonio || ''} onChange={(e) => setShowEditUser({ ...showEditUser, patrimonio: e.target.value })} />
            <Select label="Tipo" value={showEditUser.tipo || 'ALUNO'} onChange={(e) => setShowEditUser({ ...showEditUser, tipo: e.target.value })}>
              <option value="ALUNO">Aluno</option>
              <option value="STAFF">Staff</option>
              <option value="ADMIN">Admin</option>
            </Select>

            {showEditUser.tipo !== 'ALUNO' && (
              <div className="flex flex-col gap-1.5">
                <span className="eyebrow">Turmas do mentor</span>
                {allTurmas.length === 0 ? (
                  <p className="text-xs text-muted">Nenhuma turma cadastrada.</p>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {allTurmas.map((t) => {
                      const on = mentorTurmasSel.includes(t);
                      return (
                        <label key={t} className={`inline-flex cursor-pointer items-center gap-1.5 rounded-pill border px-3 py-1 text-xs font-semibold transition-colors ${on ? 'border-primary bg-primary/10 text-primary' : 'border-border text-muted hover:text-ink'}`}>
                          <input
                            type="checkbox"
                            className="accent-primary"
                            checked={on}
                            onChange={(e) => setMentorTurmasSel((p) => (e.target.checked ? [...p, t] : p.filter((x) => x !== t)))}
                          />
                          {t}
                        </label>
                      );
                    })}
                  </div>
                )}
                <p className="text-xs text-muted">O mentor só lança frequência/avaliações das turmas marcadas.</p>
              </div>
            )}
          </form>
        )}
      </Modal>
    </>
  );
}
