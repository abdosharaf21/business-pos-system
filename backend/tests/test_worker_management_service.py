"""Tests for Worker Management service business logic.

Covers salary computation, automatic advances deduction and settling,
duplicate detection, worker existence checks, and validation flows using
mocked repositories.
"""

from unittest.mock import MagicMock

import pytest

from backend.modules.worker_management.model import Advance, Salary, Worker
from backend.modules.worker_management.service import WorkerManagementService


class _FakeRepos:
    """Container holding fake repositories for the service."""

    def __init__(self):
        self.worker_repo = MagicMock()
        self.attendance_repo = MagicMock()
        self.salary_repo = MagicMock()
        self.advance_repo = MagicMock()
        self.worker_management_repo = MagicMock()


def _make_service(repos: _FakeRepos) -> WorkerManagementService:
    """Build a service wired to fake repositories.

    Args:
        repos: Container of fake repositories.

    Returns:
        WorkerManagementService instance.
    """
    return WorkerManagementService(
        repos.worker_repo,
        repos.attendance_repo,
        repos.salary_repo,
        repos.advance_repo,
        repos.worker_management_repo,
    )


class TestWorkerService:
    """Tests for worker business logic."""

    def test_create_worker_rejects_duplicate_phone(self):
        """Duplicate phone raises a business error."""
        repos = _FakeRepos()
        repos.worker_repo.exists_by_phone.return_value = True
        service = _make_service(repos)

        with pytest.raises(ValueError, match="phone number already exists"):
            service.create_worker({
                "full_name": "Ahmed Ali",
                "phone": "+201000000001",
            })

    def test_create_worker_success(self):
        """Valid worker is created through the repository."""
        repos = _FakeRepos()
        repos.worker_repo.exists_by_phone.return_value = False
        repos.worker_repo.create.side_effect = lambda worker: worker
        service = _make_service(repos)

        worker = service.create_worker({
            "full_name": "Ahmed Ali",
            "phone": "+201000000001",
            "base_salary": 5000,
        })

        assert worker.full_name == "Ahmed Ali"
        assert worker.base_salary == 5000.0
        repos.worker_repo.create.assert_called_once()

    def test_create_worker_defaults_base_salary_to_zero(self):
        """Missing base salary defaults to zero not None."""
        repos = _FakeRepos()
        repos.worker_repo.exists_by_phone.return_value = False
        repos.worker_repo.create.side_effect = lambda worker: worker
        service = _make_service(repos)

        worker = service.create_worker({
            "full_name": "Ahmed Ali",
            "phone": "+201000000001",
        })

        assert worker.base_salary == 0.0

    def test_get_worker_not_found(self):
        """Missing worker raises a business error."""
        repos = _FakeRepos()
        repos.worker_repo.get_by_id.return_value = None
        service = _make_service(repos)

        with pytest.raises(ValueError, match="Worker not found"):
            service.get_worker(999)

    def test_delete_worker_not_found(self):
        """Deleting a missing worker raises a business error."""
        repos = _FakeRepos()
        repos.worker_repo.delete.return_value = False
        service = _make_service(repos)

        with pytest.raises(ValueError, match="Worker not found"):
            service.delete_worker(999)


class TestAttendanceService:
    """Tests for attendance business logic."""

    def test_create_attendance_requires_worker(self):
        """Creating attendance for a missing worker raises an error."""
        repos = _FakeRepos()
        repos.worker_repo.get_by_id.return_value = None
        service = _make_service(repos)

        with pytest.raises(ValueError, match="Worker not found"):
            service.create_attendance({
                "worker_id": 999,
                "attendance_date": "2026-08-01",
            })

    def test_create_attendance_duplicate_rejected(self):
        """Duplicate attendance for a worker and date raises an error."""
        repos = _FakeRepos()
        repos.worker_repo.get_by_id.return_value = Worker(id=1, full_name="A")
        repos.attendance_repo.exists.return_value = True
        service = _make_service(repos)

        with pytest.raises(ValueError, match="already exists"):
            service.create_attendance({
                "worker_id": 1,
                "attendance_date": "2026-08-01",
            })

    def test_create_attendance_requires_date(self):
        """Missing attendance date raises an error."""
        repos = _FakeRepos()
        repos.worker_repo.get_by_id.return_value = Worker(id=1, full_name="A")
        repos.attendance_repo.exists.return_value = False
        service = _make_service(repos)

        with pytest.raises(ValueError, match="Attendance date is required"):
            service.create_attendance({"worker_id": 1})


