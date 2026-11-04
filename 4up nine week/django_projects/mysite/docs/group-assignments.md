# 群組作業與 PyBryt 批改

## 教師操作

1. 首頁 → 教師介面 → 群組管理，建立群組並加入學生。
2. 開啟群組，點選「建立／管理此群組的作業」。
3. 輸入作業名稱、題目說明，或上傳題目附件（PDF、Markdown、文字、Notebook）。
4. 上傳含 PyBryt 檢查點的教師參考答案 `.ipynb`；頁面提供可下載的 Notebook 範例。後台自動編譯成該作業的 `.pkl`。
5. 建立作業後，可選擇群組成員，上傳該學生的 `.ipynb`，立即交由 PyBryt 批改。
6. 作業頁保留每次上傳、上傳者、學生、時間及檢查點結果。遇到執行錯誤時可以重新批改。

## 學生操作

首頁 → 群組作業 → 所屬群組 → 作業，查看題目、下載附件並上傳 `.ipynb`。
每次繳交自動批改；學生只能看到自己的紀錄，無法下載教師參考檔或其他學生作業。
移出群組後，即無法進入該群組作業。

## 評分參考檔

參考 Notebook 需包含正確解法、測試呼叫及 `pybryt.Value` 等檢查點，例如：

```python
import pybryt

def value(x, y):
    return x * y if x > 0 and y > 0 else "ERROR"

result1 = value(26, 6)
result2 = value(5, 0)
pybryt.Value(result1, name="一般乘法", failure_message="請檢查乘法")
pybryt.Value(result2, name="零值處理", failure_message="請檢查零值")
```

後台沿用 `teacher/footprint.ipynb` 的 `ReferenceImplementation.compile()` 與 `dump()` 流程，但使用各份作業自己的檔案，不執行整份 footprint Notebook 或覆寫既有關卡參考檔。

- 轉檔在獨立背景程序中執行，限時 120 秒。沒有檢查點、執行錯誤或逾時時會提示教師，作業不發布。
- 只有教師能上傳及啟動參考 Notebook 轉檔。此流程經使用者明確同意，會以應用程式權限執行教師的程式；獨立程序不等同作業系統隔離。
- 不提供 `test.py` 上傳功能。學生 Notebook 應自行包含測試呼叫，例如 `result1 = value(26, 6)`，不能只有函式定義。
- PyBryt 比對執行過程中的記憶體值，並非只比對函式最終輸出。
- 不再接受 JSON 作為新作業參考檔；既有作業已產生的 `.pkl` 及測試程式保持有效。

## 儲存與維護

- 題目、參考檔及學生作業放在 `assignment_uploads/`，位於公開媒體目錄以外；下載由登入及群組權限檢查控制。
- 原有關卡及其批改流程繼續使用原本的參考檔。群組作業使用獨立紀錄，不計入原有關卡點數或解鎖。
- 每個上傳檔案上限 10 MB。批改沿用現有 PyBryt 與 Python Kernel 環境。
- 部署到其他環境時，執行 `python manage.py migrate`，並一併備份資料庫與 `assignment_uploads/`。
