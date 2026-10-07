# Code Quest Django 網站逐行講解簡報稿

---

## 1. 專題目標

這個網站是一個遊戲式學習平台。

使用者流程：

1. 進入首頁
2. 點擊「開始遊戲」
3. 選擇章節關卡
4. 進入關卡後切換「劇情、遊戲、討論區、關卡統計」
5. 在遊戲頁提交程式碼到 Django 後端

講解檔案：

- `pages/views.py`
- `pages/templates/pages/home.html`

---

## 2. Django 架構分工

`views.py` 負責後端資料與邏輯。

`home.html` 負責前端畫面與互動。

整體分工：

- 關卡資料存在 `views.py`
- Django 把資料傳給 `home.html`
- `home.html` 用 HTML/CSS/JavaScript 顯示遊戲介面
- 使用者提交程式碼後，後端存成 `.py` 檔案

---

## 3. views.py 第 1-3 行：匯入 Python 工具

```python
import json
from datetime import datetime
from pathlib import Path
```

逐行說明：

- 第 1 行：匯入 `json`，用來把 Python 字典轉成 JavaScript 可以讀的 JSON。
- 第 2 行：匯入 `datetime`，用來產生提交檔案的時間戳記。
- 第 3 行：匯入 `Path`，用比較乾淨的方式處理資料夾與檔案路徑。

---

## 4. views.py 第 5-8 行：匯入 Django 功能

```python
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
```

逐行說明：

- 第 5 行：`settings` 可以取得 Django 專案設定，例如 `BASE_DIR`。
- 第 6 行：`JsonResponse` 用來回傳 JSON 給前端 JavaScript。
- 第 7 行：`render` 用來把 template HTML 回傳給瀏覽器。
- 第 8 行：`csrf_exempt` 暫時關閉 CSRF 檢查，讓前端提交程式碼時比較容易測試。

注意：

正式上線時不建議直接使用 `csrf_exempt`，應改成 CSRF token 或登入驗證。

---

## 5. views.py 第 11-102 行：LEVELS 關卡資料

```python
LEVELS = [
    {
        "id": "chapter-1-level-1",
        "chapter": "第 1 章第一關",
        "level": "1-1",
        "title": "變數港口",
        "difficulty": "20％",
        "story_url": "...",
        "game_url": "...",
        "summary": "1-1描述",
    },
]
```

這裡是一個 list，裡面放很多 dictionary。

每一個 dictionary 代表一個小關。

欄位說明：

- `id`：關卡唯一代號，JavaScript 用它辨識使用者點了哪一關。
- `chapter`：顯示章節名稱。
- `level`：顯示小關編號。
- `title`：關卡標題。
- `difficulty`：難度百分比。
- `story_url`：劇情 iframe 的網址，未來可接 Ren'Py。
- `game_url`：遊戲 iframe 的網址，未來可接 Jupyter Notebook。
- `summary`：關卡統計裡顯示的描述。

---

## 6. views.py 第 105-114 行：home 首頁 view

```python
def home(request):
    levels_by_id = {level["id"]: level for level in LEVELS}
    return render(
        request,
        "pages/home.html",
        {
            "levels": LEVELS,
            "levels_json": json.dumps(levels_by_id, ensure_ascii=False),
        },
    )
```

逐行說明：

- 第 105 行：定義首頁函式，當使用者進入 `/` 時執行。
- 第 106 行：把 `LEVELS` 轉成以 `id` 為 key 的字典，方便 JavaScript 查資料。
- 第 107-114 行：使用 `render()` 回傳 `pages/home.html`。

傳到 template 的資料：

- `levels`：給 Django template 的 `{% for %}` 迴圈使用。
- `levels_json`：給前端 JavaScript 使用。

---

## 7. views.py 第 117-120 行：提交 API 開頭

```python
@csrf_exempt
def submit_solution(request):
    if request.method != "POST":
        return JsonResponse({"message": "Only POST requests are accepted."}, status=405)
```

逐行說明：

- 第 117 行：暫時免除 CSRF 驗證。
- 第 118 行：建立提交程式碼用的 view。
- 第 119 行：檢查使用者是不是用 POST。
- 第 120 行：如果不是 POST，就回傳錯誤狀態 `405`。

---

## 8. views.py 第 122-127 行：接收表單資料

```python
level = request.POST.get("level", "unknown-level").replace("/", "-").replace("\\", "-")
player = request.POST.get("player", "player").replace("/", "-").replace("\\", "-")
code = request.POST.get("code", "").strip()

if not code:
    return JsonResponse({"message": "請先輸入要提交的程式碼。"}, status=400)
```

