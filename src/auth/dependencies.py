from fastapi import HTTPException, Request, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.auth.utils import decode_token
from src.db.redis import token_in_blocklist
from src.db.main import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.service import UserService
from src.auth.schemas import UserBook, UserModel

from src.errors import (AccessTokenRequired, AccountNotVerified, InsufficientPermission, RefreshTokenRequired, RevokedToken, InvalidToken)



class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)
        
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        credentials = await super().__call__(request)
        token = credentials.credentials
        token_data = decode_token(token)
        if token_data is None:
            raise InvalidToken()
        if await token_in_blocklist(token_data["jti"]):
            raise RevokedToken()
        self.verify_token_data(token_data)
        return token_data
    
    def verify_token_data(self, token_data: dict):
        raise NotImplementedError("Please Override this method in child classes")
    
class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise AccessTokenRequired()
            
    
class RefreshTokenBearer(TokenBearer):
    async def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise RefreshTokenRequired()
            
access_token_bearer = AccessTokenBearer()  
user_service = UserService()              
async def get_current_user(token_details: dict = Depends(access_token_bearer),
                           session: AsyncSession = Depends(get_session)) -> UserModel:
    user = await user_service.get_user_by_email(token_details["user"]["email"], session)
    return user
                 
class RoleChecker:
    def __init__(self, roles: list[str]):
        self.roles = roles
    
    async def __call__(self, user: UserModel = Depends(get_current_user)) -> None:
        if not user.is_verified:
            raise AccountNotVerified()
        if user.role not in self.roles:
            raise InsufficientPermission()
            

    