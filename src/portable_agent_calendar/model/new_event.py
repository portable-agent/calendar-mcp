from dataclasses import dataclass, replace
from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


@dataclass(frozen=True, slots=True)
class NewEvent:
    tenant_id: str
    request_key: str
    title: str
    start_at: str
    end_at: str
    time_zone: str
    description: str | None = None
    attendees: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "tenant_id", str(UUID(self.tenant_id)))
        self._check_text()
        self._check_attendees()
        try:
            ZoneInfo(self.time_zone)
        except ZoneInfoNotFoundError as error:
            raise ValueError("timeZone is unknown") from error
        if self.start_time.tzinfo is None or self.end_time.tzinfo is None:
            raise ValueError("startAt and endAt must contain an offset")
        if self.end_time <= self.start_time:
            raise ValueError("endAt must be after startAt")

    @classmethod
    def from_text(
        cls,
        *,
        tenant_id: str,
        request_key: str,
        title: str,
        start_at: str,
        end_at: str,
        time_zone: str,
        description: str | None = None,
        attendees: list[str] | None = None,
    ) -> NewEvent:
        return cls(
            tenant_id=tenant_id,
            request_key=request_key,
            title=title,
            start_at=start_at,
            end_at=end_at,
            time_zone=time_zone,
            description=description,
            attendees=tuple(attendees or ()),
        )

    @property
    def start_time(self) -> datetime:
        return self._read_time(self.start_at, "startAt")

    @property
    def end_time(self) -> datetime:
        return self._read_time(self.end_at, "endAt")

    def with_title(self, title: str) -> NewEvent:
        return replace(self, title=title)

    def _check_text(self) -> None:
        if not self.request_key or len(self.request_key) > 128:
            raise ValueError("requestKey must contain 1 to 128 characters")
        if not self.title.strip() or len(self.title) > 200:
            raise ValueError("title must contain 1 to 200 characters")
        if len(self.time_zone) > 100:
            raise ValueError("timeZone must not be longer than 100 characters")
        if self.description is not None and len(self.description) > 2000:
            raise ValueError("description must not be longer than 2000 characters")

    def _check_attendees(self) -> None:
        if len(self.attendees) > 50:
            raise ValueError("attendees must not contain more than 50 values")
        if len(set(self.attendees)) != len(self.attendees):
            raise ValueError("attendees must be unique")
        if any(len(item) > 254 or "@" not in item for item in self.attendees):
            raise ValueError("attendees must contain email addresses")

    @staticmethod
    def _read_time(value: str, field: str) -> datetime:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as error:
            raise ValueError(f"{field} must be an ISO date-time") from error
