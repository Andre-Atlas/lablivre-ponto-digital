import re, glob
def rep(p, o, n):
    with open(p, 'r') as f: c = f.read()
    c = c.replace(o, n)
    with open(p, 'w') as f: f.write(c)

rep('backend/app/domain/ports/geolocation_service.py', 'lat_user: float = None,', 'lat_user: float | None = None,')
rep('backend/app/domain/ports/geolocation_service.py', 'lng_user: float = None,', 'lng_user: float | None = None,')
rep('backend/app/adapters/external/geolocation_service_impl.py', 'lat_user: float = None,', 'lat_user: float | None = None,')
rep('backend/app/adapters/external/geolocation_service_impl.py', 'lng_user: float = None,', 'lng_user: float | None = None,')

rep('backend/app/adapters/persistence/config_repo_impl.py', '        pass', '        raise NotImplementedError("Configuração ainda não implementada")')

# bssids list
rep('backend/app/adapters/persistence/checkin_repo_impl.py', 'bssids=orm.bssids,', 'bssids=[item for item in orm.bssids if isinstance(item, str)] if isinstance(orm.bssids, list) else [],')

# Init returns
rep('backend/app/application/checkin_use_case.py', 'def __init__(\n        self,\n        checkin_repo: CheckInRepository,\n        user_repo: UserRepository,\n        device_repo: DeviceRepository,\n    ):', 'def __init__(\n        self,\n        checkin_repo: CheckInRepository,\n        user_repo: UserRepository,\n        device_repo: DeviceRepository,\n    ) -> None:')
rep('backend/app/application/onboarding_use_case.py', 'def __init__(self, user_repo: UserRepository, device_repo: DeviceRepository):', 'def __init__(self, user_repo: UserRepository, device_repo: DeviceRepository) -> None:')
rep('backend/app/adapters/persistence/checkin_repo_impl.py', 'def __init__(self, session: AsyncSession):', 'def __init__(self, session: AsyncSession) -> None:')

# Fix enums in ORM
with open('backend/app/adapters/persistence/orm_models.py', 'r') as f: c = f.read()
c = re.sub(r'class StatusCheckin\(str, Enum\):.*?ATRASADO = "ATRASADO"\n', '', c, flags=re.DOTALL)
c = re.sub(r'class RoleAdmin\(str, Enum\):.*?NONE = "NONE"\n', '', c, flags=re.DOTALL)
c = re.sub(r'class TipoUsuario\(str, Enum\):.*?STAFF = "STAFF"\n', '', c, flags=re.DOTALL)
c = c.replace('from app.domain.enums import TipoUsuario', 'from app.domain.enums import TipoUsuario, StatusCheckin, RoleAdmin')
with open('backend/app/adapters/persistence/orm_models.py', 'w') as f: f.write(c)

# oauth_sub
rep('backend/app/application/onboarding_use_case.py', 'oauth_sub=sub,', 'oauth_sub=sub or "",')

# sheets client guard
rep('backend/app/adapters/external/sheets_service_impl.py', '            sh = self.gc.open_by_key(settings.GOOGLE_SHEET_ID)', '            if self.gc is None:\n                return False\n            sh = self.gc.open_by_key(settings.GOOGLE_SHEET_ID)')

# Dict returns
for p in glob.glob('backend/app/api/v1/router_*.py'):
    rep(p, ') -> dict:', ') -> dict[str, Any]:')
    rep(p, ') -> dict\n', ') -> dict[str, Any]\n')

# checkins_by_user: dict
rep('backend/app/api/v1/router_admin.py', 'checkins_by_user: dict = {}', 'checkins_by_user: dict[Any, Any] = {}')
rep('backend/app/api/v1/router_admin.py', 'payload: dict = Depends(get_current_user)', 'payload: dict[str, Any] = Depends(get_current_user)')
rep('backend/app/api/v1/router_auth.py', 'user_payload: dict = Depends(get_current_user)', 'user_payload: dict[str, Any] = Depends(get_current_user)')
rep('backend/app/api/v1/router_checkin.py', 'user_payload: dict = Depends(get_current_user)', 'user_payload: dict[str, Any] = Depends(get_current_user)')

# Security casts
rep('backend/app/adapters/auth/jwt_handler.py', 'return encoded_jwt', 'return str(encoded_jwt)')
rep('backend/app/utils/security.py', 'return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")', 'return str(bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8"))')
rep('backend/app/utils/security.py', 'return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))', 'return bool(bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8")))')