class TestSalaryService:
    """Tests for salary business logic."""

    def test_create_salary_computes_net(self):
        """Net salary is base + bonuses - deductions - advances deduction."""
        repos = _FakeRepos()
        repos.worker_repo.get_by_id.return_value = Worker(id=1, full_name="A")
        repos.salary_repo.exists.return_value = False
        repos.advance_repo.outstanding_total.return_value = 0.0
        repos.salary_repo.create.side_effect = lambda salary: salary
        service = _make_service(repos)

        salary = service.create_salary({
            "worker_id": 1,
            "salary_period": "2026-07",
            "base_salary": 5000,
            "bonuses": 200,
            "deductions": 100,
            "advances_deduction": 0,
        })

        assert salary.net_amount == 5100.0

    def test_create_salary_auto_deducts_outstanding_advances(self):
        """Outstanding advances are deducted and advances are settled."""
        repos = _FakeRepos()
        repos.worker_repo.get_by_id.return_value = Worker(id=1, full_name="A")
        repos.salary_repo.exists.return_value = False
        repos.advance_repo.outstanding_total.return_value = 400.0
        repos.salary_repo.create.side_effect = lambda salary: salary
        service = _make_service(repos)

        salary = service.create_salary({
            "worker_id": 1,
            "salary_period": "2026-07",
            "base_salary": 5000,
        })

        assert salary.advances_deduction == 400.0
        assert salary.net_amount == 4600.0
        repos.advance_repo.settle_all_for_worker.assert_called_once_with(1)

    def test_create_salary_duplicate_period_rejected(self):
        """Duplicate worker and period raises an error."""
        repos = _FakeRepos()
        repos.worker_repo.get_by_id.return_value = Worker(id=1, full_name="A")
        repos.salary_repo.exists.return_value = True
        service = _make_service(repos)

        with pytest.raises(ValueError, match="already exists"):
            service.create_salary({
                "worker_id": 1,
                "salary_period": "2026-07",
                "base_salary": 5000,
            })

    def test_create_salary_requires_period(self):
        """Missing salary period raises an error."""
        repos = _FakeRepos()
        repos.worker_repo.get_by_id.return_value = Worker(id=1, full_name="A")
        repos.salary_repo.exists.return_value = False
        service = _make_service(repos)

        with pytest.raises(ValueError, match="Salary period is required"):
            service.create_salary({
                "worker_id": 1,
                "base_salary": 5000,
            })

    def test_create_salary_requires_worker(self):
        """Creating a salary for a missing worker raises an error."""
        repos = _FakeRepos()
        repos.worker_repo.get_by_id.return_value = None
        service = _make_service(repos)

        with pytest.raises(ValueError, match="Worker not found"):
            service.create_salary({
                "worker_id": 999,
                "salary_period": "2026-07",
                "base_salary": 5000,
            })

    def test_mark_salary_paid_updates_status_and_date(self):
        """Marking a salary paid sets status and payment date."""
        repos = _FakeRepos()
        salary = Salary(
            id=1,
            worker_id=1,
            salary_period="2026-07",
            base_salary=5000.0,
            payment_status="pending",
        )
        repos.salary_repo.get_by_id.return_value = salary
        repos.salary_repo.update.side_effect = lambda salary: salary
        service = _make_service(repos)

        updated = service.mark_salary_paid(1, {"payment_date": "2026-08-01"})

        assert updated.payment_status == "paid"
        assert updated.payment_date == "2026-08-01"


class TestAdvanceService:
    """Tests for advance business logic."""

    def test_create_advance_requires_worker(self):
        """Creating an advance for a missing worker raises an error."""
        repos = _FakeRepos()
        repos.worker_repo.get_by_id.return_value = None
        service = _make_service(repos)

        with pytest.raises(ValueError, match="Worker not found"):
            service.create_advance({
                "worker_id": 999,
                "amount": 100,
                "advance_date": "2026-07-01",
            })

    def test_create_advance_success(self):
        """Valid advance is created through the repository."""
        repos = _FakeRepos()
        repos.worker_repo.get_by_id.return_value = Worker(id=1, full_name="A")
        repos.advance_repo.create.side_effect = lambda advance: advance
        service = _make_service(repos)

        advance = service.create_advance({
            "worker_id": 1,
            "amount": 300,
            "advance_date": "2026-07-10",
        })

        assert advance.amount == 300.0
        assert advance.status == "pending"
        repos.advance_repo.create.assert_called_once()

    def test_create_advance_rejects_zero_amount(self):
        """Zero amount advance raises a validation error."""
        repos = _FakeRepos()
        repos.worker_repo.get_by_id.return_value = Worker(id=1, full_name="A")
        service = _make_service(repos)

        with pytest.raises(ValueError, match="greater than zero"):
            service.create_advance({
                "worker_id": 1,
                "amount": 0,
                "advance_date": "2026-07-10",
            })


class TestReports:
    """Tests for statistics and report delegation."""

    def test_statistics_delegates_to_repository(self):
        """Statistics are forwarded from the repository."""
        repos = _FakeRepos()
        repos.worker_management_repo.get_statistics.return_value = {"total_workers": 5}
        service = _make_service(repos)

        assert service.get_statistics() == {"total_workers": 5}

    def test_attendance_report_delegates_with_filters(self):
        """Attendance report forwards date filters to the repository."""
        repos = _FakeRepos()
        service = _make_service(repos)
        service.get_attendance_report("2026-07-01", "2026-07-31")
        repos.worker_management_repo.get_attendance_report.assert_called_once_with(
            from_date="2026-07-01",
            to_date="2026-07-31",
        )
