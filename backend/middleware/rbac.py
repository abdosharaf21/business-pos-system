"""Role-Based Access Control (RBAC) middleware for Flask routes."""

from functools import wraps
from typing import List, Callable

from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def require_roles(*allowed_roles: str) -> Callable:
    """Decorator to restrict route access by user role.

    Args:
        *allowed_roles: Variable number of role strings that are allowed.

    Returns:
        Decorated function with role-based access control.

    Usage:
        @require_roles("admin")
        def admin_only_route():
            pass

        @require_roles("admin", "manager")
        def admin_or_manager_route():
            pass
    """
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            jwt_data = get_jwt()
            user_role = jwt_data.get("role")

            if user_role not in allowed_roles:
                return jsonify({
                    "success": False,
                    "message": "Access denied. Insufficient permissions."
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def require_admin(fn: Callable) -> Callable:
    """Decorator to restrict route access to admin only.

    Args:
        fn: The route function to protect.

    Returns:
        Decorated function with admin-only access control.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        jwt_data = get_jwt()
        user_role = jwt_data.get("role")

        if user_role != "admin":
            return jsonify({
                "success": False,
                "message": "Access denied. Admin privileges required."
            }), 403

        return fn(*args, **kwargs)
    return wrapper


def require_admin_or_manager(fn: Callable) -> Callable:
    """Decorator to restrict route access to admin or manager.

    Args:
        fn: The route function to protect.

    Returns:
        Decorated function with admin or manager access control.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        jwt_data = get_jwt()
        user_role = jwt_data.get("role")

        if user_role not in ("admin", "manager"):
            return jsonify({
                "success": False,
                "message": "Access denied. Admin or manager privileges required."
            }), 403

        return fn(*args, **kwargs)
    return wrapper


def require_authenticated(fn: Callable) -> Callable:
    """Decorator to require valid JWT authentication.

    Args:
        fn: The route function to protect.

    Returns:
        Decorated function with authentication requirement.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        return fn(*args, **kwargs)
    return wrapper
