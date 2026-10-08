import re

with open("backend/app/api/v1/router_admin.py", "r") as f:
    content = f.read()

new_logic = """
from datetime import datetime, timezone
import calendar

@router.get("/export/checkins")
async def export_checkins(
    tipo: Optional[TipoUsuario] = None, 
    format: Optional[str] = "csv",
    ano: Optional[int] = None,
    mes: Optional[int] = None,
    db: AsyncSession = Depends(get_db), 
    admin: User = Depends(require_admin)
):
    query = select(CheckInModel, UserModel).join(UserModel, CheckInModel.user_id == UserModel.id)
    if tipo:
        query = query.where(UserModel.tipo == tipo)
    
    now_utc = datetime.now(timezone.utc)
    target_year = ano if ano else now_utc.year
    target_month = mes if mes else now_utc.month
    
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
        
        # Organize checkins by user and day/turno
        checkins_by_user = {}
        for checkin, user in rows:
            if user.id not in checkins_by_user:
                checkins_by_user[user.id] = []
            checkins_by_user[user.id].append(checkin)
            
        # Fetch all users to calculate faltas even for those who didn't check in at all
        users_result = await db.execute(select(UserModel))
        all_users = users_result.scalars().all()
        
        from app.domain.models import TURNOS_ALUNOS, DiaSemana, _DIA_SEMANA_MAP
        from app.domain.enums import StatusCheckin
        
        # Determine valid days in the target month up to today
        num_days = calendar.monthrange(target_year, target_month)[1]
        
        for user in all_users:
            if tipo and user.tipo != tipo: continue
            
            user_checkins = checkins_by_user.get(user.id, [])
            
            if user.tipo == TipoUsuario.STAFF:
                # Just dump raw checkins for Staff
                for checkin in user_checkins:
                    # Filter by month/year (approx)
                    if checkin.hora_checkin.year == target_year and checkin.hora_checkin.month == target_month:
                        ws_staff.append([
                            user.nome, user.email, 
                            checkin.hora_checkin.strftime("%Y-%m-%d %H:%M:%S") if checkin.hora_checkin else "",
                            checkin.turno_referencia or "",
                            checkin.status.value if checkin.status else "",
                            checkin.ip_publico or ""
                        ])
            else:
                # ALUNO: Calculate Faltas
                if not user.turma_ou_equipe:
                    continue
                    
                # Find the shifts for this turma
                turma_shifts = [t for t in TURNOS_ALUNOS if t.turma == user.turma_ou_equipe]
                if not turma_shifts:
                    continue
                
                # Check each day of the month
                for day in range(1, num_days + 1):
                    try:
                        current_date = datetime(target_year, target_month, day)
                    except ValueError:
                        continue
                        
                    # Don't calculate faltas for future days
                    if current_date.date() > now_utc.date():
                        continue
                        
                    weekday = current_date.weekday()
                    if weekday not in _DIA_SEMANA_MAP:
                        continue
                        
                    dia_enum = _DIA_SEMANA_MAP[weekday]
                    
                    # Expected shifts for this day
                    expected_shifts = [t for t in turma_shifts if t.dia == dia_enum]
                    
                    for shift in expected_shifts:
                        # Find if user has checkin for this shift
                        # turno_referencia is usually "{YYYY-MM-DD}_{MANHA/TARDE}"
                        expected_ref = f"{current_date.strftime('%Y-%m-%d')}_{shift.turno.value}"
                        
                        found_checkin = next((c for c in user_checkins if c.turno_referencia == expected_ref), None)
                        
                        if found_checkin:
                            ws_alunos.append([
                                user.nome, user.email, user.turma_ou_equipe,
                                found_checkin.hora_checkin.strftime("%Y-%m-%d %H:%M:%S") if found_checkin.hora_checkin else "",
                                expected_ref,
                                found_checkin.status.value if found_checkin.status else "",
                                found_checkin.ip_publico or ""
                            ])
                        else:
                            # Falta!
                            ws_alunos.append([
                                user.nome, user.email, user.turma_ou_equipe,
                                current_date.strftime("%Y-%m-%d"),
                                expected_ref,
                                "FALTA",
                                ""
                            ])
                            
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=checkins_lablivre_{target_year}_{target_month:02d}.xlsx"}
        )
"""

pattern = re.compile(r'@router\.get\("/export/checkins"\).*?headers=\{"Content-Disposition": "attachment; filename=checkins_lablivre\.xlsx"\}\n        \)', re.DOTALL)
content = pattern.sub(new_logic.strip(), content)

with open("backend/app/api/v1/router_admin.py", "w") as f:
    f.write(content)
