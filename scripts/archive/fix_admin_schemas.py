with open("backend/app/api/schemas/admin_schemas.py", "r") as f:
    content = f.read()

# Add ConfigDict to pydantic import
if "ConfigDict" not in content:
    content = content.replace("from pydantic import BaseModel", "from pydantic import BaseModel, ConfigDict")

if "model_config = ConfigDict(from_attributes=True)" not in content:
    content = content.replace("class UserAdminResponse(BaseModel):", "class UserAdminResponse(BaseModel):\n    model_config = ConfigDict(from_attributes=True)\n")

with open("backend/app/api/schemas/admin_schemas.py", "w") as f:
    f.write(content)
