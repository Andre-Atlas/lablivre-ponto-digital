import re
with open("web_admin/src/pages/Login.tsx", "r") as f:
    content = f.read()

# Add state
if "const [showPassword, setShowPassword] = useState(false);" not in content:
    content = content.replace("const [loading, setLoading] = useState(false);", "const [showPassword, setShowPassword] = useState(false);\n  const [loading, setLoading] = useState(false);")

# Add icons
if "Eye" not in content:
    content = content.replace("Lock, Loader2 } from 'lucide-react';", "Lock, Loader2, Eye, EyeOff } from 'lucide-react';")

new_pw = """                  <input 
                    type={showPassword ? "text" : "password"}
                    required 
                    placeholder="••••••••"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    className="w-full bg-white/50 dark:bg-black/20 border border-slate-200 dark:border-white/[0.08] rounded-xl pl-11 pr-12 py-3.5 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-white/20 text-sm outline-none focus:border-[#D12A6A]/50 focus:bg-white dark:focus:bg-black/40 transition-all shadow-[inset_0_2px_4px_rgba(0,0,0,0.02)] dark:shadow-[inset_0_2px_4px_rgba(0,0,0,0.2)]" 
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-4 flex items-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>"""

pattern = r'<input[^>]*type="password"[^>]*value={password}[^>]*>'
content = re.sub(pattern, new_pw, content, flags=re.DOTALL)

with open("web_admin/src/pages/Login.tsx", "w") as f:
    f.write(content)
