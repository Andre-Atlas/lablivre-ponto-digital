with open("web_admin/src/pages/Dashboard.tsx", "r") as f:
    content = f.read()

helper_funcs = """
  const handleExport = async (endpoint: string, filename: string) => {
    try {
      const res = await fetch(`${API_URL}/admin/export/${endpoint}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!res.ok) throw new Error('Falha ao exportar');
      
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert("Erro ao exportar arquivo.");
    }
  };

  const confirmApprove"""

content = content.replace("  const confirmApprove", helper_funcs)

with open("web_admin/src/pages/Dashboard.tsx", "w") as f:
    f.write(content)
