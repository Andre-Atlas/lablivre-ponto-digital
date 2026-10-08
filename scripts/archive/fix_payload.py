with open("backend/tests/integration/test_aluno_checkin_real.py", "r") as f:
    content = f.read()

import re
old_payload = re.search(r'payload = \{.*?"bssid": "WRONG_BSSID"\n\s*\}', content, re.DOTALL).group(0)
new_payload = """payload = {
            "device_mac": "00:11:22:33:44:55",
            "ssid": "My_Wifi",
            "bssids": ["WRONG_BSSID"]
        }"""
        
content = content.replace(old_payload, new_payload)

with open("backend/tests/integration/test_aluno_checkin_real.py", "w") as f:
    f.write(content)
