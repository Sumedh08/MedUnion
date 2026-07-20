from pydantic import BaseModel
from typing import Optional, List


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    permissions: List[str]


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    role: str
    name: str
    permissions: List[str]


class AuditLogResponse(BaseModel):
    id: int
    user_id: str
    action: str
    resource: str
    resource_id: Optional[str]
    result: str
    timestamp: str
