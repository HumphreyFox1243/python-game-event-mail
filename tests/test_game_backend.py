from src.game_backend import LiveEvent, publish_event_notice


class FakeClient:
    def __init__(self):
        self.calls = []

    def send_email(self, to, subject, html, request_id):
        self.calls.append((to, subject, html, request_id))
        return {"message_id": "m-1"}


def test_empty_event_is_not_sent():
    client = FakeClient()
    result = publish_event_notice(LiveEvent("e1", "", "2026-09-12T18:00:00Z"), ["a@example.com"], client)
    assert result == []
    assert client.calls == []


def test_approved_event_notifies_each_recipient():
    client = FakeClient()
    result = publish_event_notice(LiveEvent("e1", "Skyforge weekend", "2026-09-12T18:00:00Z"),
                                  ["a@example.com", "b@example.com"], client)
    assert [item["message_id"] for item in result] == ["m-1", "m-1"]
    assert [call[0] for call in client.calls] == ["a@example.com", "b@example.com"]

