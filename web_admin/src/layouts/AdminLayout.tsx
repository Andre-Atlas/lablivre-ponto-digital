import { Outlet } from 'react-router-dom';
import { AdminNavbar } from '../components/AdminNavbar';
import { AppFooter } from '../components/AppFooter';

export function AdminLayout({ onLogout }: { onLogout: () => void }) {
  return (
    <div className="flex min-h-screen flex-col bg-bg text-ink">
      <AdminNavbar onLogout={onLogout} />
      <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-10 lg:px-8">
        <Outlet />
      </main>
      <AppFooter />
    </div>
  );
}
