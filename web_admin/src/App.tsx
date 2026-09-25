import { useState, useEffect } from 'react';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isDark, setIsDark] = useState(false); // Default to light mode

  useEffect(() => {
    setIsAuthenticated(!!localStorage.getItem('token'));
    // Read from localStorage if saved
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

  const handleLogin = () => setIsAuthenticated(true);
  
  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
  };

  return isAuthenticated 
    ? <Dashboard onLogout={handleLogout} isDark={isDark} toggleTheme={toggleTheme} /> 
    : <Login onLogin={handleLogin} isDark={isDark} toggleTheme={toggleTheme} />;
}

export default App;
