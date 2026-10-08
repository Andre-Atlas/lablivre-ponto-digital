import gspread
import asyncio
import os
from datetime import datetime
from app.domain.ports.sheets_service import SheetsService
from app.domain.models import CheckIn, User, Device
from app.config import settings


class SheetsServiceImpl(SheetsService):
    def __init__(self):
        # Conecta usando a conta de serviço
        creds_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "..", "credentials.json"
        )
        self.gc = None
        if os.path.exists(creds_path) and settings.GOOGLE_SHEET_ID:
            try:
                self.gc = gspread.service_account(filename=creds_path)
            except Exception as e:
                print(f"Erro ao carregar credenciais do Google: {e}")

    async def exportar_checkin_aluno(self, checkin: CheckIn, user: User, device: Device) -> bool:
        if not self.gc:
            return False
        return await asyncio.to_thread(self._sync_export, "Alunos", checkin, user, device)

    async def exportar_checkin_staff(self, checkin: CheckIn, user: User, device: Device) -> bool:
        if not self.gc:
            return False
        return await asyncio.to_thread(self._sync_export, "Staff", checkin, user, device)

    def _sync_export(self, nome_aba: str, checkin: CheckIn, user: User, device: Device) -> bool:
        try:
            sh = self.gc.open_by_key(settings.GOOGLE_SHEET_ID)

            # Tenta pegar a aba com o mês atual, ex: "Alunos_09_2026"
            mes_ano = datetime.now().strftime("%m_%Y")
            nome_aba_completo = f"{nome_aba}_{mes_ano}"

            try:
                worksheet = sh.worksheet(nome_aba_completo)
            except gspread.exceptions.WorksheetNotFound:
                # Se a aba não existe, cria com os cabeçalhos
                worksheet = sh.add_worksheet(title=nome_aba_completo, rows=1000, cols=10)
                cabecalhos = [
                    "ID Check-in",
                    "Nome",
                    "E-mail",
                    "Turma/Equipe",
                    "Patrimônio",
                    "Data/Hora",
                    "Turno",
                    "Status",
                    "IP",
                    "MAC Address",
                ]
                worksheet.append_row(cabecalhos)

            # Prepara a linha de dados
            hora_formatada = checkin.hora_checkin.strftime("%Y-%m-%d %H:%M:%S")
            row = [
                str(checkin.id),
                user.nome,
                user.email,
                user.turma_ou_equipe,
                user.patrimonio or "",
                hora_formatada,
                checkin.turno_referencia,
                checkin.status.value,
                checkin.ip_publico or "",
                device.mac_address,
            ]

            worksheet.append_row(row)
            return True
        except Exception as e:
            print(f"Erro ao exportar para Sheets: {e}")
            return False
