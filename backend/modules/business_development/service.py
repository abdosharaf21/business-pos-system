"""Service for Business Development dashboard aggregation."""


class BusinessDevelopmentService:
    """Delegates dashboard statistics to the repository."""

    def __init__(self, repository):
        self._repo = repository

    def get_statistics(self) -> dict:
        return self._repo.get_statistics()
