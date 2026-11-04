"""
一鍵把各題的 reference.py 編成 PyBryt 參考答案 (.pkl)，可選擇順便輸出 .ipynb。

放置位置：mysite/build_references.py（與 manage.py 同層）

約定：
    levels/<level>/topics/<topic-id>/reference.py   ← 老師的參考解 + pybryt 註記
    用 "# %%" 分隔 cell（可省略，整個檔案就是一個 cell），切法與網站上的「.py 轉 .ipynb」相同

用法（在 mysite/ 底下執行）：
    python build_references.py                       # 編譯全部 → references/<topic-id>.pkl
    python build_references.py chapter-1-level-2-2   # 只編指定題目（可多個）
    python build_references.py --ipynb               # 另外輸出 teacher/generated/<topic-id>.ipynb
    python build_references.py --ipynb-only          # 只轉 .ipynb，不編 .pkl
    python build_references.py --out D:/tmp/refs     # .pkl 輸出到別的資料夾（先比對、不動正式檔）

注意：
    - 覆寫 references/ 裡已存在的 .pkl 之前，會先把舊檔備份成 <topic-id>.pkl.bak。
    - 參考解會在這個程式的行程裡執行（PyBryt 的 compile 就是 exec 原始碼），
      執行時的工作目錄是該題的資料夾，所以參考解可以用相對路徑讀同資料夾的測試檔。
"""
import argparse
import os
import shutil
import sys
from contextlib import contextmanager
from pathlib import Path

# 參考解若有 plt.show()，不要跳出視窗卡住批次編譯
os.environ.setdefault("MPLBACKEND", "Agg")

import nbformat

from pages.py2ipynb import build_notebook, decode_source

BASE_DIR = Path(__file__).resolve().parent
LEVELS_DIR = BASE_DIR / "levels"
REFERENCES_DIR = BASE_DIR / "references"
NB_OUT_DIR = BASE_DIR / "teacher" / "generated"


def py_to_notebook(py_path: Path) -> nbformat.NotebookNode:
    # 不直接用 pybryt.ReferenceImplementation.compile("x.py")：它內部用 open() 不帶 encoding，
    # Windows（cp950）遇到中文註解會 UnicodeDecodeError。這裡自己讀成文字、轉成 notebook。
    return build_notebook([(py_path.name, decode_source(py_path.read_bytes()))])


@contextmanager
def working_directory(path: Path):
    old = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old)


def find_topics(only: set[str]) -> list[tuple[str, Path]]:
    found = []
    for ref_py in sorted(LEVELS_DIR.glob("*/topics/*/reference.py")):
        topic_id = ref_py.parent.name
        if not only or topic_id in only:
            found.append((topic_id, ref_py))
    missing = only - {topic_id for topic_id, _ in found}
    for topic_id in sorted(missing):
        print(f"  ! 找不到 {topic_id} 的 reference.py，略過")
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description="把 levels/*/topics/*/reference.py 編成 PyBryt .pkl")
    ap.add_argument("topics", nargs="*", help="只處理這些 topic id")
    ap.add_argument("--ipynb", action="store_true", help="另外輸出 .ipynb 到 teacher/generated/")
    ap.add_argument("--ipynb-only", action="store_true", help="只輸出 .ipynb，不編 .pkl")
    ap.add_argument("--out", type=Path, default=REFERENCES_DIR, help="輸出 .pkl 的資料夾（預設 references/）")
    args = ap.parse_args()

    topics = find_topics(set(args.topics))
    if not topics:
        print("找不到任何 reference.py（或指定的 topic id 不存在）")
        return 1

    out_dir = args.out.resolve()
    if not args.ipynb_only:
        import pybryt  # 延後 import，--ipynb-only 不需要裝 pybryt
        out_dir.mkdir(parents=True, exist_ok=True)
    if args.ipynb or args.ipynb_only:
        NB_OUT_DIR.mkdir(parents=True, exist_ok=True)

    failed = []
    for topic_id, ref_py in topics:
        try:
            nb = py_to_notebook(ref_py)

            if args.ipynb or args.ipynb_only:
                nbformat.write(nb, str(NB_OUT_DIR / f"{topic_id}.ipynb"))

            if args.ipynb_only:
                print(f"OK  {topic_id}  -> .ipynb")
                continue

            with working_directory(ref_py.parent):
                ref = pybryt.ReferenceImplementation.compile(nb, name=topic_id)
            if isinstance(ref, list):
                raise ValueError(f"產生了 {len(ref)} 個 reference，一題只能有一個")
            n = len(ref.annotations)
            if n == 0:
                raise ValueError("沒有任何 pybryt 註記（pybryt.Value / ReturnValue ...），不產生 .pkl")

            pkl_path = out_dir / f"{topic_id}.pkl"
            if pkl_path.exists():
                shutil.copy2(pkl_path, pkl_path.with_name(pkl_path.name + ".bak"))
            ref.dump(str(pkl_path))
            print(f"OK  {topic_id}  ({n} annotations)")
        except Exception as e:
            failed.append(topic_id)
            print(f"ERR {topic_id}: {type(e).__name__}: {e}")

    print(f"\n完成 {len(topics) - len(failed)}/{len(topics)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
