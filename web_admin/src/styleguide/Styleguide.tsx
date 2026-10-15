import { useState } from 'react';
import { Plus, Download, Users } from 'lucide-react';
import {
  Button, Card, Input, Textarea, Select, Badge, Table, Modal, Tabs,
  Alert, ToastProvider, useToast, PageHeader, StatCallout, Blob, EmptyState,
} from '../components/ui';

const COLORS = [
  ['primary', 'bg-primary'], ['primary-dark', 'bg-primary-dark'], ['primary-light', 'bg-primary-light'],
  ['accent', 'bg-accent'], ['accent-pink', 'bg-accent-pink'], ['ink', 'bg-ink'],
  ['success', 'bg-success'], ['danger', 'bg-danger'], ['bg', 'bg-bg'], ['peach', 'bg-peach'],
];

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mb-12">
      <h2 className="eyebrow mb-4">{title}</h2>
      <Card>{children}</Card>
    </section>
  );
}

function ToastDemo() {
  const { toast } = useToast();
  return (
    <div className="flex flex-wrap gap-3">
      <Button onClick={() => toast({ tone: 'success', title: 'Salvo', message: 'Avaliação registrada.' })}>Success toast</Button>
      <Button variant="danger" onClick={() => toast({ tone: 'danger', title: 'Erro', message: 'Algo falhou.' })}>Danger toast</Button>
    </div>
  );
}

export function Styleguide() {
  const [modal, setModal] = useState(false);
  const rows = [
    { nome: 'Ana Souza', email: 'ana@lab.dev', status: 'Aprovado' },
    { nome: 'Bruno Lima', email: 'bruno@lab.dev', status: 'Pendente' },
  ];

  return (
    <ToastProvider>
      <div className="min-h-screen bg-bg px-6 py-12">
        <div className="mx-auto max-w-5xl">
          <PageHeader
            eyebrow="Design System"
            title="Lab Livre — Styleguide"
            description="Showcase de tokens e componentes. Rota de desenvolvimento."
            actions={<Button iconLeft={<Plus size={16} />}>Ação</Button>}
          />

          <div className="mt-10" />

          <Section title="Cores">
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
              {COLORS.map(([name, cls]) => (
                <div key={name} className="flex flex-col gap-1.5">
                  <div className={`h-14 rounded-lg border border-border/50 ${cls}`} />
                  <span className="text-xs text-muted">{name}</span>
                </div>
              ))}
            </div>
          </Section>

          <Section title="Tipografia">
            <p className="display mb-2">Display / Poppins</p>
            <h1 className="text-4xl">Heading 1</h1>
            <h2 className="text-2xl">Heading 2</h2>
            <h3 className="text-xl">Heading 3</h3>
            <p className="eyebrow mt-3">Eyebrow / overline</p>
            <p className="mt-2 text-text">Corpo de texto em Inter. The quick brown fox pula sobre o cão.</p>
            <p className="text-sm text-muted">Texto pequeno / secundário.</p>
          </Section>

          <Section title="Botões">
            <div className="flex flex-wrap items-center gap-3">
              <Button>Primary</Button>
              <Button variant="secondary">Secondary</Button>
              <Button variant="ghost">Ghost</Button>
              <Button variant="danger">Danger</Button>
              <Button loading>Loading</Button>
              <Button disabled>Disabled</Button>
              <Button size="sm">Small</Button>
              <Button size="lg" iconRight={<Download size={16} />}>Large</Button>
            </div>
          </Section>

          <Section title="Formulário">
            <div className="grid gap-4 sm:grid-cols-2">
              <Input label="Nome" placeholder="Seu nome" hint="Como aparece na lista" />
              <Input label="E-mail" type="email" error="E-mail inválido" defaultValue="x@" />
              <Select label="Turma" options={[{ value: 'Turma 1', label: 'Turma 1' }, { value: 'Turma 2', label: 'Turma 2' }]} />
              <Textarea label="Comentário" placeholder="Observações" wrapperClassName="sm:col-span-2" />
            </div>
          </Section>

          <Section title="Badges">
            <div className="flex flex-wrap gap-2">
              <Badge tone="neutral">Neutral</Badge>
              <Badge tone="primary">Primary</Badge>
              <Badge tone="success">Aprovado</Badge>
              <Badge tone="accent">Pendente</Badge>
              <Badge tone="danger">Revogado</Badge>
            </div>
          </Section>

          <Section title="Stat callouts">
            <div className="flex flex-wrap gap-10">
              <StatCallout value="1500+" label="Estudantes formados" />
              <StatCallout value="14" tone="accent" label="Anos de pesquisa" />
              <StatCallout value="3" tone="success" label="Programas" />
            </div>
          </Section>

          <Section title="Tabela">
            <Table
              columns={[
                { key: 'nome', header: 'Colaborador' },
                { key: 'email', header: 'E-mail' },
                { key: 'status', header: 'Status', render: (r) => <Badge tone={r.status === 'Aprovado' ? 'success' : 'accent'}>{r.status}</Badge> },
              ]}
              data={rows}
              rowKey={(r) => r.email}
            />
          </Section>

          <Section title="Tabs">
            <Tabs
              tabs={[
                { id: 'a', label: 'Resumo', content: <p className="text-sm text-text">Conteúdo A</p> },
                { id: 'b', label: 'Detalhes', content: <p className="text-sm text-text">Conteúdo B</p> },
              ]}
            />
          </Section>

          <Section title="Alertas & Toasts">
            <div className="flex flex-col gap-3">
              <Alert tone="info" title="Info">Mensagem informativa.</Alert>
              <Alert tone="success" title="Sucesso">Operação concluída.</Alert>
              <Alert tone="danger" title="Erro">Algo deu errado.</Alert>
              <ToastDemo />
            </div>
          </Section>

          <Section title="Modal">
            <Button onClick={() => setModal(true)}>Abrir modal</Button>
            <Modal open={modal} onClose={() => setModal(false)} title="Exemplo" description="Com focus trap e Esc"
              footer={<><Button variant="ghost" onClick={() => setModal(false)}>Cancelar</Button><Button onClick={() => setModal(false)}>Confirmar</Button></>}>
              <Input label="Campo" placeholder="Digite algo" />
            </Modal>
          </Section>

          <Section title="Empty state & Blobs">
            <EmptyState icon={<Users size={22} />} title="Nenhum registro" description="Não há itens para exibir." action={<Button size="sm">Adicionar</Button>} />
            <div className="mt-4 flex gap-4">
              <Blob variant="navy" className="h-16 w-16" />
              <Blob variant="green" className="h-16 w-16" />
              <Blob variant="orange" className="h-16 w-16" />
              <Blob variant="purple-ring" ring className="h-16 w-16" />
            </div>
          </Section>
        </div>
      </div>
    </ToastProvider>
  );
}
