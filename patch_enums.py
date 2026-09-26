import re

with open("backend/app/domain/enums.py", "r") as f:
    content = f.read()

if 'NONE = "NONE"' not in content:
    content = content.replace('VIEWER = "VIEWER"', 'VIEWER = "VIEWER"\n    NONE = "NONE"')

with open("backend/app/domain/enums.py", "w") as f:
    f.write(content)