逐行說明：

- `level`：接收目前關卡 id。
- `player`：接收玩家名稱。
- `code`：接收玩家貼上的程式碼。
- `replace()`：避免使用者輸入 `/` 或 `\` 影響檔案路徑。
- `strip()`：去掉前後空白。
- 如果 `code` 是空的，就回傳錯誤。

---

## 9. views.py 第 129-134 行：建立提交檔案

```python
submitted_at = datetime.now().strftime("%Y%m%d-%H%M%S")
submissions_dir = Path(settings.BASE_DIR) / "submissions"
submissions_dir.mkdir(exist_ok=True)
filename = f"{submitted_at}_{level}_{player}.py"
file_path = submissions_dir / filename
file_path.write_text(code + "\n", encoding="utf-8")
```

逐行說明：

- 第 129 行：產生時間字串，例如 `20260518-103000`。
- 第 130 行：設定存檔資料夾為 `mysite/submissions`。
- 第 131 行：如果資料夾不存在就建立。
- 第 132 行：組合檔名。
- 第 133 行：組合完整檔案路徑。
- 第 134 行：把程式碼寫入 `.py` 檔案。

---

## 10. views.py 第 136-141 行：回傳儲存結果

```python
return JsonResponse(
    {
        "message": f"已儲存到後端 submissions/{filename}",
        "filename": filename,
    }
)
```

這段會回傳 JSON 給前端。

前端收到後會顯示：

```text
已儲存到後端 submissions/檔名.py
```

---

## 11. home.html 第 1-7 行：HTML 基本架構

```html
<!doctype html>
<html lang="zh-Hant">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Code Quest</title>
    <style>
```

逐行說明：

- 第 1 行：宣告 HTML5 文件。
- 第 2 行：設定語言為繁體中文。
- 第 4 行：使用 UTF-8，避免中文亂碼。
- 第 5 行：讓網頁在手機上正常縮放。
- 第 6 行：瀏覽器分頁標題。
- 第 7 行：開始撰寫 CSS。

---

## 12. home.html 第 8-33 行：全域基本 CSS

重點：

- `box-sizing: border-box`：讓寬高計算更直覺。
- `scroll-behavior: smooth`：點擊後捲動更平滑。
- `body` 設定整體字型、背景、文字顏色。
- `button` 設定滑鼠移過去會變手指。

這一段是整個網站的基本視覺設定。

---

## 13. home.html 第 35-40 行：主背景

```css
.shell {
    min-height: 100vh;
    background:
        linear-gradient(135deg, rgba(16, 37, 54, 0.92), rgba(7, 18, 30, 0.84)),
        url("/static/pages/images/mainbackground.png") center/cover no-repeat;
}
```

逐行說明：

- `.shell` 是整個頁面的外層容器。
- `min-height: 100vh` 代表至少填滿整個螢幕高度。
- `linear-gradient(...)` 是半透明遮罩，讓文字比較清楚。
- `url(...)` 是背景圖片位置。
- `center/cover no-repeat` 代表圖片置中、填滿、不重複。

要換背景圖就改這一行：

```css
url("/static/pages/images/mainbackground.png")
```

---

## 14. home.html 第 42-69 行：上方導覽列

重點：

- `.topbar` 是上方固定導覽列。
- `position: sticky` 讓導覽列捲動時黏在上方。
- `.top-actions` 放登入、登出、管理按鈕。

目前 HTML 裡第 464-477 行會真正顯示導覽列。

---

## 15. home.html 第 71-100 行：按鈕樣式

這裡定義四種常用按鈕：

- `.nav-pill`：導覽列按鈕
- `.primary-button`：主要按鈕，例如「開始遊戲」
- `.secondary-button`：次要按鈕，例如「返回首頁」
- `.tab-button`：關卡裡的分頁按鈕

視覺特色：

- 圓角 8px
- 粗體
- 主要按鈕使用綠色，並用 `box-shadow` 做出立體感

---

## 16. home.html 第 102-137 行：開始畫面

這一段控制首頁開始畫面：

- `.start-screen`：把內容置中。
- `.start-card`：限制內容寬度。
- `.title-frame`：標題外框。
- `h1`：大標題。
- `.subtitle`：副標題。

對應 HTML：

```html
<section class="start-screen" id="startScreen">
    ...
    <h1>pybryt</h1>
    <button>開始遊戲</button>
