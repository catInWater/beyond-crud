from datetime import timedelta, datetime, timezone
import uuid
from fastapi import HTTPException
import jwt
from src.config import Config
import logging
from passlib.context import CryptContext
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)

def create_access_token(user_data: dict, expiry: timedelta=None, refresh: bool=False) -> str:
    payload = {
        'user': user_data,
        'exp': datetime.now(timezone.utc) + (expiry if expiry is not None else timedelta(minutes=Config.ACCESS_TOKEN_EXPIRY_MINUTE)),
        'jti': str(uuid.uuid4()),
        'refresh': refresh
    }
    
    token = jwt.encode(payload=payload,
                       key=Config.JWT_SECRET,
                       algorithm=Config.JWT_ALGORITHM)
    return token

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError as jwte:
        logging.exception(jwte)
        return None
    except Exception as e:
        logging.exception(e)
        return None



serializer = URLSafeTimedSerializer(
    secret_key=Config.JWT_SECRET, salt="email-configuration"
)

def create_url_safe_token(data: dict, expiry: timedelta = timedelta(hours=1)) -> str:
    """Serialize a dict into a URLSafe token"""

    token = serializer.dumps(data)

    return token

def decode_url_safe_token(token:str, max_age: timedelta = timedelta(hours=1)) -> dict:
    """Deserialize a URLSafe token to get data"""
    try:
        token_data = serializer.loads(token, max_age=max_age.total_seconds())
        return token_data
    except SignatureExpired:
        raise HTTPException(status_code=400, detail="Token has expired")
    except BadSignature:
        raise HTTPException(status_code=400, detail="Invalid token")

    

