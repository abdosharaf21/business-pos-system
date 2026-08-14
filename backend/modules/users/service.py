"""User service for user-related business logic."""

from typing import Optional, List, Set

from backend.modules.users.model import User
from backend.modules.users.repository import UserRepository
from backend.modules.users.validator import UserValidator
from backend.shared.security import (
    create_access_token_for_user,
    hash_password,
    verify_password,
)


class UserService:
    """Service for user business operations.

    Handles all user-related business logic including authentication,
    registration, and user management. Communicates only with
    UserRepository for data access.
    """

    def __init__(self, user_repository: UserRepository, blocklist: Set[str] = None) -> None:
        """Initialize UserService with a UserRepository.

        Args:
            user_repository: Repository for user database operations.
            blocklist: Set of revoked JWT tokens.
        """
        self._user_repository = user_repository
        self._blocklist = blocklist if blocklist is not None else set()

    def login(self, email: str, password: str) -> dict:
        """Authenticate a user by email and password.

        Args:
            email: User's email address.
            password: User's plain text password.

        Returns:
            Dictionary containing user data and access token.

        Raises:
            ValueError: If email or password is invalid.
            ValueError: If user account is inactive.
        """
        validated = UserValidator.validate_login({"email": email, "password": password})
        email = validated["email"]
        password = validated["password"]

        user = self._user_repository.get_by_email(email)
        if user is None:
            raise ValueError("Invalid email or password")

        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")

        if user.status != "active":
            raise ValueError("Account is inactive")

        access_token = create_access_token_for_user(user)

        return {
            "access_token": access_token,
            "user": user.to_dict()
        }

    def logout(self, jti: str) -> None:
        """Revoke a JWT token by adding it to the blocklist.

        Args:
            jti: JWT ID to revoke.
        """
        self._blocklist.add(jti)

    def get_user_by_id(self, user_id: int) -> User:
        """Retrieve a user by their unique identifier.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            User instance if found.

        Raises:
            ValueError: If user not found.
        """
        user = self._user_repository.get_by_id(user_id)
        if user is None:
            raise ValueError("User not found")
        return user

    def get_user_by_email(self, email: str) -> User:
        """Retrieve a user by their email address.

        Args:
            email: The email address to search for.

        Returns:
            User instance if found.

        Raises:
            ValueError: If user not found.
        """
        user = self._user_repository.get_by_email(email)
        if user is None:
            raise ValueError("User not found")
        return user

    def get_all_users(self) -> List[User]:
        """Retrieve all users.

        Returns:
            List of User instances.
        """
        return self._user_repository.get_all()

    def create_user(self, user_data: dict) -> User:
        """Create a new user.

        Args:
            user_data: Dictionary containing user information.

        Returns:
            Created User instance.

        Raises:
            ValueError: If email already exists.
            ValueError: If required fields are missing.
            ValueError: If validation fails.
        """
        validated = UserValidator.validate_create_user(user_data)

        if self._user_repository.exists_by_email(validated["email"]):
            raise ValueError("Email already exists")

        password_hash = hash_password(validated["password"])

        user = User(
            full_name=validated["full_name"],
            email=validated["email"],
            password_hash=password_hash,
            phone=validated["phone"],
            role=validated["role"],
            status=validated["status"]
        )

        return self._user_repository.create(user)

    def update_user(self, user_id: int, data: dict) -> User:
        """Update an existing user.

        Args:
            user_id: The unique identifier of the user.
            data: Dictionary containing fields to update.

        Returns:
            Updated User instance.

        Raises:
            ValueError: If user not found.
            ValueError: If email already exists for another user.
            ValueError: If validation fails.
        """
        validated = UserValidator.validate_update_user(data)

        user = self._user_repository.get_by_id(user_id)
        if user is None:
            raise ValueError("User not found")

        if "email" in validated and validated["email"] != user.email:
            if self._user_repository.exists_by_email(validated["email"]):
                raise ValueError("Email already exists")

        if "full_name" in validated:
            user.full_name = validated["full_name"]
        if "email" in validated:
            user.email = validated["email"]
        if "phone" in validated:
            user.phone = validated["phone"]
        if "role" in validated:
            user.role = validated["role"]
        if "status" in validated:
            user.status = validated["status"]

        updated = self._user_repository.update(user)
        if updated is None:
            raise ValueError("Failed to update user")
        return updated

    def change_password(self, user_id: int, new_password: str) -> User:
        """Change a user's password.

        Args:
            user_id: The unique identifier of the user.
            new_password: The new plain text password.

        Returns:
            Updated User instance.

        Raises:
            ValueError: If user not found.
            ValueError: If new password is empty or invalid.
        """
        validated = UserValidator.validate_change_password({"new_password": new_password})
        new_password = validated["new_password"]

        user = self._user_repository.get_by_id(user_id)
        if user is None:
            raise ValueError("User not found")

        user.password_hash = hash_password(new_password)

        updated = self._user_repository.update(user)
        if updated is None:
            raise ValueError("Failed to update password")
        return updated

    def activate_user(self, user_id: int) -> User:
        """Activate a user account.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            Updated User instance.

        Raises:
            ValueError: If user not found.
        """
        user = self._user_repository.get_by_id(user_id)
        if user is None:
            raise ValueError("User not found")

        user.status = "active"
        updated = self._user_repository.update(user)
        if updated is None:
            raise ValueError("Failed to activate user")
        return updated

    def deactivate_user(self, user_id: int) -> User:
        """Deactivate a user account.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            Updated User instance.

        Raises:
            ValueError: If user not found.
        """
        user = self._user_repository.get_by_id(user_id)
        if user is None:
            raise ValueError("User not found")

        user.status = "inactive"
        updated = self._user_repository.update(user)
        if updated is None:
            raise ValueError("Failed to deactivate user")
        return updated

    def delete_user(self, user_id: int) -> bool:
        """Delete a user account.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            True if user was deleted successfully.

        Raises:
            ValueError: If user not found.
        """
        deleted = self._user_repository.delete(user_id)
        if not deleted:
            raise ValueError("User not found")
        return True
