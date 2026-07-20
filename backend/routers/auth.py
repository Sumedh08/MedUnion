from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from core.security import create_access_token, ROLES
from schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])

DEMO_USERS = {
    "admin": {"password": "admin", "role": "admin", "name": "System Administrator"},
    "hospital": {"password": "hospital", "role": "hospital_manager", "name": "Hospital Manager"},
    "district": {"password": "district", "role": "district_officer", "name": "District Health Officer"},
    "analyst": {"password": "analyst", "role": "analyst", "name": "Data Analyst"},
    "viewer": {"password": "viewer", "role": "viewer", "name": "Read-only Viewer"},
}


@router.post("/token", response_model=TokenResponse)
def login(request: LoginRequest):
    user = DEMO_USERS.get(request.username)
    if not user or user["password"] != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token(
        data={"sub": request.username, "role": user["role"], "name": user["name"]},
        expires_delta=timedelta(hours=24),
    )
    return TokenResponse(
        access_token=token,
        role=user["role"],
        permissions=ROLES.get(user["role"], []),
    )
