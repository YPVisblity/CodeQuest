"""
.py 原始碼 → .ipynb（給 views.py_to_ipynb 與 build_references.py 共用）

這個模組只把程式碼當「文字」切成 cell，不會執行上傳的程式。

切 cell 規則（與 VS Code / jupytext 的 percent 格式相同）：
    - 沒有任何標記時，整個檔案就是一個 code cell
    - "# %%"（或 "#%%"）開始新的 code cell，標記後面的文字當作 cell 標題，會被忽略
    - "# %% [markdown]"（或 "[md]"）底下變成 markdown cell，每行開頭的 "# " 會去掉
"""
import re

import nbformat

CELL_MARK = re.compile(r"^#[ \t]?%%(.*)$", re.MULTILINE)
MARKDOWN_TAG = re.compile(r"\[(markdown|md)\]", re.IGNORECASE)


def natural_key(name: str):
    # 讓 2_xxx.py 排在 10_xxx.py 前面（chapter-3-level-3-2 也排在 3-10 前面）。
    # split 的結果中奇數位置一定是數字段；只認 ASCII 數字，和 home.html 裡的 JS 排序一致。
    parts = re.split(r"([0-9]+)", name)
    return [int(t) if i % 2 else t.lower() for i, t in enumerate(parts)]


def decode_source(raw: bytes) -> str:
    # 學生在 Windows 用記事本存檔可能是 cp950（Big5），先試 UTF-8（含 BOM），失敗再退回
    for enc in ("utf-8-sig", "cp950"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("utf-8/cp950", raw, 0, len(raw), "無法辨識檔案編碼")


def source_to_cells(source: str) -> list:
    source = source.replace("\r\n", "\n").replace("\r", "\n")
    parts = CELL_MARK.split(source)  # [第一段, 標記1, 內容1, 標記2, 內容2, ...]
    chunks = [("", parts[0])] + list(zip(parts[1::2], parts[2::2]))

    cells = []
    for mark, body in chunks:
        body = body.strip("\n")
        if not body.strip():
            continue
        if MARKDOWN_TAG.search(mark):
            text = "\n".join(re.sub(r"^# ?", "", line) for line in body.splitlines())
            cells.append(nbformat.v4.new_markdown_cell(text))
        else:
            cells.append(nbformat.v4.new_code_cell(body))
    return cells


def build_notebook(sources: list[tuple[str, str]], label: bool = False) -> nbformat.NotebookNode:
    """sources: [(檔名, 原始碼), ...]，依給定順序拼成一本 notebook。

    label=True 時，每個檔案前面多一格 markdown 標出來源檔名。
    """
    cells = []
    for name, source in sources:
        if label:
            cells.append(nbformat.v4.new_markdown_cell(f"### {name}"))
        cells += source_to_cells(source)

    nb = nbformat.v4.new_notebook(cells=cells)
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    nb.metadata["language_info"] = {"name": "python"}
    nbformat.validate(nb)
    return nb
