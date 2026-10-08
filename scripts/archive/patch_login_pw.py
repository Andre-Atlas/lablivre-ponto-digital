import re
with open("web_admin/src/pages/Login.tsx", "r") as f:
    content = f.read()

# Add state
if "const [showPassword, setShowPassword] = useState(false);" not in content:
    content = content.replace("const [loading, setLoading] = useState(false);", "const [showPassword, setShowPassword] = useState(false);\n  const [loading, setLoading] = useState(false);")

# Add icons
if "Eye" not in content:
    content = content.replace("Lock, Mail, ArrowRight } from 'lucide-react';", "Lock, Mail, ArrowRight, Eye, EyeOff } from 'lucide-react';")

# Find the password input block
old_block = """<div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400">
                <Lock size={20} />
              </div>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-11 pr-4 py-3.5 bg-white/50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700/50 rounded-2xl focus:outline-none focus:ring-2 focus:ring-[#D12A6A]/30 focus:border-[#D12A6A] text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 backdrop-blur-sm transition-all"
                placeholder="••••••••"
                required
              />
            </div>"""

new_block = """<div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400">
                <Lock size={20} />
              </div>
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-11 pr-12 py-3.5 bg-white/50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700/50 rounded-2xl focus:outline-none focus:ring-2 focus:ring-[#D12A6A]/30 focus:border-[#D12A6A] text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 backdrop-blur-sm transition-all"
                placeholder="••••••••"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 pr-4 flex items-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>"""

# Replace exactly
content = content.replace(old_block, new_block)

with open("web_admin/src/pages/Login.tsx", "w") as f:
    f.write(content)
