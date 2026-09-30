# 範例：比較有沒有加 User-Agent的差別（已完成，供參考）
import requests
 
 
def show_headers(url, headers=None, label=""):
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"{label}伺服器收到的 headers：")
        print(resp.json())
    except Exception as e:
        print(f"{label}請求失敗（httpbin.org 可能暫時連不上）：{e}")
 
 
show_headers("https://httpbin.org/headers", label="沒加 User-Agent，")
 
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
show_headers("https://httpbin.org/headers", headers=headers, label="加上 User-Agent 後，")