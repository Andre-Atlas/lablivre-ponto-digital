with open("web_admin/src/pages/Login.tsx", "r") as f:
    content = f.read()

# Add state
if "const [showPassword, setShowPassword] = useState(false);" not in content:
    content = content.replace("const [isLoading, setIsLoading] = useState(false);", "const [showPassword, setShowPassword] = useState(false);\n  const [isLoading, setIsLoading] = useState(false);")

# Add icons
if "Eye" not in content:
    content = content.replace("Mail, Lock, ChevronRight } from 'lucide-react';", "Mail, Lock, ChevronRight, Eye, EyeOff } from 'lucide-react';")

with open("web_admin/src/pages/Login.tsx", "w") as f:
    f.write(content)
