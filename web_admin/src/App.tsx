import { useState, useEffect } from 'react';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Checkin } from './pages/Checkin';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userType, setUserType] = useState<string | null>(null);
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    setIsAuthenticated(!!localStorage.getItem('token'));
    setUserType(localStorage.getItem('userType'));
    const saved = localStorage.getItem('theme');
    if (saved === 'dark') {
      setIsDark(true);
    }
  }, []);

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [isDark]);

  const toggleTheme = () => setIsDark(!isDark);

  const handleLogin = (tipo: string) => {
    setIsAuthenticated(true);
    setUserType(tipo);
    localStorage.setItem('userType', tipo);
  };
  
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userType');
    setIsAuthenticated(false);
    setUserType(null);
  };

  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} isDark={isDark} toggleTheme={toggleTheme} />;
  }

  if (userType === 'ADMIN') {
    return <Dashboard onLogout={handleLogout} isDark={isDark} toggleTheme={toggleTheme} />;
  }

  return <Checkin onLogout={handleLogout} isDark={isDark} toggleTheme={toggleTheme} />;
}

export default App;
