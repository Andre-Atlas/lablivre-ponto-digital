import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Instância do TanStack Query Client para gerenciamento de cache e requisições assíncronas
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutos de cache
      retry: 1,
    },
  },
});

// Componentes de páginas de espaço reservado (placeholders)
function Dashboard() {
  return <h1>Dashboard</h1>;
}

function Users() {
  return <h1>Users</h1>;
}

function Logs() {
  return <h1>Logs</h1>;
}

function Settings() {
  return <h1>Settings</h1>;
}

function Login() {
  return <h1>Login</h1>;
}

/**
 * Componente principal da aplicação com roteamento React Router e TanStack Query Provider.
 */
export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/users" element={<Users />} />
          <Route path="/logs" element={<Logs />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/login" element={<Login />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
