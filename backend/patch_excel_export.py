import re

with open("app/api/v1/router_admin.py", "r") as f:
    content = f.read()

new_export = """
import openpyxl
from fastapi.responses import StreamingResponse
import io
from app.domain.enums import TipoUsuario
from sqlalchemy.orm import selectinload

@router.get("/export/checkins")
async def export_checkins(
    tipo: Optional[TipoUsuario] = None, 
    format: Optional[str] = "csv",
    db: AsyncSession = Depends(get_db), 
    admin: User = Depends(require_admin)
):
    query = select(CheckInModel, UserModel).join(UserModel, CheckInModel.user_id == UserModel.id)
    if tipo:
        query = query.where(UserModel.tipo == tipo)
    query = query.order_by(CheckInModel.hora_checkin.desc())
    result = await db.execute(query)
    rows = result.all()
    
    if format == "excel":
        wb = openpyxl.Workbook()
        ws_staff = wb.active
        ws_staff.title = "Staff"
        ws_alunos = wb.create_sheet("Alunos")
        
        ws_staff.append(["Nome", "Email", "Data/Hora", "Turno", "Status", "IP"])
        ws_alunos.append(["Nome", "Email", "Turma", "Data/Hora", "Turno", "Status", "IP"])
        
        # Here we would run the logic to proactively inject 'FALTAS' for Alunos
        # based on TURNOS_ALUNOS. For this MVP export, we'll append the existing records
        # separated by type. 
        # (Generating proactive falsas for an entire month requires a date parameter.
        # Assuming current month if not provided).
        
        for checkin, user in rows:
            if user.tipo == TipoUsuario.STAFF:
                ws_staff.append([
                    user.nome, user.email, 
                    checkin.hora_checkin.strftime("%Y-%m-%d %H:%M:%S") if checkin.hora_checkin else "",
                    checkin.turno_referencia or "",
                    checkin.status.value if checkin.status else "",
                    checkin.ip_publico or ""
                ])
            else:
                ws_alunos.append([
                    user.nome, user.email, user.turma_ou_equipe or "",
                    checkin.hora_checkin.strftime("%Y-%m-%d %H:%M:%S") if checkin.hora_checkin else "",
                    checkin.turno_referencia or "",
                    checkin.status.value if checkin.status else "",
                    checkin.ip_publico or ""
                ])
                
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=checkins_lablivre.xlsx"}
        )
    else:
        # Default CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Nome", "Email", "Data/Hora", "Turno", "Status", "IP", "Lat", "Lng"])
        
        for checkin, user in rows:
            writer.writerow([
                user.nome, user.email,
                checkin.hora_checkin.strftime("%Y-%m-%d %H:%M:%S") if checkin.hora_checkin else "",
                checkin.turno_referencia or "",
                checkin.status.value if checkin.status else "",
                checkin.ip_publico or "",
                "",
                ""
            ])
            
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=checkins_lablivre.csv"}
        )
"""

# Replace the existing export_checkins function
pattern = re.compile(r'@router\.get\("/export/checkins"\).*?(?=@router|\Z)', re.DOTALL)
content = pattern.sub(new_export + "\n", content)

with open("app/api/v1/router_admin.py", "w") as f:
    f.write(content)
