from cryptography.hazmat.primitives.ciphers import algorithms
from fastapi import HTTPException, status, Request, Depends
from src.user.user_models import UserModel
from src.user.user_schema import Register,Login
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.utils.db import get_db
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta, timezone
from src.utils.settings import settings
from jwt.exceptions import InvalidTokenError, InvalidSignatureError

security = HTTPBearer()

async def create_refresh_token(user_id):
    expiry = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRY_TIME)
    jwt_payload = {
        "_id": user_id,
        "exp": expiry,
        "type": "refresh"
    }
    refresh_token = jwt.encode(jwt_payload,settings.JWT_SECRET, algorithm =settings.ALGORITHM )
    return refresh_token

async def create_access_token(user_id):
    expiry = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRY_TIME)
    jwt_payload = {
        "_id": user_id,
        "exp": expiry,
        "type": "access"
    }
    access_token = jwt.encode(jwt_payload,settings.JWT_SECRET, algorithm =settings.ALGORITHM )
    return access_token


async def register_user(user:Register,db:Session):
    username = db.query(UserModel).filter(UserModel.username == user.username).first()
    if username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Username already exist")

    email = db.query(UserModel).filter(UserModel.email == user.email).first()
    if email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email already exist")
    
    new_user = UserModel(
        username = user.username,
        email = user.email,
        password = generate_password_hash(user.password),
        is_active = False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

async def login_user(body:Login, db:Session):
    user = db.query(UserModel).filter(UserModel.email == body.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid email or password")
    
    password = check_password_hash(password = body.password , pwhash = user.password)
    
    if not password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid email or password")
    access_token = await create_access_token(user.id)
    refresh_token = await create_refresh_token(user.id)
    
    return {"refresh_token": refresh_token,"access_token":access_token, "token_type":"bearer"}

async def authentication(request:Request, db:Session):
    try: 
        token = request.headers.get("Authorization")
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Authorization header missing")
        token = token.split(' ')[-1]
        data = jwt.decode(token, settings.JWT_SECRET, algorithms=settings.ALGORITHM)
        if not data["type"] == "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid token type")
        user_id = data["_id"]
        user = db.get(UserModel, user_id)

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="User not found")
        return user
    
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="user unauthorized")
    
async def check_refresh_token(request:Request, db:Session):
    try:
        header = request.headers.get("Authorization")
        refresh_token = header.split(' ')[-1]
        data = jwt.decode(refresh_token, settings.JWT_SECRET, algorithms=settings.ALGORITHM)
        if not data["type"] == "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="invalid refresh token")
        access_token = await create_access_token(data["_id"])
        return {"access_token": access_token, "token_type":"bearer"}
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="invalid refresh token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """"
    Dependency to get the current authenticated user,
    """
    try: 
        token = credentials.credentials
        data = jwt.decode(token, settings.JWT_SECRET, algorithms= 
        settings.ALGORITHM)

        if not data["type"] == "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = data["_id"]
        user = db.query(UserModel).get(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
    
    except InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )