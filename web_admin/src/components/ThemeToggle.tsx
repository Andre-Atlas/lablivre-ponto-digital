import { Sun, Moon } from 'lucide-react';

interface ThemeToggleProps {
  isDark: boolean;
  toggle: () => void;
}

export function ThemeToggle({ isDark, toggle }: ThemeToggleProps) {
  return (
    <button
      onClick={toggle}
      className={`
        relative flex items-center w-28 h-10 rounded-full p-1 cursor-pointer transition-all duration-500
        border border-black/10 dark:border-white/20
        bg-white/40 dark:bg-black/40 backdrop-blur-xl
        shadow-[inset_0_2px_4px_rgba(0,0,0,0.05),0_4px_12px_rgba(0,0,0,0.05)]
        dark:shadow-[inset_0_2px_4px_rgba(0,0,0,0.2),0_4px_12px_rgba(0,0,0,0.5)]
      `}
    >
      {/* Track Text */}
      <div className="absolute inset-0 flex items-center justify-between px-3.5 pointer-events-none">
        <span className={`text-xs font-medium tracking-wide transition-opacity duration-300 ${isDark ? 'opacity-100 text-white/70' : 'opacity-0'}`}>
          Night
        </span>
        <span className={`text-xs font-medium tracking-wide transition-opacity duration-300 ${isDark ? 'opacity-0' : 'opacity-100 text-slate-500'}`}>
          Day
        </span>
      </div>

      {/* Thumb */}
      <div
        className={`
          relative flex items-center justify-center w-8 h-8 rounded-full transition-all duration-500 transform
          ${isDark ? 'translate-x-[72px]' : 'translate-x-0'}
        `}
      >
        {/* Glow Effect */}
        <div 
          className={`
            absolute inset-0 rounded-full blur-[8px] opacity-80 transition-colors duration-500
            ${isDark ? 'bg-[#00B9DE]' : 'bg-[#F39200]'}
          `}
        ></div>
        
        {/* Solid Thumb Body */}
        <div 
          className={`
            absolute inset-0 rounded-full border shadow-sm transition-colors duration-500
            ${isDark 
              ? 'bg-gradient-to-br from-blue-400 to-[#00B9DE] border-white/20' 
              : 'bg-gradient-to-br from-yellow-300 to-[#F39200] border-white/40'
            }
          `}
        ></div>

        {/* Icon */}
        <div className="relative z-10 text-white">
          {isDark ? <Moon size={16} fill="currentColor" /> : <Sun size={16} fill="currentColor" />}
        </div>
      </div>
    </button>
  );
}
