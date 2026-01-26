from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# Secret key (in real app, use .env)
SECRET_KEY = "supersecretkey_tn_health_hackathon"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class TokenData(BaseModel):
    username: str | None = None
    role: str | None = None

class User(BaseModel):
    username: str
    full_name: str | None = None
    role: str # "admin" | "facility" | "logistics"
    facility_id: str | None = None

class UserInDB(User):
    hashed_password: str

# Mock Database
fake_users_db = {
    "tn_health_sec": {
        "username": "tn_health_sec",
        "full_name": "Dr. J. Radhakrishnan",
        "role": "admin",
        "hashed_password": pwd_context.hash("admin123"),
    },
    "rgggh_dean": {
        "username": "rgggh_dean",
        "full_name": "Dean RGGGH",
        "role": "facility",
        "facility_id": "FAC-CHE-001",
        "hashed_password": pwd_context.hash("hospital123"),
    },
    "108_dispatch": {
        "username": "108_dispatch",
        "full_name": "GVK EMRI Dispatch",
        "role": "logistics",
        "hashed_password": pwd_context.hash("ambulance123"),
    }
}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str):
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)
    return None

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
