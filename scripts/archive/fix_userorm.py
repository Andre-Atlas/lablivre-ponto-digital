with open("backend/app/api/v1/router_admin.py", "r") as f:
    content = f.read()

content = content.replace("admin: UserORM = Depends(require_admin)", "admin: UserModel = Depends(require_admin)")

with open("backend/app/api/v1/router_admin.py", "w") as f:
    f.write(content)
