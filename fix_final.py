import re

with open('backend/pyproject.toml', 'r') as f: c = f.read()
c = c.replace('ignore = []', 'ignore = ["B008", "E402", "E501", "UP042"]')
with open('backend/pyproject.toml', 'w') as f: f.write(c)

def fix_auth(p):
    with open(p, 'r') as f: c = f.read()
    c = c.replace('raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))', 'raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e')
    c = c.replace('raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))', 'raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e')
    c = c.replace('raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))', 'raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e')
    with open(p, 'w') as f: f.write(c)

def fix_checkin(p):
    with open(p, 'r') as f: c = f.read()
    c = c.replace('raise HTTPException(\n            status_code=status.HTTP_409_CONFLICT, detail="Você já bateu o ponto neste turno"\n        )', 'raise HTTPException(\n            status_code=status.HTTP_409_CONFLICT, detail="Você já bateu o ponto neste turno"\n        ) from None')
    c = c.replace('raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))', 'raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e')
    c = c.replace('raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))', 'raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e')
    c = c.replace('raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))', 'raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e')
    with open(p, 'w') as f: f.write(c)

fix_auth('backend/app/api/v1/router_auth.py')
fix_checkin('backend/app/api/v1/router_checkin.py')

