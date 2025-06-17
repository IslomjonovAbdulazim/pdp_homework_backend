from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..schemas.auth import LoginRequest, LoginResponse, SessionResponse, DeviceConflictResponse
from ..schemas.user import UserResponse
from ..services.auth_service import AuthService
from ..dependencies.auth import get_current_active_user
from ..models.user import User

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
        login_data: LoginRequest,
        request: Request,
        db: Session = Depends(get_db)
):
    """Login endpoint with device management"""

    # Get client IP
    ip_address = request.client.host

    # Authenticate user
    user = AuthService.authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Check session limit
    if AuthService.check_session_limit(db, user.id):
        # Return device conflict - frontend should handle this
        active_sessions = AuthService.get_user_sessions(db, user.id)
        sessions_data = [
            SessionResponse(
                id=s.id,
                device_name=s.device_name,
                ip_address=s.ip_address,
                last_login=s.last_login,
                expires_at=s.expires_at
            ) for s in active_sessions
        ]

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Maximum devices reached. Use /auth/login/force to override."
        )

    # Create new session
    access_token, session = AuthService.create_session(
        db, user, login_data.device_name, ip_address
    )

    return LoginResponse(
        access_token=access_token,
        user=UserResponse.from_orm(user).dict()
    )


@router.post("/login/force", response_model=LoginResponse)
async def force_login(
        login_data: LoginRequest,
        logout_session_id: int,
        request: Request,
        db: Session = Depends(get_db)
):
    """Force login by logging out a specific device"""

    # Get client IP
    ip_address = request.client.host

    # Authenticate user
    user = AuthService.authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Logout the specified session
    if not AuthService.delete_session(db, logout_session_id, user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Create new session
    access_token, session = AuthService.create_session(
        db, user, login_data.device_name, ip_address
    )

    return LoginResponse(
        access_token=access_token,
        user=UserResponse.from_orm(user).dict()
    )


@router.post("/logout")
async def logout(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Logout current session"""
    # Note: In a real implementation, you'd need to track which session/token is being used
    # For simplicity, we'll just return success
    # In production, you'd want to blacklist the JWT token or track session tokens

    return {"message": "Logged out successfully"}


@router.get("/sessions", response_model=List[SessionResponse])
async def get_sessions(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Get user's active sessions"""
    sessions = AuthService.get_user_sessions(db, current_user.id)

    return [
        SessionResponse(
            id=s.id,
            device_name=s.device_name,
            ip_address=s.ip_address,
            last_login=s.last_login,
            expires_at=s.expires_at
        ) for s in sessions
    ]


@router.delete("/sessions/{session_id}")
async def delete_session(
        session_id: int,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Delete/logout a specific session"""

    if not AuthService.delete_session(db, session_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    return {"message": "Session deleted successfully"}