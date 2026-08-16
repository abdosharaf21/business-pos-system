"""Worker management routes for the worker and payroll API endpoints."""

from flask import Blueprint, request, jsonify

from backend.middleware.rbac import require_authenticated, require_admin_or_manager
from backend.modules.worker_management.service import WorkerManagementService

worker_management_bp = Blueprint(
    "worker_management", __name__, url_prefix="/api/worker-management"
)

_worker_management_service: WorkerManagementService = None


def init_worker_management_service(
    worker_management_service: WorkerManagementService
) -> None:
    """Initialize the worker management service dependency.

    Args:
        worker_management_service: Instance of WorkerManagementService
            for dependency injection.
    """
    global _worker_management_service
    _worker_management_service = worker_management_service


def _json_ok(message: str, data=None, status: int = 200):
    """Build a successful JSON response.

    Args:
        message: Human readable success message.
        data: Optional payload to include.
        status: HTTP status code.

    Returns:
        JSON response tuple.
    """
    return jsonify({
        "success": True,
        "message": message,
        "data": data,
    }), status


def _json_error(message: str, status: int = 400):
    """Build an error JSON response.

    Args:
        message: Human readable error message.
        status: HTTP status code.

    Returns:
        JSON response tuple.
    """
    return jsonify({"success": False, "message": message}), status


# ----------------------------------------------------------------------
# Workers
# ----------------------------------------------------------------------

@worker_management_bp.route("/workers/", methods=["GET"])
@require_authenticated
def get_all_workers():
    """Get all workers with optional search and status filters.

    Query params:
        search: Search term for name, phone, job title or department.
        status: Status filter (active or inactive).

    Returns:
        JSON response with the list of workers.
    """
    search = request.args.get("search", "")
    status = request.args.get("status", "")
    workers = _worker_management_service.get_all_workers(
        search=search or None,
        status=status or None,
    )
    return _json_ok(
        "Workers retrieved successfully",
        [worker.to_dict() for worker in workers],
        200,
    )


@worker_management_bp.route("/workers/<int:worker_id>", methods=["GET"])
@require_authenticated
def get_worker(worker_id):
    """Get a worker by ID.

    Args:
        worker_id: The unique identifier of the worker.

    Returns:
        JSON response with the worker data.
    """
    try:
        worker = _worker_management_service.get_worker(worker_id)
        return _json_ok("Worker retrieved successfully", worker.to_dict(), 200)
    except ValueError as e:
        return _json_error(str(e), 404)


@worker_management_bp.route("/workers/", methods=["POST"])
@require_admin_or_manager
def create_worker():
    """Create a new worker.

    Expects JSON body with worker fields.

    Returns:
        JSON response with the created worker data.
    """
    data = request.get_json()
    try:
        worker = _worker_management_service.create_worker(data)
        return _json_ok("Worker created successfully", worker.to_dict(), 201)
    except ValueError as e:
        return _json_error(str(e), 400)


@worker_management_bp.route("/workers/<int:worker_id>", methods=["PUT"])
@require_admin_or_manager
def update_worker(worker_id):
    """Update an existing worker.

    Args:
        worker_id: The unique identifier of the worker.

    Returns:
        JSON response with the updated worker data.
    """
    data = request.get_json()
    try:
        worker = _worker_management_service.update_worker(worker_id, data)
        return _json_ok("Worker updated successfully", worker.to_dict(), 200)
    except ValueError as e:
        return _json_error(str(e), 400)


@worker_management_bp.route("/workers/<int:worker_id>", methods=["DELETE"])
@require_admin_or_manager
def delete_worker(worker_id):
    """Delete a worker.

    Args:
        worker_id: The unique identifier of the worker.

    Returns:
        JSON response with the deletion result.
    """
    try:
        _worker_management_service.delete_worker(worker_id)
        return _json_ok("Worker deleted successfully", None, 200)
    except ValueError as e:
        return _json_error(str(e), 404)


# ----------------------------------------------------------------------
# Attendance
# ----------------------------------------------------------------------

