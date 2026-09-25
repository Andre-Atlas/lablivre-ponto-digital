import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
import httpx
from app.core.config import settings

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        if "code" in params:
            code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            html = """
            <html>
            <body style='font-family: sans-serif; text-align: center; margin-top: 50px;'>
                <h1 style='color: green;'>Login efetuado com sucesso!</h1>
                <p>Você já pode fechar esta aba e voltar para o aplicativo Ponto Digital.</p>
                <script>window.close();</script>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))
            
            if hasattr(self.server, 'on_auth_success'):
                self.server.on_auth_success(code)
        else:
            self.send_response(400)
            self.end_headers()
            
    def log_message(self, format, *args):
        # Desativa logs sujos no terminal
        pass

def exchange_code_for_token(code: str) -> str:
    """Troca o código de autorização pelo Access Token do Google."""
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": "http://127.0.0.1:8550/oauth_callback"
    }
    
    resp = httpx.post(token_url, data=payload)
    if resp.status_code == 200:
        return resp.json().get("access_token")
    else:
        raise Exception(f"Erro ao trocar código por token: {resp.text}")

def listen_for_oauth_callback(on_success):
    """
    Inicia um servidor web local super leve em background 
    para receber o redirect do Google.
    """
    server = HTTPServer(('127.0.0.1', 8550), OAuthCallbackHandler)
    
    def handle_auth(code):
        try:
            access_token = exchange_code_for_token(code)
            on_success(access_token)
        except Exception as e:
            print("Erro:", e)
            
    server.on_auth_success = handle_auth
    
    # Roda em thread e morre depois que receber 1 requisição
    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()
