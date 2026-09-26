import os
import sys
import platform

def add_to_startup():
    system = platform.system()
    app_name = "PontoDigital"
    # Current executable or script
    if getattr(sys, 'frozen', False):
        app_path = sys.executable
    else:
        app_path = os.path.abspath(sys.argv[0])
        
    if system == "Windows":
        import winreg as reg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_ALL_ACCESS)
            reg.SetValueEx(key, app_name, 0, reg.REG_SZ, app_path)
            reg.CloseKey(key)
            print("Adicionado ao startup do Windows com sucesso.")
        except Exception as e:
            print(f"Erro ao adicionar no startup: {e}")
            
    elif system == "Darwin": # macOS
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.lablivre.pontodigital</string>
    <key>ProgramArguments</key>
    <array>
        <string>{app_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""
        plist_path = os.path.expanduser(f"~/Library/LaunchAgents/com.lablivre.pontodigital.plist")
        try:
            with open(plist_path, "w") as f:
                f.write(plist_content)
            print("Adicionado ao startup do macOS via LaunchAgent.")
        except Exception as e:
            print(f"Erro ao criar plist no macOS: {e}")
            
if __name__ == "__main__":
    add_to_startup()
