import re

def fix(p, old, new):
    with open(p, 'r') as f: c = f.read()
    c = c.replace(old, new)
    with open(p, 'w') as f: f.write(c)

fix('backend/tests/conftest.py', '"""Fixture que fornece um cliente HTTP assíncrono (httpx.AsyncClient) para testes de endpoints."""', '"""Fixture que fornece um cliente HTTP assíncrono (httpx.AsyncClient) para testes de api."""')
fix('backend/tests/integration/test_admin_roles.py', '"DELETE FROM users WHERE email IN (\'super@test.com\', \'admin@test.com\', \'staff@test.com\', \'aluno@test.com\')"', '"DELETE FROM users WHERE email IN "\n                "(\'super@test.com\', \'admin@test.com\', \'staff@test.com\', \'aluno@test.com\')"')
fix('backend/tests/integration/test_web_checkin.py', '# 2. Staff trying to use Web Checkin -> Should succeed (201) (or 400 if weekend, but endpoint works)', '# 2. Staff trying to use Web Checkin -> Should succeed (201) (or 400 if weekend)')

