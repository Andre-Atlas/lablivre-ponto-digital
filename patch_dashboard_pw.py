import re
with open("web_admin/src/pages/Dashboard.tsx", "r") as f:
    content = f.read()

# Replace the input block
new_pw_input = """<div className="relative">
                  <input 
                    type={showPassword ? "text" : "password"}
                    required
                    value={newAdmin.senha}
                    onChange={e => setNewAdmin({...newAdmin, senha: e.target.value})}
                    className="w-full bg-white dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.08] rounded-xl px-4 py-2.5 pr-12 focus:outline-none focus:border-[#00B9DE]/50 focus:bg-white dark:focus:bg-white/[0.05] transition-all font-light text-sm text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-white/30 shadow-[inset_0_2px_4px_rgba(0,0,0,0.02)]"
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-4 flex items-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>"""

# Match the old input precisely with regex
pattern = r'<input[^>]*type="password"[^>]*value={newAdmin\.senha}[^>]*>'
content = re.sub(pattern, new_pw_input, content, flags=re.DOTALL)

with open("web_admin/src/pages/Dashboard.tsx", "w") as f:
    f.write(content)
