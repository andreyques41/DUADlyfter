"""Calendar (.ics) export for appointments."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import re


def _dt_to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        # Treat naive datetimes as UTC (project stores naive timestamps)
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _ics_escape(value: str) -> str:
    # RFC5545 basic escaping
    value = value.replace("\\", "\\\\")
    value = value.replace(";", "\\;")
    value = value.replace(",", "\\,")
    value = value.replace("\r\n", "\\n").replace("\n", "\\n").replace("\r", "\\n")
    return value


@dataclass(frozen=True)
class IcsEvent:
    uid: str
    dtstart_utc: datetime
    dtend_utc: datetime
    summary: str
    description: str
    location: str
    url: str

    def to_ics(self) -> str:
        fmt = "%Y%m%dT%H%M%SZ"
        now = datetime.now(timezone.utc).strftime(fmt)

        return "\r\n".join(
            [
                "BEGIN:VCALENDAR",
                "VERSION:2.0",
                "PRODID:-//LyfterCook//EN",
                "CALSCALE:GREGORIAN",
                "BEGIN:VEVENT",
                f"UID:{_ics_escape(self.uid)}",
                f"DTSTAMP:{now}",
                f"DTSTART:{self.dtstart_utc.strftime(fmt)}",
                f"DTEND:{self.dtend_utc.strftime(fmt)}",
                f"SUMMARY:{_ics_escape(self.summary)}",
                f"DESCRIPTION:{_ics_escape(self.description)}",
                f"LOCATION:{_ics_escape(self.location)}" if self.location else "",
                f"URL:{_ics_escape(self.url)}" if self.url else "",
                "END:VEVENT",
                "END:VCALENDAR",
                "",
            ]
        )


class CalendarIcsService:
    @staticmethod
    def appointment_to_event(appointment, backend_url: str = "") -> IcsEvent:
        start = getattr(appointment, "scheduled_at", None)
        if not isinstance(start, datetime):
            raise ValueError("Appointment has no valid scheduled_at")

        start_utc = _dt_to_utc(start)
        duration = int(getattr(appointment, "duration_minutes", 60) or 60)
        end_utc = start_utc + timedelta(minutes=duration)

        title = getattr(appointment, "title", "Appointment") or "Appointment"
        description_parts = []
        if getattr(appointment, "description", None):
            description_parts.append(str(appointment.description))
        if getattr(appointment, "meeting_url", None):
            description_parts.append(f"Meeting: {appointment.meeting_url}")
        description = "\\n\\n".join(description_parts)

        url = ""
        if backend_url and getattr(appointment, "id", None) is not None:
            url = backend_url.rstrip("/") + f"/appointments/{appointment.id}"

        uid = f"appointment-{appointment.id}@lyftercook" if getattr(appointment, "id", None) else "appointment@lyftercook"
        location = getattr(appointment, "location", "") or ""

        return IcsEvent(
            uid=uid,
            dtstart_utc=start_utc,
            dtend_utc=end_utc,
            summary=str(title),
            description=str(description),
            location=str(location),
            url=str(url),
        )
