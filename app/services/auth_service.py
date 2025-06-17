from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..models.user import User
from ..models.session import Session as UserSession
from ..utils.security import verify_password, create_access_token
from ..utils.constants import ACCESS_TOKEN_EXPIRE_HOURS, MAX_SESSIONS_PER_USER
import secrets


class AuthService:
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        user = db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def get_user_sessions(db: Session, user_id: int) -> List[UserSession]:
        """Get all active sessions for a user"""
        return db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.expires_at > datetime.utcnow()
        ).all()

    @staticmethod
    def check_session_limit(db: Session, user_id: int) -> bool:
        """Check if user has reached session limit"""
        active_sessions = AuthService.get_user_sessions(db, user_id)
        return len(active_sessions) >= MAX_SESSIONS_PER_USER

    @staticmethod
    def delete_session(db: Session, session_id: int, user_id: int) -> bool:
        """Delete a specific session"""
        session = db.query(UserSession).filter(
            UserSession.id == session_id,
            UserSession.user_id == user_id
        ).first()

        if session:
            db.delete(session)
            db.commit()
            return True
        return False

    @staticmethod
    def create_session(
            db: Session,
            user: User,
            device_name: str,
            ip_address: str
    ) -> tuple[str, UserSession]:
        """Create new session and return token"""
        # Generate JWT token
        token_data = {"sub": user.username, "user_id": user.id}
        expires_delta = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        access_token = create_access_token(token_data, expires_delta)

        # Create session record
        session = UserSession(
            user_id=user.id,
            token=secrets.token_urlsafe(32),  # Unique session identifier
            device_name=device_name,
            ip_address=ip_address,
            last_login=datetime.utcnow(),
            expires_at=datetime.utcnow() + expires_delta
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        return access_token, session

    @staticmethod
    def logout_session(db: Session, token: str) -> bool:
        """Logout current session"""
        session = db.query(UserSession).filter(UserSession.token == token).first()
        if session:
            db.delete(session)
            db.commit()
            return True
        return False

    @staticmethod
    def cleanup_expired_sessions(db: Session):
        """Remove expired sessions"""
        db.query(UserSession).filter(
            UserSession.expires_at <= datetime.utcnow()
        ).delete()
        db.commit()