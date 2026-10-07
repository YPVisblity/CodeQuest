from unittest.mock import patch, MagicMock


def _fake_get(url, headers=None, **kwargs):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    _fake_get.captured_headers = headers
    return mock_resp


with patch("requests.get", side_effect=_fake_get):
    submit_status = fetch_with_header("https://example.com")

submit_headers = getattr(_fake_get, "captured_headers", None) or {}
submit_ua = submit_headers.get("User-Agent", "")

status_is_valid = (submit_status == 200)
has_user_agent_key = "User-Agent" in submit_headers
user_agent_is_valid = (
    "python-requests" not in submit_ua.lower()
    and any(keyword in submit_ua.lower() for keyword in ("mozilla", "chrome", "safari", "firefox", "edge"))
)

status_signature = ("chapter-2-level-3-1:status_is_valid", status_is_valid)
has_ua_signature = ("chapter-2-level-3-1:has_user_agent_key", has_user_agent_key)
ua_format_signature = ("chapter-2-level-3-1:user_agent_is_valid", user_agent_is_valid)