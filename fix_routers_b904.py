import re

def fix(p):
    with open(p, 'r') as f: c = f.read()
    
    # raise HTTPException(status_code=..., detail=...) -> raise HTTPException(...) from err
    def replacer(match):
        stmt = match.group(0)
        if 'from e' not in stmt and 'from None' not in stmt:
            if 'Você já bateu o ponto' in stmt:
                return stmt + ' from None'
            return stmt + ' from e'
        return stmt

    # match raise HTTPException(....) correctly even across lines
    c = re.sub(r'raise HTTPException\([^)]+\)', replacer, c)
    with open(p, 'w') as f: f.write(c)

fix('backend/app/api/v1/router_auth.py')
fix('backend/app/api/v1/router_checkin.py')

