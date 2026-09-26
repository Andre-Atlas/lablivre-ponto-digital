import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select
from app.adapters.persistence.orm_models import User as UserModel, Checkin as CheckInModel
import io
import csv

async def main():
    engine = create_async_engine("postgresql+asyncpg://postgres.djvpkrevmkrpvfzinqev:J.4_jkbaKyDe3XK@aws-0-sa-east-1.pooler.supabase.com:6543/postgres?ssl=require", connect_args={"statement_cache_size": 0})
    async with engine.connect() as conn:
        result = await conn.execute(
            select(CheckInModel, UserModel)
            .join(UserModel, CheckInModel.user_id == UserModel.id)
            .order_by(CheckInModel.hora_checkin.desc())
        )
        rows = result.all()
        
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
                str(checkin.latitude) if checkin.latitude else "",
                str(checkin.longitude) if checkin.longitude else "",
            ])
        print("Checkins ok!")
    await engine.dispose()

asyncio.run(main())
