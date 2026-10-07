上一關我們學會了如何偽裝成瀏覽器發送請求，這一關要學習「解析」抓回來的網頁內容。

請定義 extract_titles(html) 函式：
輸入是一段 HTML 字串
使用 BeautifulSoup 解析，找出所有 h2 標籤的文字內容
回傳一個 list，內容為每個 h2 的文字（依照原本順序）

提示：
from bs4 import BeautifulSoup
soup = BeautifulSoup(html, "html.parser")
soup.find_all("h2")  # 找出所有 h2 標籤
tag.get_text()       # 取出標籤內的文字