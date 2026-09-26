import httpx

url = "https://lablivre-ponto-digital.onrender.com/api/v1/checkin/"
try:
    resp = httpx.post(url, json={"turno_referencia": "Manhã"}, headers={"Authorization": "Bearer BAD_TOKEN"})
    print(resp.status_code)
    print(resp.text)
    data = resp.json()
    print("JSON:", data)
except Exception as e:
    print("EXCEPTION:", repr(e))
