import { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Login } from './pages/Login';
import { Styleguide } from './styleguide/Styleguide';
import { AdminLayout } from './layouts/AdminLayout';
import { PessoasPage } from './pages/admin/PessoasPage';
import { AvaliarPage } from './pages/admin/AvaliarPage';
import { LODashboardPage } from './pages/admin/LODashboardPage';
import { CatalogoPage } from './pages/admin/CatalogoPage';
import { FrequenciaPage } from './pages/admin/FrequenciaPage';
import { RegistrarAlunoPage } from './pages/admin/RegistrarAlunoPage';
import { RegistrarAdminPage } from './pages/admin/RegistrarAdminPage';
import { TurmasPage } from './pages/admin/TurmasPage';

function AppRoutes() {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'));
  const [userType, setUserType] = useState<string | null>(() => localStorage.getItem('userType'));

  // Só mentores autenticam (o backend rejeita alunos no login).
  const isAuthed = !!token;

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
  void userType;

  const home = isAuthed ? '/avaliacoes/dashboard' : '/login';

  return (
    <Routes>
      <Route path="/styleguide" element={<Styleguide />} />

      <Route path="/login" element={isAuthed ? <Navigate to={home} replace /> : <Login onLogin={handleLogin} />} />

      {/* Área do mentor (único perfil que autentica) */}
      <Route
        element={isAuthed ? <AdminLayout onLogout={handleLogout} /> : <Navigate to={home} replace />}
      >
        <Route path="/pessoas" element={<PessoasPage />} />
        <Route path="/avaliacoes/avaliar" element={<AvaliarPage />} />
        <Route path="/avaliacoes/dashboard" element={<LODashboardPage />} />
        <Route path="/avaliacoes/catalogo" element={<CatalogoPage />} />
        <Route path="/frequencia" element={<FrequenciaPage />} />
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
