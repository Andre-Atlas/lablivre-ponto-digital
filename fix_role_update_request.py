with open("backend/app/api/v1/router_admin.py", "r") as f:
    content = f.read()
    
# Insert before @router.post("/usuarios/{user_id}/role")
if "class RoleUpdateRequest" not in content:
    content = content.replace(
        '@router.post("/usuarios/{user_id}/role")',
        'class RoleUpdateRequest(BaseModel):\n    role: RoleAdmin\n\n@router.post("/usuarios/{user_id}/role")'
    )

with open("backend/app/api/v1/router_admin.py", "w") as f:
    f.write(content)
