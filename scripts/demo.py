import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.game_backend import LiveEvent, publish_event_notice
from src.infrai_client import InfraiClient


def main() -> None:
    recipient = os.environ.get("DEMO_EMAIL_TO")
    domain = os.environ.get("SENDING_DOMAIN")
    if not recipient or not domain:
        raise SystemExit("Set DEMO_EMAIL_TO and SENDING_DOMAIN")
    client = InfraiClient()
    verification = client.verify_domain(domain)
    print("domain verification:", verification)
    event = LiveEvent("season-01", "Skyforge weekend", "2026-09-12T18:00:00Z")
    sent = publish_event_notice(event, [recipient], client)
    print("event notices:", sent)


if __name__ == "__main__":
    main()

