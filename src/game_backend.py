from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .infrai_client import InfraiClient


@dataclass(frozen=True)
class PlayerAsset:
    asset_id: str
    player_id: str
    title: str
    status: str = "pending"


@dataclass(frozen=True)
class LiveEvent:
    event_id: str
    title: str
    starts_at: str


@dataclass(frozen=True)
class ModerationQueue:
    asset_id: str
    reason: str


def publish_event_notice(event: LiveEvent, recipients: List[str], client: InfraiClient):
    """Notify players only after the event has been approved for publication."""
    if not event.title.strip() or not recipients:
        return []
    return [client.send_email(to, f"Live event: {event.title}",
                              f"<p>{event.title} starts at {event.starts_at}.</p>",
                              event.event_id + ":" + to) for to in recipients]