@worker_management_bp.route("/attendance/", methods=["GET"])
@require_authenticated
def get_all_attendance():
    """Get all attendance records with optional filters.

    Query params:
        worker_id: Worker id filter.
        date: Exact date filter (YYYY-MM-DD).
        month: Month filter (YYYY-MM).

    Returns:
        JSON response with the list of attendance records.
    """
    worker_id = request.args.get("worker_id", "")
    date = request.args.get("date", "")
    month = request.args.get("month", "")
    attendance = _worker_management_service.get_all_attendance(
        worker_id=int(worker_id) if worker_id.isdigit() else None,
        date=date or None,
        month=month or None,
    )
    return _json_ok(
        "Attendance records retrieved successfully",
        [record.to_dict() for record in attendance],
        200,
    )


@worker_management_bp.route("/attendance/", methods=["POST"])
@require_admin_or_manager
def create_attendance():
    """Create a new attendance record.

    Expects JSON body with attendance fields.

    Returns:
        JSON response with the created attendance record.
    """
    data = request.get_json()
    try:
        record = _worker_management_service.create_attendance(data)
        return _json_ok("Attendance record created successfully", record.to_dict(), 201)
    except ValueError as e:
        return _json_error(str(e), 400)


@worker_management_bp.route("/attendance/<int:attendance_id>", methods=["PUT"])
@require_admin_or_manager
def update_attendance(attendance_id):
    """Update an existing attendance record.

    Args:
        attendance_id: The unique identifier of the attendance record.

    Returns:
        JSON response with the updated attendance record.
    """
    data = request.get_json()
    try:
        record = _worker_management_service.update_attendance(attendance_id, data)
        return _json_ok("Attendance record updated successfully", record.to_dict(), 200)
    except ValueError as e:
        return _json_error(str(e), 400)


@worker_management_bp.route("/attendance/<int:attendance_id>", methods=["DELETE"])
@require_admin_or_manager
def delete_attendance(attendance_id):
    """Delete an attendance record.

    Args:
        attendance_id: The unique identifier of the attendance record.

    Returns:
        JSON response with the deletion result.
    """
    try:
        _worker_management_service.delete_attendance(attendance_id)
        return _json_ok("Attendance record deleted successfully", None, 200)
    except ValueError as e:
        return _json_error(str(e), 404)


# ----------------------------------------------------------------------
# Salaries
# ----------------------------------------------------------------------

@worker_management_bp.route("/salaries/", methods=["GET"])
@require_authenticated
def get_all_salaries():
    """Get all salary records with optional filters.

    Query params:
        worker_id: Worker id filter.
        period: Period filter (YYYY-MM).
        payment_status: Payment status filter.

    Returns:
        JSON response with the list of salary records.
    """
    worker_id = request.args.get("worker_id", "")
    period = request.args.get("period", "")
    payment_status = request.args.get("payment_status", "")
    salaries = _worker_management_service.get_all_salaries(
        worker_id=int(worker_id) if worker_id.isdigit() else None,
        period=period or None,
        payment_status=payment_status or None,
    )
    return _json_ok(
        "Salary records retrieved successfully",
        [salary.to_dict() for salary in salaries],
        200,
    )


@worker_management_bp.route("/salaries/", methods=["POST"])
@require_admin_or_manager
def create_salary():
    """Create a new salary record.

    Expects JSON body with salary fields.

    Returns:
        JSON response with the created salary record.
    """
    data = request.get_json()
    try:
        salary = _worker_management_service.create_salary(data)
        return _json_ok("Salary record created successfully", salary.to_dict(), 201)
    except ValueError as e:
        return _json_error(str(e), 400)


@worker_management_bp.route("/salaries/<int:salary_id>", methods=["PUT"])
@require_admin_or_manager
def update_salary(salary_id):
    """Update an existing salary record.

    Args:
        salary_id: The unique identifier of the salary record.

    Returns:
        JSON response with the updated salary record.
    """
    data = request.get_json()
    try:
        salary = _worker_management_service.update_salary(salary_id, data)
        return _json_ok("Salary record updated successfully", salary.to_dict(), 200)
    except ValueError as e:
        return _json_error(str(e), 400)


@worker_management_bp.route("/salaries/<int:salary_id>/pay", methods=["POST"])
@require_admin_or_manager
def mark_salary_paid(salary_id):
    """Mark a salary record as paid.

    Args:
        salary_id: The unique identifier of the salary record.

    Returns:
        JSON response with the updated salary record.
    """
    data = request.get_json(silent=True)
    try:
        salary = _worker_management_service.mark_salary_paid(salary_id, data)
        return _json_ok("Salary marked as paid successfully", salary.to_dict(), 200)
    except ValueError as e:
        return _json_error(str(e), 400)


