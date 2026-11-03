from datetime import timedelta
from fastapi.responses import JSONResponse
from src.config import Config
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.schemas import PasswordModel, PasswordResetRequestModel, UserLoginModel, UserModel, UserRegisterModel, UserBook, EmailModel
from src.auth.service import UserService
from src.db.main import get_session
from src.db.redis import add_jti_to_blocklist
from src.auth.utils import create_access_token, create_url_safe_token, decode_url_safe_token, hash_password
from src.auth.dependencies import RefreshTokenBearer, AccessTokenBearer, RoleChecker, get_current_user
import time

from src.mail import create_message, mail
from src.celery_tasks import send_email_task

from src.errors import EmailAlreadyExists, InvalidToken, UserNotFound


auth_router = APIRouter()
user_service = UserService()
refresh_token_bearer = RefreshTokenBearer()
access_token_bearer = AccessTokenBearer()
role_checker = RoleChecker(["admin", "user"])


@auth_router.post("/send_hello_email")
async def send_hello_email(email: EmailModel):
    message = create_message(
        recipients=email.addresses,
        subject="Hello from Bookly",
        body="<h1>Hello from Bookly</h1><p>This is a test email sent from the Bookly API.</p>",
    )
    mail.send_message(message)
    return {"message": "Email sent successfully"}

@auth_router.get("/me", response_model=UserBook, dependencies=[Depends(role_checker)])
async def get_current_user(session: AsyncSession = Depends(get_session), user: UserModel = Depends(get_current_user)) -> UserBook:
    return user

@auth_router.post("/register")
async def creater_user(user: UserRegisterModel, bg_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)) -> dict:
    old_user = await user_service.get_user_by_email(user.email, session)
    if old_user:
        raise EmailAlreadyExists()
    new_user = await user_service.create_user(user, session)
    token = create_url_safe_token({"email": new_user.email})
    recipients=[new_user.email]
    subject="Welcome to Bookly"
    body=f"<h1>Welcome to Bookly</h1><p>Thank you for registering. Please verify your email by clicking the link below:</p><a href='http://{Config.DOMAIN}/api/v1/auth/verify_email?token={token}'>Verify Email</a>"
    # await mail.send_message(message)
    send_email_task.delay(recipients, subject, body)
    return {
        "message": "User registered successfully. Please check your email to verify your account.",
        "user": new_user
    }
    
@auth_router.get("/verify_email")
async def verify_email(token: str, session: AsyncSession = Depends(get_session)) -> dict:
    token_data = decode_url_safe_token(token)
    if "email" not in token_data:
            raise InvalidToken()
    
    user = await user_service.get_user_by_email(token_data["email"], session)
    if not user:
        raise UserNotFound()
    
    # Here you would typically update the user's record to mark them as verified.
    # For example: user.is_verified = True
    # Then commit the changes to the database.
    await user_service.update_user(user, {"is_verified": True}, session)
    
    return JSONResponse(
            content={"message": "Account verified successfully"},
            status_code=status.HTTP_200_OK,
        )

@auth_router.post("/login")
async def login_user(user: UserLoginModel, session: AsyncSession = Depends(get_session)) -> dict:
    result = await user_service.login_user(user, session)
    if result:
        access_token = create_access_token(user_data={"email": result.email, "user_uid": str(result.uid), "role": result.role})
        refresh_token = create_access_token(user_data={"email": result.email, "user_uid": str(result.uid), "role": result.role},
                                            refresh=True,
                                            expiry=timedelta(days=Config.REFRESH_TOKEN_EXPIRY_DAY))
        return {
                "message": "Login successful",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {"email": result.email, "uid": str(result.uid)},
        }
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Email Or Password"
    )
    
@auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(refresh_token_bearer)) -> dict:
    if token_details["exp"] > time.time():
        access_token = create_access_token(user_data=token_details["user"])
        return {"access_token": access_token}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Or expired token"
    )
    
@auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(access_token_bearer)) -> dict:
    await add_jti_to_blocklist(token_details["jti"])
    return {
            "message":"Logged Out Successfully"
            }
    
@auth_router.delete("/delete/{email}")
async def delete_user(email: str, session: AsyncSession = Depends(get_session)) -> dict:
    user = await user_service.get_user_by_email(email, session)
    if not user:
        raise UserNotFound()
    await user_service.delete_user(user, session)
    return {"message": "User deleted successfully"}

@auth_router.post("/reset_password")
async def reset_password(email: PasswordResetRequestModel, session: AsyncSession = Depends(get_session)) -> dict:
    user = await user_service.get_user_by_email(email.email, session)
    if not user:
        raise UserNotFound()
    token = create_url_safe_token({"email": user.email})
    recipients=[user.email]
    subject="Reset Your Password"
    body=f"<h1>Reset Your Password</h1><p>Please reset your password by clicking the link below:</p><a href='http://{Config.DOMAIN}/api/v1/auth/reset_password_confirm?token={token}'>Reset Password</a>"
    send_email_task.delay(recipients, subject, body)
    return {
        "message": "Password reset email sent successfully. Please check your email.",
    }
    
@auth_router.post("/reset_password_confirm")
async def reset_password_confirm(token: str, new_password: PasswordModel, session: AsyncSession = Depends(get_session)) -> dict:
    token_data = decode_url_safe_token(token)
    if "email" not in token_data:
        raise InvalidToken()
    
    user = await user_service.get_user_by_email(token_data["email"], session)
    if not user:
        raise UserNotFound()
    
    await user_service.update_user(user, {"password_hash": hash_password(new_password.password)}, session)
    
    return {
        "message": "Password reset successfully. You can now log in with your new password.",
    }


