with open("backend/app/api/v1/router_admin.py", "r") as f:
    content = f.read()

# Fix export_checkins
old_checkins = """        writer.writerow([
            user.nome, user.email,
            checkin.hora_checkin.strftime("%Y-%m-%d %H:%M:%S") if checkin.hora_checkin else "",
            checkin.turno_referencia or "",
            checkin.status.value if checkin.status else "",
            checkin.ip_publico or "",
            str(checkin.latitude) if checkin.latitude else "",
            str(checkin.longitude) if checkin.longitude else "",
        ])"""

new_checkins = """        writer.writerow([
            user.nome, user.email,
            checkin.hora_checkin.strftime("%Y-%m-%d %H:%M:%S") if checkin.hora_checkin else "",
            checkin.turno_referencia or "",
            checkin.status.value if checkin.status else "",
            checkin.ip_publico or "",
            "",
            "",
        ])"""

content = content.replace(old_checkins, new_checkins)

# Fix export_usuarios
old_usuarios = """        writer.writerow([
            str(u.id), u.nome, u.email, u.tipo.value if u.tipo else "",
            "Sim" if u.admin_aprovado else "Nao", u.turma_ou_equipe or "",
            u.created_at.strftime("%Y-%m-%d %H:%M:%S") if u.created_at else ""
        ])"""

new_usuarios = """        writer.writerow([
            str(u.id), u.nome, u.email, u.tipo.value if u.tipo else "",
            "Sim" if u.admin_aprovado else "Nao", u.turma_ou_equipe or "",
            u.criado_em.strftime("%Y-%m-%d %H:%M:%S") if u.criado_em else ""
        ])"""

content = content.replace(old_usuarios, new_usuarios)

with open("backend/app/api/v1/router_admin.py", "w") as f:
    f.write(content)
