import { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LogOut, ChevronDown, Menu as MenuIcon, X, Users, Users2, ClipboardList, BarChart3,
  ListChecks, FileText, Download, GraduationCap, UserPlus,
} from 'lucide-react';
import { LabLivreLogo } from './LabLivreLogo';
import { Menu, MenuItem } from './ui';
import { adminExport } from '../services/api';

const linkBase = 'rounded-lg px-3 py-1.5 text-sm font-semibold transition-colors';
const navLinkCls = ({ isActive }: { isActive: boolean }) =>
  `${linkBase} ${isActive ? 'bg-white/20 text-white' : 'text-white/80 hover:bg-white/10 hover:text-white'}`;

const triggerCls = `${linkBase} inline-flex items-center gap-1 text-white/80 hover:bg-white/10 hover:text-white`;

function doExport(endpoint: string, filename: string) {
  adminExport(endpoint, filename).catch(() => alert('Erro ao exportar arquivo.'));
}

export function AdminNavbar({ onLogout }: { onLogout: () => void }) {
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const go = (path: string) => navigate(path);

  return (
    <header className="sticky top-0 z-30 bg-primary text-white shadow-sm">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between gap-4 px-6 lg:px-8">
        <div className="flex items-center gap-6">
          <NavLink to="/avaliacoes/dashboard" aria-label="Início"><LabLivreLogo variant="light" className="w-20" /></NavLink>

          {/* Desktop nav */}
          <nav className="hidden items-center gap-1 lg:flex" aria-label="Navegação principal">
            <NavLink to="/avaliacoes/dashboard" className={navLinkCls}>Dashboard</NavLink>
            <NavLink to="/pessoas" className={navLinkCls}>Pessoas</NavLink>
            <NavLink to="/avaliacoes/avaliar" className={navLinkCls}>Avaliação</NavLink>
            <NavLink to="/atestados" className={navLinkCls}>Atestados</NavLink>

            <Menu triggerClassName={triggerCls} label={<>Cadastro <ChevronDown size={14} /></>}>
              {(close) => (
                <>
                  <MenuItem icon={<Users2 size={15} />} onClick={() => { go('/registrar/turma'); close(); }}>Turma</MenuItem>
                  <MenuItem icon={<GraduationCap size={15} />} onClick={() => { go('/registrar/aluno'); close(); }}>Aluno</MenuItem>
                  <MenuItem icon={<ListChecks size={15} />} onClick={() => { go('/avaliacoes/catalogo'); close(); }}>LOs</MenuItem>
                  <MenuItem icon={<UserPlus size={15} />} onClick={() => { go('/registrar/admin'); close(); }}>Novo admin</MenuItem>
                </>
              )}
            </Menu>

            <Menu triggerClassName={triggerCls} label={<>Exportar <ChevronDown size={14} /></>}>
              {(close) => (
                <>
                  <MenuItem icon={<Download size={15} />} onClick={() => { doExport('checkins?tipo=ALUNO', 'pontos_alunos.csv'); close(); }}>Pontos (Alunos)</MenuItem>
                  <MenuItem icon={<Download size={15} />} onClick={() => { doExport('checkins?tipo=STAFF', 'pontos_staff.csv'); close(); }}>Pontos (Staff)</MenuItem>
                  <MenuItem icon={<Download size={15} />} onClick={() => { doExport('usuarios', 'usuarios_lablivre.csv'); close(); }}>Usuários</MenuItem>
                </>
              )}
            </Menu>
          </nav>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onLogout}
            className="hidden items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-semibold text-white/90 transition-colors hover:bg-white/10 hover:text-white lg:inline-flex"
          >
            Sair <LogOut size={16} />
          </button>
          {/* Mobile toggle */}
          <button
            type="button"
            className="rounded-lg p-2 text-white hover:bg-white/10 lg:hidden"
            aria-label={mobileOpen ? 'Fechar menu' : 'Abrir menu'}
            aria-expanded={mobileOpen}
            onClick={() => setMobileOpen((o) => !o)}
          >
            {mobileOpen ? <X size={22} /> : <MenuIcon size={22} />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <nav className="border-t border-white/10 bg-primary px-6 pb-4 lg:hidden" aria-label="Navegação principal">
          <MobileGroup title="Dashboard">
            <MobileLink onClick={() => { go('/avaliacoes/dashboard'); setMobileOpen(false); }} icon={<BarChart3 size={16} />}>Dashboard</MobileLink>
          </MobileGroup>
          <MobileGroup title="Pessoas">
            <MobileLink onClick={() => { go('/pessoas'); setMobileOpen(false); }} icon={<Users size={16} />}>Pessoas</MobileLink>
          </MobileGroup>
          <MobileGroup title="Avaliação">
            <MobileLink onClick={() => { go('/avaliacoes/avaliar'); setMobileOpen(false); }} icon={<ClipboardList size={16} />}>Avaliação</MobileLink>
          </MobileGroup>
          <MobileGroup title="Atestados">
            <MobileLink onClick={() => { go('/atestados'); setMobileOpen(false); }} icon={<FileText size={16} />}>Atestados</MobileLink>
          </MobileGroup>
          <MobileGroup title="Cadastro">
            <MobileLink onClick={() => { go('/registrar/turma'); setMobileOpen(false); }} icon={<Users2 size={16} />}>Turma</MobileLink>
            <MobileLink onClick={() => { go('/registrar/aluno'); setMobileOpen(false); }} icon={<GraduationCap size={16} />}>Aluno</MobileLink>
            <MobileLink onClick={() => { go('/avaliacoes/catalogo'); setMobileOpen(false); }} icon={<ListChecks size={16} />}>LOs</MobileLink>
            <MobileLink onClick={() => { go('/registrar/admin'); setMobileOpen(false); }} icon={<UserPlus size={16} />}>Novo admin</MobileLink>
          </MobileGroup>
          <MobileGroup title="Exportar">
            <MobileLink onClick={() => { doExport('checkins?tipo=ALUNO', 'pontos_alunos.csv'); setMobileOpen(false); }} icon={<Download size={16} />}>Pontos (Alunos)</MobileLink>
            <MobileLink onClick={() => { doExport('checkins?tipo=STAFF', 'pontos_staff.csv'); setMobileOpen(false); }} icon={<Download size={16} />}>Pontos (Staff)</MobileLink>
            <MobileLink onClick={() => { doExport('usuarios', 'usuarios_lablivre.csv'); setMobileOpen(false); }} icon={<Download size={16} />}>Usuários</MobileLink>
          </MobileGroup>
          <button
            type="button"
            onClick={onLogout}
            className="mt-3 inline-flex items-center gap-2 rounded-lg bg-white/10 px-3 py-2 text-sm font-semibold text-white"
          >
            Sair <LogOut size={16} />
          </button>
        </nav>
      )}
    </header>
  );
}

function MobileGroup({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mt-3">
      <p className="px-1 pb-1 text-[11px] font-bold uppercase tracking-wider text-white/50">{title}</p>
      <div className="flex flex-col gap-0.5">{children}</div>
    </div>
  );
}

function MobileLink({ onClick, icon, children }: { onClick: () => void; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <button type="button" onClick={onClick} className="flex items-center gap-2.5 rounded-lg px-3 py-2 text-left text-sm font-semibold text-white/90 hover:bg-white/10">
      <span className="text-white/60">{icon}</span>{children}
    </button>
  );
}