</section>
```

---

## 17. home.html 第 139-213 行：章節地圖區

重點：

- `.map-screen` 預設 `display: none`，所以一開始看不到地圖。
- 按下開始遊戲後，JavaScript 會加上 `is-active`。
- `.map-window` 是可以橫向捲動的地圖視窗。
- `.map-track` 使用 `display: flex` 讓關卡橫向排列。
- `.map-track::before` 畫出連接關卡的路線。

這就是橫向關卡地圖的核心。

---

## 18. home.html 第 215-281 行：關卡島嶼樣式

這一段控制每個關卡按鈕的外觀。

重點：

- `.level-node`：每個關卡按鈕。
- `transform: translateY(...)`：讓關卡上下錯開，像地圖節點。
- `.level-island`：島嶼外型。
- `.level-icon`：島嶼中間的數字。
- `.level-name`：關卡名稱。
- `.level-code`：章節與小關編號。

---

## 19. home.html 第 283-358 行：關卡面板與 iframe

重點：

- `.detail-panel` 預設隱藏。
- `.detail-panel.is-open` 顯示關卡面板。
- `.tabs` 是劇情、遊戲、討論區、統計的分頁。
- `.iframe-wrap` 包住 iframe。
- `iframe` 用來嵌入 Ren'Py 或 Jupyter Notebook。

也就是說：

- 劇情頁顯示 `story_url`
- 遊戲頁顯示 `game_url`

---

## 20. home.html 第 360-425 行：統計卡片與提交表單

重點：

- `.stats-grid` 用三欄顯示關卡統計。
- `.paper-card` 是統計卡片。
- `.submit-grid` 把程式碼輸入區和提交按鈕分成兩欄。
- `textarea` 是使用者貼程式碼的地方。
- `.status` 顯示儲存成功或失敗訊息。

---

## 21. home.html 第 436-459 行：RWD 響應式

```css
@media (max-width: 880px) {
    ...
}
```

這段代表當螢幕寬度小於 880px 時套用。

目的：

- 手機上導覽列改成直向排列。
- 地圖區縮小左右 padding。
- 統計卡片和提交表單改成單欄。

---

## 22. home.html 第 464-477 行：登入與登出顯示

```django
{% if user.is_authenticated %}
    <span class="user-name">{{ user.username }}</span>
    <form action="{% url 'logout' %}" method="post">
        {% csrf_token %}
        <button>登出</button>
    </form>
{% else %}
    <a href="{% url 'login' %}">登入</a>
{% endif %}
```

逐行說明：

- 如果使用者已登入，顯示使用者名稱和登出按鈕。
- 如果尚未登入，顯示登入連結。
- `{% csrf_token %}` 是 Django 表單安全機制。
- `{% url 'login' %}` 和 `{% url 'logout' %}` 會對應到 `urls.py` 裡的登入登出路由。

---

## 23. home.html 第 479-486 行：開始畫面 HTML

```html
<section class="start-screen" id="startScreen">
    <div class="start-card">
        <div class="title-frame">
            <h1>pybryt</h1>
        </div>
        <button class="primary-button" id="startButton">開始遊戲</button>
    </div>
