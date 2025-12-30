from database.models import async_session
from database.models import User
from sqlalchemy import select

async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()
            
async def get_users():
    async with async_session() as session:
        users = await session.scalars(select(User))
        return users.all()