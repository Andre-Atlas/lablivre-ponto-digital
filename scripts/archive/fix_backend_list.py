import re

with open("backend/app/api/v1/router_admin.py", "r") as f:
    content = f.read()

old_return = """    return [
        UserAdminResponse(
            id=u.id, 
            nome=u.nome, 
            email=u.email, 
            tipo=u.tipo, 
            admin_aprovado=u.admin_aprovado
        ) for u in users
    ]"""

new_return = """    return users  # Let FastAPI serialize it. We just need from_attributes=True in schema."""

# Wait, if we return users, we must ensure UserAdminResponse has from_attributes=True.
content = content.replace(old_return, new_return)

with open("backend/app/api/v1/router_admin.py", "w") as f:
    f.write(content)
