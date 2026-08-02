"""Inventory audit routes for stock count API endpoints."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity

from backend.modules.inventory_audits.service import InventoryAuditService
from backend.middleware.rbac import require_authenticated, require_admin_or_manager

inventory_audits_bp = Blueprint(
    "inventory_audits", __name__, url_prefix="/api/inventory-audits"
)

_audit_service: InventoryAuditService = None


def init_audit_service(audit_service: InventoryAuditService) -> None:
    """Initialize the audit service dependency.

    Args:
        audit_service: Instance of InventoryAuditService for DI.
    """
    global _audit_service
    _audit_service = audit_service


@inventory_audits_bp.route("/", methods=["GET"])
@require_authenticated
def list_audits():
    """List audits with filters, sorting, and pagination.

    Query params:
        search: Search in audit name.
        location: Filter by location (warehouse, store).
        status: Filter by status (open, completed, cancelled).
        sort: Sort column (name, location, status, ...).
        order: Sort direction (asc, desc).
        page: Page number (default 1).
        per_page: Records per page (default 20, max 100).

    Returns:
        JSON response with paginated audit list.
    """
    filters = {
        "search": request.args.get("search"),
        "location": request.args.get("location"),
        "status": request.args.get("status"),
        "sort": request.args.get("sort", "created_at"),
        "order": request.args.get("order", "desc"),
        "page": request.args.get("page", 1),
        "per_page": request.args.get("per_page", 20),
    }
    try:
        result = _audit_service.list_audits(filters)
        return jsonify({
            "success": True,
            "message": "Inventory audits retrieved successfully",
            "data": result,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@inventory_audits_bp.route("/<int:audit_id>", methods=["GET"])
@require_authenticated
def get_audit(audit_id):
    """Get an audit by ID.

    Args:
        audit_id: The unique identifier of the audit.

    Returns:
        JSON response with audit data.
    """
    try:
        audit = _audit_service.get_audit(audit_id)
        return jsonify({
            "success": True,
            "message": "Inventory audit retrieved successfully",
            "data": audit.to_dict(),
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404


@inventory_audits_bp.route("/<int:audit_id>/items", methods=["GET"])
@require_authenticated
def get_audit_items(audit_id):
    """Get the items of an audit.

    Args:
        audit_id: The unique identifier of the audit.

    Returns:
        JSON response with the audit items list.
    """
    try:
        items = _audit_service.get_items(audit_id)
        return jsonify({
            "success": True,
            "message": "Inventory audit items retrieved successfully",
            "data": items,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404


@inventory_audits_bp.route("/", methods=["POST"])
@require_admin_or_manager
def create_audit():
    """Create a new inventory audit.

    Body:
        name: Required audit name.
        location: Required location (warehouse or store).

    Returns:
        JSON response with created audit data.
    """
    data = request.get_json(silent=True)
    try:
        user_id = int(get_jwt_identity())
        audit = _audit_service.create_audit(data, user_id)
        return jsonify({
            "success": True,
            "message": "Inventory audit created successfully",
            "data": audit.to_dict(),
        }), 201
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@inventory_audits_bp.route("/<int:audit_id>/complete", methods=["POST"])
@require_admin_or_manager
def complete_audit(audit_id):
    """Complete an open audit applying adjustments to inventory.

    Args:
        audit_id: The unique identifier of the audit.

    Returns:
        JSON response with the completion result.
    """
    try:
        user_id = int(get_jwt_identity())
        result = _audit_service.complete_audit(audit_id, user_id)
        return jsonify({
            "success": True,
            "message": "Inventory audit completed successfully",
            "data": result,
        }), 200
    except ValueError as e:
        if str(e) == "Audit not found":
            return jsonify({"success": False, "message": str(e)}), 404
        return jsonify({"success": False, "message": str(e)}), 400


@inventory_audits_bp.route("/<int:audit_id>", methods=["PUT"])
@require_admin_or_manager
def update_audit(audit_id):
    """Update an open audit (name, status, or counted quantities).

    Args:
        audit_id: The unique identifier of the audit.

    Returns:
        JSON response with updated audit data.
    """
    data = request.get_json(silent=True)
    try:
        audit = _audit_service.update_audit(audit_id, data)
        return jsonify({
            "success": True,
            "message": "Inventory audit updated successfully",
            "data": audit.to_dict(),
        }), 200
    except ValueError as e:
        if str(e) == "Audit not found":
            return jsonify({"success": False, "message": str(e)}), 404
        return jsonify({"success": False, "message": str(e)}), 400


@inventory_audits_bp.route("/<int:audit_id>", methods=["DELETE"])
@require_admin_or_manager
def delete_audit(audit_id):
    """Delete an audit.

    Args:
        audit_id: The unique identifier of the audit.

    Returns:
        JSON response with result.
    """
    try:
        _audit_service.delete_audit(audit_id)
        return jsonify({"success": True, "message": "Inventory audit deleted successfully"}), 200
    except ValueError as e:
        if str(e) == "Audit not found":
            return jsonify({"success": False, "message": str(e)}), 404
        return jsonify({"success": False, "message": str(e)}), 400
