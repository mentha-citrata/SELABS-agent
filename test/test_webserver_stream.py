"""Structured SSE tests for the Agent webserver."""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
for site_packages in (PROJECT_ROOT / ".venv" / "lib").glob("python*/site-packages"):
    sys.path.insert(0, str(site_packages))

from src.webserver import (
    _format_sse_event,
    _format_done_sse_event,
    _message_events_from_agent_text,
    _extract_a2ui_blocks,
    SESSIONS,
)


def test_format_sse_event_serializes_data_event():
    event = _format_sse_event({"type": "markdown_delta", "message_id": "m1", "content": "hello"})

    assert event.startswith("data: ")
    assert event.endswith("\n\n")
    payload = json.loads(event.removeprefix("data: ").strip())
    assert payload == {"type": "markdown_delta", "message_id": "m1", "content": "hello"}


def test_format_done_sse_event_has_data_payload():
    event = _format_done_sse_event()

    assert event == "event: done\ndata: {}\n\n"


def test_message_events_from_plain_text():
    events = list(_message_events_from_agent_text("hello world", message_id="m1"))

    assert events[0] == {"type": "message_start", "message_id": "m1"}
    assert events[1] == {"type": "markdown_delta", "message_id": "m1", "content": "hello world"}
    assert events[-1] == {"type": "message_done", "message_id": "m1"}


def test_extract_a2ui_block_from_fenced_json():
    text = """请填写预约信息。

```a2ui
{"kind":"form","id":"seat","title":"预约机位","fields":[{"name":"roomName","label":"房间","type":"text","required":true}]}
```

提交后我会继续处理。"""

    markdown, blocks = _extract_a2ui_blocks(text)

    assert "```a2ui" not in markdown
    assert "请填写预约信息。" in markdown
    assert blocks == [
        {
            "kind": "form",
            "id": "seat",
            "title": "预约机位",
            "fields": [
                {
                    "name": "roomName",
                    "label": "房间",
                    "type": "text",
                    "required": True,
                }
            ],
        }
    ]


def test_message_events_preserve_markdown_then_emit_ui_block():
    text = """请填写预约信息。

```a2ui
{"kind":"form","id":"seat","title":"预约机位","fields":[]}
```

提交后我会继续处理。"""

    events = list(_message_events_from_agent_text(text, message_id="m2"))

    assert [event["type"] for event in events] == [
        "message_start",
        "markdown_delta",
        "ui_block",
        "message_done",
    ]
    assert events[1]["content"] == "请填写预约信息。\n\n\n\n提交后我会继续处理。"
    assert events[2]["block"] == {
        "kind": "form",
        "id": "seat",
        "title": "预约机位",
        "fields": [],
    }


def test_invalid_a2ui_json_stays_in_markdown():
    text = """请填写预约信息。

```a2ui
{"kind":"form","id":
```
"""

    markdown, blocks = _extract_a2ui_blocks(text)

    assert blocks == []
    assert "```a2ui" in markdown


def test_session_store_survives_stream_completion_marker():
    session_id = "test-session"
    SESSIONS[session_id] = {"queue": None, "auth": {"is_authenticated": True}}

    try:
        assert session_id in SESSIONS
    finally:
        SESSIONS.pop(session_id, None)


def main():
    test_format_sse_event_serializes_data_event()
    test_format_done_sse_event_has_data_payload()
    test_message_events_from_plain_text()
    test_extract_a2ui_block_from_fenced_json()
    test_message_events_preserve_markdown_then_emit_ui_block()
    test_invalid_a2ui_json_stays_in_markdown()
    test_session_store_survives_stream_completion_marker()
    print("structured SSE tests passed")


if __name__ == "__main__":
    main()
