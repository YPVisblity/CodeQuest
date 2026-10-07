def fetch_with_header(url):
    """建立帶有 User-Agent 的 headers，發送請求並回傳 status_code"""
    # TODO 1：建立 headers 字典，加入 User-Agent 來模擬瀏覽器
    headers = {
        # "User-Agent": "?"
    }

    # TODO 2：使用 requests.get，並把 headers 帶進去
    response = None

    # TODO 3：回傳 response 的狀態碼
    return None


# ===== 自我檢查 =====
from unittest.mock import patch, MagicMock


def _fake_get(url, headers=None, **kwargs):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    _fake_get.captured_headers = headers
    return mock_resp


with patch("requests.get", side_effect=_fake_get):
    check_status = fetch_with_header("https://example.com")

check_headers = getattr(_fake_get, "captured_headers", None) or {}
check_ua = check_headers.get("User-Agent", "")

assert check_status == 200, "函式沒有正確回傳 response 的狀態碼，請確認有 return response.status_code。"
assert "User-Agent" in check_headers, "headers 字典裡沒有找到 User-Agent 這個 key，請檢查拼字（大小寫要對）。"
assert "python-requests" not in check_ua.lower() and any(
    keyword in check_ua.lower() for keyword in ("mozilla", "chrome", "safari", "firefox", "edge")
), "User-Agent 字串不像瀏覽器（或還是預設值），請參考題目提示的格式。"

print("恭喜通過！你已經學會如何用 User-Agent 偽裝成瀏覽器")