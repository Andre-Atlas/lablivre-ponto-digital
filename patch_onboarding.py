with open('backend/app/application/onboarding_use_case.py', 'r') as f:
    content = f.read()

old_logic = """        usuario_existente = await self.user_repo.buscar_por_email(email)
        if usuario_existente:
            # Login normal
            jwt_token = create_access_token(data={
                "sub": str(usuario_existente.id), 
                "tipo": str(usuario_existente.tipo)
            })
            return usuario_existente, jwt_token, False"""

new_logic = """        usuario_existente = await self.user_repo.buscar_por_email(email)
        if usuario_existente:
            # Verifica se o dispositivo atual está registrado para este usuário
            dispositivos_do_usuario = await self.device_repo.listar_por_usuario(usuario_existente.id)
            mac_existente = any(d.mac_address == request.device_mac for d in dispositivos_do_usuario)
            
            if not mac_existente:
                from uuid import uuid4
                from datetime import datetime, timezone
                from app.domain.models import Device
                
                novo_device = Device(
                    id=uuid4(),
                    user_id=usuario_existente.id,
                    mac_address=request.device_mac,
                    os_type=request.device_os,
                    hostname=request.device_hostname,
                    serial_number=request.device_serial,
                    principal=len(dispositivos_do_usuario) == 0,
                    registrado_em=datetime.now(timezone.utc)
                )
                await self.device_repo.criar(novo_device)

            jwt_token = create_access_token(data={
                "sub": str(usuario_existente.id), 
                "tipo": str(usuario_existente.tipo)
            })
            return usuario_existente, jwt_token, False"""

content = content.replace(old_logic, new_logic)

with open('backend/app/application/onboarding_use_case.py', 'w') as f:
    f.write(content)
