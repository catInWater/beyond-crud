from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select


from src.db.models import User
from src.auth.schemas import UserBook, UserLoginModel, UserModel, UserPassword, UserRegisterModel
from src.auth.utils import hash_password, verify_password


class UserService():
    
    async def get_user_by_email(self, email: str, session: AsyncSession) -> UserModel:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        return user

    async def create_user(self, user: UserRegisterModel, session: AsyncSession) -> UserModel:
        new_user = User(
            username=user.username,
            email=user.email,
            password_hash=hash_password(user.password),
            first_name=user.first_name,
            last_name=user.last_name,
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return UserModel.model_validate(new_user)
    
    async def login_user(self, user: UserLoginModel, session: AsyncSession) -> UserModel:
        result = await session.execute(select(User).where(User.email == user.email))
        res_user = result.scalar_one_or_none()
        if res_user and verify_password(user.password, res_user.password_hash):
            return UserModel.model_validate(res_user)
        return None
    
    async def update_user(self, user: UserModel, update_data: dict, session: AsyncSession) -> UserModel:
        for key, value in update_data.items():
            setattr(user, key, value)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return UserModel.model_validate(user)
            
    async def delete_user(self, user: UserModel, session: AsyncSession) -> None:
        await session.delete(user)
        await session.commit()
        
    async def reset_password(self, user: User, new_password: str, session: AsyncSession) -> UserModel:
        user.password_hash = hash_password(new_password)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return UserModel.model_validate(user)
