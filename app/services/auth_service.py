"""Authentication service."""

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate

logger = get_logger(__name__)


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register(self, user_data: UserCreate) -> User:
        if self.user_repo.get_by_email(user_data.email):
            raise ValueError("Email already registered")

        if self.user_repo.get_by_username(user_data.username):
            raise ValueError("Username already taken")

        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hash_password(user_data.password),
            role=user_data.role,
        )

        user = self.user_repo.create(user)
        logger.info("User registered", user_id=user.id, email=user.email)
        return user

    def authenticate(self, username: str, password: str) -> dict | None:
        user = self.user_repo.get_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            return None

        access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
        refresh_token = create_refresh_token(data={"sub": str(user.id), "role": user.role.value})

        logger.info("User authenticated", user_id=user.id)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    def refresh_token(self, refresh_token_str: str) -> dict | None:
        payload = decode_token(refresh_token_str)
        if not payload or payload.get("type") != "refresh":
            return None

        user_id = int(payload["sub"])
        user = self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            return None

        access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token_str,
            "token_type": "bearer",
        }

    def get_current_user(self, token: str) -> User | None:
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            return None

        user_id = int(payload["sub"])
        return self.user_repo.get_by_id(user_id)
