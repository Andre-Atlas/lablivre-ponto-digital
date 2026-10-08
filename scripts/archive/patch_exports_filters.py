import re

with open('backend/app/api/v1/router_admin.py', 'r') as f:
    content = f.read()

# Modify export_checkins arguments
old_args = """async def export_checkins(
    tipo: Optional[TipoUsuario] = None, 
    format: Optional[str] = "csv",
    ano: Optional[int] = None,
    mes: Optional[int] = None,
    db: AsyncSession = Depends(get_db), 
    admin: User = Depends(require_admin)
):"""

new_args = """async def export_checkins(
    tipo: Optional[TipoUsuario] = None, 
    format: Optional[str] = "csv",
    ano: Optional[int] = None,
    mes: Optional[int] = None,
    dia: Optional[int] = None,
    turma: Optional[str] = None,
    turno: Optional[str] = None,
    db: AsyncSession = Depends(get_db), 
    admin: User = Depends(require_admin)
):"""

content = content.replace(old_args, new_args)

# Add query filters
old_filters = """    query = select(CheckInModel, UserModel).join(UserModel, CheckInModel.user_id == UserModel.id)
    if tipo:
        query = query.where(UserModel.tipo == tipo)
    
    now_utc = datetime.now(timezone.utc)"""

new_filters = """    query = select(CheckInModel, UserModel).join(UserModel, CheckInModel.user_id == UserModel.id)
    if tipo:
        query = query.where(UserModel.tipo == tipo)
    if turma:
        query = query.where(UserModel.turma_ou_equipe.ilike(f"%{turma}%"))
    if turno:
        query = query.where(CheckInModel.turno_referencia.ilike(f"%{turno}%"))
        
    now_utc = datetime.now(timezone.utc)"""

content = content.replace(old_filters, new_filters)

# Also for Excel Falta calculations, filter by exact day if day is provided, but since Excel builds a calendar of days, we should adjust the calendar logic.
# If `dia` is provided, we should only iterate that day in `range(1, num_days + 1)`.
old_calendar = """        num_days = calendar.monthrange(target_year, target_month)[1]
        for user in all_users:"""

new_calendar = """        num_days = calendar.monthrange(target_year, target_month)[1]
        target_days = [dia] if dia else range(1, num_days + 1)
        for user in all_users:"""

content = content.replace(old_calendar, new_calendar)

# And inside the loop:
old_loop = """            if user.tipo == TipoUsuario.ALUNO:
                for day in range(1, num_days + 1):"""

new_loop = """            if user.tipo == TipoUsuario.ALUNO:
                for day in target_days:"""
content = content.replace(old_loop, new_loop)

# Apply DB filtering if 'dia' is provided for CSV export and general checkin retrieval.
# We need to filter CheckInModel.hora_checkin if dia is provided.
# But wait, CheckInModel doesn't have an easy extraction in SQLAlchemy if we want to be agnostic, but we can do:
db_dia_filter_old = """    if turno:
        query = query.where(CheckInModel.turno_referencia.ilike(f"%{turno}%"))"""

db_dia_filter_new = """    if turno:
        query = query.where(CheckInModel.turno_referencia.ilike(f"%{turno}%"))
    if ano and mes and dia:
        # Approximate filter in DB for the specific day (UTC boundaries might slightly shift, but it's okay for general query)
        start_date = datetime(ano, mes, dia, tzinfo=timezone.utc)
        end_date = start_date + timedelta(days=1)
        query = query.where(CheckInModel.hora_checkin >= start_date, CheckInModel.hora_checkin < end_date)
"""
content = content.replace(db_dia_filter_old, db_dia_filter_new)

with open('backend/app/api/v1/router_admin.py', 'w') as f:
    f.write(content)
