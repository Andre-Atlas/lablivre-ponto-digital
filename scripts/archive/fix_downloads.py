import re

with open("web_admin/src/pages/Dashboard.tsx", "r") as f:
    content = f.read()

# Remove the block:
#           {/* Client Downloads */}
#           <div className="flex gap-2 w-full mt-4 sm:w-auto">
#           ...
#           </div>

content = re.sub(r'\s*\{\/\* Client Downloads \*\/\}.*?</div>', '', content, flags=re.DOTALL)

with open("web_admin/src/pages/Dashboard.tsx", "w") as f:
    f.write(content)
