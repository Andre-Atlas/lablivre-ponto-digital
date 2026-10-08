import re

with open('backend/app/api/v1/router_admin.py', 'r') as f:
    content = f.read()

# Add timezone import if not there
if 'from datetime import timedelta' not in content:
    content = content.replace('from datetime import datetime, timezone', 'from datetime import datetime, timezone, timedelta')

# Update export_usuarios
content = content.replace(
    'writer.writerow(["ID", "Nome", "Email", "Tipo", "Aprovado", "Turma", "Criado Em"])',
    'writer.writerow(["ID", "Nome", "Email", "Tipo", "Aprovado", "Turma", "Máquina", "Criado Em"])'
)
def repl_usuarios(m):
    return '''writer.writerow([
            str(u.id), u.nome, u.email, u.tipo.value if u.tipo else "",
            "Sim" if u.admin_aprovado else "Nao", u.turma_ou_equipe or "", u.patrimonio or "",
            u.criado_em.astimezone(timezone(timedelta(hours=-3))).strftime("%Y-%m-%d %H:%M:%S") if u.criado_em else ""
        ])'''
content = re.sub(r'writer\.writerow\(\[\s*str\(u\.id\).*?\]\)', repl_usuarios, content, flags=re.DOTALL)

# Update export_checkins
content = content.replace(
    'ws_staff.append(["Nome", "Email", "Data/Hora", "Turno", "Status", "IP"])',
    'ws_staff.append(["Nome", "Email", "Máquina", "Data/Hora", "Turno", "Status", "IP"])'
)
content = content.replace(
    'ws_alunos.append(["Nome", "Email", "Turma", "Data/Hora", "Turno", "Status", "IP"])',
    'ws_alunos.append(["Nome", "Email", "Turma", "Máquina", "Data/Hora", "Turno", "Status", "IP"])'
)
content = content.replace(
    'writer.writerow(["Nome", "Email", "Data/Hora", "Turno", "Status", "IP", "Lat", "Lng"])',
    'writer.writerow(["Nome", "Email", "Turma", "Máquina", "Data/Hora", "Turno", "Status", "IP"])'
)

# Replace staff append
def repl_staff(m):
    return '''ws_staff.append([
                            user.nome, user.email, user.patrimonio or "",
                            checkin.hora_checkin.astimezone(timezone(timedelta(hours=-3))).strftime("%Y-%m-%d %H:%M:%S") if checkin.hora_checkin else "",
                            checkin.turno_referencia or "",
                            checkin.status.value if checkin.status else "",
                            checkin.ip_publico or ""
                        ])'''
content = re.sub(r'ws_staff\.append\(\[\s*user\.nome, user\.email,\s*checkin\.hora_checkin\.strftime.*?\]\)', repl_staff, content, flags=re.DOTALL)

# Replace aluno append found
def repl_aluno_found(m):
    return '''ws_alunos.append([
                                user.nome, user.email, user.turma_ou_equipe, user.patrimonio or "",
                                found_checkin.hora_checkin.astimezone(timezone(timedelta(hours=-3))).strftime("%Y-%m-%d %H:%M:%S") if found_checkin.hora_checkin else "",
                                expected_ref,
                                found_checkin.status.value if found_checkin.status else "",
                                found_checkin.ip_publico or ""
                            ])'''
content = re.sub(r'ws_alunos\.append\(\[\s*user\.nome, user\.email, user\.turma_ou_equipe,\s*found_checkin\.hora_checkin\.strftime.*?\]\)', repl_aluno_found, content, flags=re.DOTALL)

# Replace aluno append missing (Falta)
def repl_aluno_missing(m):
    return '''ws_alunos.append([
                                user.nome, user.email, user.turma_ou_equipe, user.patrimonio or "",
                                current_date.strftime("%Y-%m-%d"),
                                expected_ref,
                                "FALTA",
                                ""
                            ])'''
content = re.sub(r'ws_alunos\.append\(\[\s*user\.nome, user\.email, user\.turma_ou_equipe,\s*current_date\.strftime.*?\]\)', repl_aluno_missing, content, flags=re.DOTALL)

# Replace CSV checkins
def repl_csv(m):
    return '''writer.writerow([
                user.nome, user.email, user.turma_ou_equipe or "", user.patrimonio or "",
                checkin.hora_checkin.astimezone(timezone(timedelta(hours=-3))).strftime("%Y-%m-%d %H:%M:%S") if checkin.hora_checkin else "",
                checkin.turno_referencia or "",
                checkin.status.value if checkin.status else "",
                checkin.ip_publico or ""
            ])'''
content = re.sub(r'writer\.writerow\(\[\s*user\.nome, user\.email,\s*checkin\.hora_checkin\.strftime.*?\]\)', repl_csv, content, flags=re.DOTALL)

with open('backend/app/api/v1/router_admin.py', 'w') as f:
    f.write(content)
