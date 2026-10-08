import re

with open('backend/app/api/v1/router_admin.py', 'r') as f:
    content = f.read()

def repl_tz(m):
    return m.group(0).replace('.astimezone', '.replace(tzinfo=timezone.utc).astimezone')

content = re.sub(r'u\.criado_em\.astimezone\([^)]+\)', repl_tz, content)
content = re.sub(r'checkin\.hora_checkin\.astimezone\([^)]+\)', repl_tz, content)
content = re.sub(r'found_checkin\.hora_checkin\.astimezone\([^)]+\)', repl_tz, content)

with open('backend/app/api/v1/router_admin.py', 'w') as f:
    f.write(content)
