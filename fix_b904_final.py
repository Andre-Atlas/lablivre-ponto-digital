import re

def fix(p):
    with open(p, 'r') as f: lines = f.readlines()
    for i, line in enumerate(lines):
        if 'raise HTTPException' in line and not 'from ' in line and not line.strip().endswith('('):
            # Check if we are inside an except block by looking up
            for j in range(i-1, -1, -1):
                if lines[j].strip().startswith('except'):
                    # Found except block
                    if 'DuplicataError' in lines[j]:
                        lines[i] = line.rstrip() + ' from None\n'
                    else:
                        lines[i] = line.rstrip() + ' from e\n'
                    break
                elif lines[j].strip().startswith('def ') or lines[j].strip().startswith('class '):
                    break # Not in an except block directly
    with open(p, 'w') as f: f.writelines(lines)

fix('backend/app/api/v1/router_auth.py')
fix('backend/app/api/v1/router_checkin.py')