</section>
```

講解：

- `id="startScreen"` 讓 JavaScript 可以找到開始畫面。
- `<h1>pybryt</h1>` 是首頁大標題。
- `id="startButton"` 是開始遊戲按鈕，JavaScript 會監聽它的 click 事件。

---

## 24. home.html 第 496-508 行：用 Django 產生關卡

```django
{% for level in levels %}
    <button class="level-node" data-level="{{ level.id }}">
        ...
        <span class="level-name">{{ level.title }}</span>
        <span class="level-code">{{ level.chapter }} · {{ level.level }}</span>
    </button>
{% endfor %}
```

逐行說明：

- `{% for level in levels %}`：逐一讀取 `views.py` 傳來的關卡資料。
- `data-level="{{ level.id }}"`：把關卡 id 存在 HTML 屬性中。
- `{{ level.title }}`：顯示關卡名稱。
- `{{ level.chapter }}` 和 `{{ level.level }}`：顯示章節與小關編號。
- `{% endfor %}`：結束迴圈。

優點：

以後只要改 `views.py` 的 `LEVELS`，畫面會自動更新。

---

## 25. home.html 第 510-527 行：關卡內容面板

面板包含：

- 關卡標題 `levelTitle`
- 關卡資訊 `levelMeta`
- 關閉按鈕
- 四個分頁按鈕
- `tabBody`，用來動態放入分頁內容

四個分頁：

- 劇情
- 遊戲
- 討論區
- 關卡統計

---

## 26. home.html 第 531-545 行：JavaScript 初始資料

```javascript
const levels = {{ levels_json|safe }};
let selectedLevel = "chapter-1-level-1";
let selectedTab = "story";
```

逐行說明：

- `levels`：取得 Django 傳來的 JSON 關卡資料。
- `|safe`：告訴 Django 這段 JSON 不要轉義，讓它能變成真正的 JavaScript 物件。
- `selectedLevel`：預設選擇第一關。
- `selectedTab`：預設顯示劇情分頁。

---

## 27. home.html 第 547-611 行：renderTab 函式

`renderTab()` 是整個互動系統的核心。

它做三件事：

1. 讀取目前選到的關卡資料
2. 更新關卡標題與按鈕狀態
3. 根據目前分頁顯示不同內容

分頁判斷：

- `story`：顯示 Ren'Py iframe
- `game`：顯示 Jupyter iframe 和提交表單
- `discussion`：跳轉到 `/blog/`
- `stats`：顯示章節、小關、關卡重點

---

## 28. home.html 第 560-567 行：劇情分頁

```javascript
if (selectedTab === "story") {
    tabBody.innerHTML = `
        <div class="iframe-wrap">
            <iframe src="${level.story_url}" title="${level.title} 劇情"></iframe>
        </div>
    `;
    return;
}
```

說明：

- 如果目前分頁是劇情，就建立 iframe。
- iframe 的網址來自 `level.story_url`。
- 未來 Ren'Py 網址改掉，只要改 `views.py` 的 `story_url`。

---

## 29. home.html 第 569-587 行：遊戲分頁

遊戲分頁顯示兩個東西：

1. Jupyter Notebook iframe
2. 程式碼提交表單

重點：

- `iframe src="${level.game_url}"`：嵌入 Jupyter。
- `textarea`：讓使用者貼上程式碼。
- `submitButton`：點擊後呼叫 `bindSubmit()` 綁定提交事件。

---

## 30. home.html 第 590-592 行：討論區分頁

```javascript
if (selectedTab === "discussion") {
    window.location.href = "/blog/";
    return;
}
```

這段很直接：

- 使用者點「討論區」
- 瀏覽器跳到 `/blog/`
- `/blog/` 是 Django 專案裡既有的 blog app

---

## 31. home.html 第 595-610 行：關卡統計分頁

統計分頁顯示：

- 章節
- 小關
- 關卡重點

資料來源都是 `views.py` 的 `LEVELS`。

---

## 32. home.html 第 613-619 行：openLevel 函式

```javascript
function openLevel(levelId) {
    selectedLevel = levelId;
    selectedTab = "story";
    detailPanel.classList.add("is-open");
    renderTab();
    detailPanel.scrollIntoView({ behavior: "smooth", block: "start" });
}
```

逐行說明：

- 設定目前選到的關卡。
- 每次點新關卡都先回到劇情分頁。
- 顯示關卡面板。
- 呼叫 `renderTab()` 更新內容。
- 自動捲動到關卡面板。

---

## 33. home.html 第 621-649 行：bindSubmit 函式

這是把玩家程式碼送到 Django 後端的函式。

流程：

1. 找到提交按鈕
2. 使用者點擊後讀取玩家名稱與程式碼
3. 用 `fetch()` POST 到 `/submit-solution/`
4. 等後端回傳 JSON
5. 顯示成功或失敗訊息

---

## 34. home.html 第 651-675 行：按鈕事件

這一段把畫面按鈕接上互動。

- 點 `startButton`：隱藏首頁，顯示地圖。
- 點 `backButton`：回到首頁。
- 點 `closePanel`：關閉關卡面板。
- 點 `.level-node`：開啟指定關卡。
- 點 `.tab-button`：切換分頁。

---

## 35. 總結

這個專案目前已完成：

- Django template 頁面
- 3 章 x 3 小關資料
- 橫向地圖選關
- 劇情 iframe
- 遊戲 iframe
- 討論區導向 blog
- 關卡統計
- 程式碼提交到後端
- 登入/登出顯示

---

## 36. 可以繼續優化的地方

下一步可以做：

- 把 CSS 拆到 static 檔案
- 把 JavaScript 拆到 static 檔案
- 讓關卡資料改用 database model
- 討論區改成真正依關卡分類
- 提交程式碼改成只允許登入使用者使用
- 移除 `csrf_exempt`，改成正式 CSRF token