@worker_management_bp.route("/salaries/<int:salary_id>", methods=["DELETE"])
@require_admin_or_manager
def delete_salary(salary_id):
    """Delete a salary record.

    Args:
        salary_id: The unique identifier of the salary record.

    Returns:
        JSON response with the deletion result.
    """
    try:
        _worker_management_service.delete_salary(salary_id)
        return _json_ok("Salary record deleted successfully", None, 200)
    except ValueError as e:
        return _json_error(str(e), 404)


# ----------------------------------------------------------------------
# Advances
# ----------------------------------------------------------------------

@worker_management_bp.route("/advances/", methods=["GET"])
@require_authenticated
def get_all_advances():
    """Get all advance records with optional filters.

    Query params:
        worker_id: Worker id filter.
        status: Status filter.

    Returns:
        JSON response with the list of advance records.
    """
    worker_id = request.args.get("worker_id", "")
    status = request.args.get("status", "")
    advances = _worker_management_service.get_all_advances(
        worker_id=int(worker_id) if worker_id.isdigit() else None,
        status=status or None,
    )
    return _json_ok(
        "Advance records retrieved successfully",
        [advance.to_dict() for advance in advances],
        200,
    )


@worker_management_bp.route("/advances/", methods=["POST"])
@require_admin_or_manager
def create_advance():
    """Create a new advance record.

    Expects JSON body with advance fields.

    Returns:
        JSON response with the created advance record.
    """
    data = request.get_json()
    try:
        advance = _worker_management_service.create_advance(data)
        return _json_ok("Advance record created successfully", advance.to_dict(), 201)
    except ValueError as e:
        return _json_error(str(e), 400)


@worker_management_bp.route("/advances/<int:advance_id>", methods=["PUT"])
@require_admin_or_manager
def update_advance(advance_id):
    """Update an existing advance record.

    Args:
        advance_id: The unique identifier of the advance record.

    Returns:
        JSON response with the updated advance record.
    """
    data = request.get_json()
    try:
        advance = _worker_management_service.update_advance(advance_id, data)
        return _json_ok("Advance record updated successfully", advance.to_dict(), 200)
    except ValueError as e:
        return _json_error(str(e), 400)


@worker_management_bp.route("/advances/<int:advance_id>", methods=["DELETE"])
@require_admin_or_manager
def delete_advance(advance_id):
    """Delete an advance record.

    Args:
        advance_id: The unique identifier of the advance record.

    Returns:
        JSON response with the deletion result.
    """
    try:
        _worker_management_service.delete_advance(advance_id)
        return _json_ok("Advance record deleted successfully", None, 200)
    except ValueError as e:
        return _json_error(str(e), 404)


# ----------------------------------------------------------------------
# Statistics and reports
# ----------------------------------------------------------------------

@worker_management_bp.route("/statistics", methods=["GET"])
@require_authenticated
def get_statistics():
    """Get worker management dashboard statistics.

    Returns:
        JSON response with worker management statistics.
    """
    statistics = _worker_management_service.get_statistics()
    return _json_ok(
        "Worker management statistics retrieved successfully",
        statistics,
        200,
    )


@worker_management_bp.route("/reports/attendance", methods=["GET"])
@require_authenticated
def get_attendance_report():
    """Get the attendance report within an optional date range.

    Query params:
        from: Start date (YYYY-MM-DD).
        to: End date (YYYY-MM-DD).

    Returns:
        JSON response with the attendance report rows.
    """
    from_date = request.args.get("from", "")
    to_date = request.args.get("to", "")
    report = _worker_management_service.get_attendance_report(
        from_date=from_date or None,
        to_date=to_date or None,
    )
    return _json_ok("Attendance report retrieved successfully", report, 200)


@worker_management_bp.route("/reports/salaries", methods=["GET"])
@require_authenticated
def get_salary_report():
    """Get the salary report within an optional period range.

    Query params:
        from: Start period (YYYY-MM).
        to: End period (YYYY-MM).

    Returns:
        JSON response with the salary report rows.
    """
    from_period = request.args.get("from", "")
    to_period = request.args.get("to", "")
    report = _worker_management_service.get_salary_report(
        from_period=from_period or None,
        to_period=to_period or None,
    )
    return _json_ok("Salary report retrieved successfully", report, 200)
