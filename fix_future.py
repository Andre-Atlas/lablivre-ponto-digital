import os, glob

for root, _, files in os.walk('backend'):
    for f in files:
        if f.endswith('.py'):
            p = os.path.join(root, f)
            with open(p, 'r') as file:
                lines = file.readlines()
            
            if lines and lines[0].startswith('from __future__ import annotations'):
                # find docstring
                if len(lines) > 2 and lines[2].startswith('"""'):
                    # swap
                    end_idx = 2
                    for i in range(2, len(lines)):
                        if i > 2 and '"""' in lines[i]:
                            end_idx = i
                            break
                    doc = lines[2:end_idx+1]
                    fut = lines[0:2]
                    rest = lines[end_idx+1:]
                    
                    with open(p, 'w') as file:
                        file.writelines(doc + ['\n'] + fut + rest)
