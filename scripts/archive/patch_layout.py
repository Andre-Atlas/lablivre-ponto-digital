with open("web_admin/src/pages/Dashboard.tsx", "r") as f:
    content = f.read()

old_container = '<div className="flex flex-col sm:flex-row items-center gap-4 w-full md:w-auto">'
new_container = '<div className="flex flex-col xl:flex-row flex-wrap items-center justify-start xl:justify-end gap-3 w-full lg:w-auto mt-4 md:mt-0">'

content = content.replace(old_container, new_container)

old_buttons_container = '<div className="flex gap-2 w-full sm:w-auto">'
new_buttons_container = '<div className="flex flex-wrap gap-2 w-full sm:w-auto">'

content = content.replace(old_buttons_container, new_buttons_container)

old_novo_admin = 'className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-[#D12A6A] to-[#B01E55] hover:from-[#D12A6A] hover:to-[#F39200] text-white font-medium tracking-wide text-xs rounded-xl shadow-[0_4px_14px_rgba(209,42,106,0.3)] hover:shadow-[0_6px_20px_rgba(209,42,106,0.4)] transition-all active:scale-95 border border-[#D12A6A]/50"'
new_novo_admin = 'className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-[#D12A6A] to-[#B01E55] hover:from-[#D12A6A] hover:to-[#F39200] text-white font-medium tracking-wide text-xs whitespace-nowrap rounded-xl shadow-[0_4px_14px_rgba(209,42,106,0.3)] hover:shadow-[0_6px_20px_rgba(209,42,106,0.4)] transition-all active:scale-95 border border-[#D12A6A]/50 shrink-0"'

content = content.replace(old_novo_admin, new_novo_admin)

with open("web_admin/src/pages/Dashboard.tsx", "w") as f:
    f.write(content)
