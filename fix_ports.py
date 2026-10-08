import glob, re
for p in glob.glob('backend/app/domain/ports/*.py') + ['backend/app/domain/models.py']:
    with open(p, 'r') as f: c = f.read()
    c = c.replace('from __future__ import annotations\n\n\n', '')
    c = c.replace('from __future__ import annotations\n\n', '')
    c = c.replace('from __future__ import annotations\n', '')
    c = 'from __future__ import annotations\n\n' + c
    with open(p, 'w') as f: f.write(c)
