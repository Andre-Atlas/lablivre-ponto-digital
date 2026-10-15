import { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Login } from './pages/Login';
import { Checkin } from './pages/Checkin';
import { Styleguide } from './styleguide/Styleguide';
import { AdminLayout } from './layouts/AdminLayout';
import { PessoasPage } from './pages/admin/PessoasPage';
import { AvaliarPage } from './pages/admin/AvaliarPage';
import { LODashboardPage } from './pages/admin/LODashboardPage';
import { CatalogoPage } from './pages/admin/CatalogoPage';
import { AtestadosPage } from './pages/admin/AtestadosPage';
import { RegistrarAlunoPage } from './pages/admin/RegistrarAlunoPage';
import { RegistrarAdminPage } from './pages/admin/RegistrarAdminPage';
import { TurmasPage } from './pages/admin/TurmasPage';

function AppRoutes() {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'));
  const [userType, setUserType] = useState<string | null>(() => localStorage.getItem('userType'));

  const isAuthed = !!token;
  const isAdmin = userType === 'ADMIN' || userType === 'STAFF';

  const handleLogin = (tipo: string) => {
    localStorage.setItem('userType', tipo);
    setUserType(tipo);
    setToken(localStorage.getItem('token'));
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userType');
    setToken(null);
    setUserType(null);
  };

  const home = !isAuthed ? '/login' : isAdmin ? '/avaliacoes/dashboard' : '/checkin';

  return (
    <Routes>
      <Route path="/styleguide" element={<Styleguide />} />

      <Route path="/login" element={isAuthed ? <Navigate to={home} replace /> : <Login onLogin={handleLogin} />} />

      <Route
        path="/checkin"
        element={isAuthed && !isAdmin ? <Checkin onLogout={handleLogout} /> : <Navigate to={home} replace />}
      />

      {/* Admin area */}
      <Route
        element={isAuthed && isAdmin ? <AdminLayout onLogout={handleLogout} /> : <Navigate to={home} replace />}
      >
        <Route path="/pessoas" element={<PessoasPage />} />
        <Route path="/avaliacoes/avaliar" element={<AvaliarPage />} />
        <Route path="/avaliacoes/dashboard" element={<LODashboardPage />} />
        <Route path="/avaliacoes/catalogo" element={<CatalogoPage />} />
        <Route path="/atestados" element={<AtestadosPage />} />
        <Route path="/registrar/turma" element={<TurmasPage />} />
        <Route path="/registrar/aluno" element={<RegistrarAlunoPage />} />
        <Route path="/registrar/admin" element={<RegistrarAdminPage />} />
      </Route>

      <Route path="*" element={<Navigate to={home} replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}
