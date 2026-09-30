# 範例：解析並取出第一個 h1 標籤的文字（已完成，供參考）
from bs4 import BeautifulSoup

def get_first_h1(html):
    soup = BeautifulSoup(html, "html.parser")
    h1_tag = soup.find("h1")
    if h1_tag:
        return h1_tag.get_text()
    return None

sample_html = "<html><body><h1>歡迎光臨</h1><p>這是內文</p></body></html>"
print(get_first_h1(sample_html))  # 歡迎光臨