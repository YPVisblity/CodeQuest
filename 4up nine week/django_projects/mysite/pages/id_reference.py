"""Build portable PyBryt references with deterministic, user-specific inputs."""
import contextlib
import copy
import io
import sys


class ExpectedTransform:
    """依學生 ID 重算某個檢查點的正確答案。

    用「模組層級的類別」而不是 closure：dill 會把類別存成 pages.id_reference.ExpectedTransform
    的參照，pkl 裡只留下原始碼字串，不含 bytecode。closure 會把 bytecode 一起存進 pkl，
    換一個 Python 版本（例如 3.12 產生、3.10 載入）就會出現 SystemError: unknown opcode。
    載入 pkl 的程式需要能 import pages（Django 伺服器本身就可以）。
    """

    def __init__(self, solution_source, test_source, checkpoint, cache):
        self.solution_source = solution_source
        self.test_source = test_source
        self.checkpoint = checkpoint
        self.cache = cache  # 同一題的所有檢查點共用，同一個 ID 只需執行一次參考解

    def __call__(self, user_id):
        user_id = int(user_id)
        cache = self.cache
        if user_id not in cache:
            namespace = {"std_id3n": user_id, "__name__": "__id_reference__"}
            with contextlib.redirect_stdout(io.StringIO()):
                before = set(sys.modules.get("matplotlib.pyplot").get_fignums()) if "matplotlib.pyplot" in sys.modules else set()
                try:
                    exec(self.solution_source, namespace)
                    exec(self.test_source, namespace)
                    cache.clear()  # Bound memory; a loaded reference only keeps the most recent ID.
                    cache[user_id] = copy.deepcopy(namespace["_id_observations"])
                finally:
                    if "matplotlib.pyplot" in sys.modules:
                        plt = sys.modules["matplotlib.pyplot"]
                        for number in set(plt.get_fignums()) - before:
                            plt.close(number)
        return copy.deepcopy(cache[user_id][self.checkpoint])


def make_expected_transform(solution_source, test_source, checkpoint, cache):
    return ExpectedTransform(solution_source, test_source, checkpoint, cache)

def build_reference(topic_id, solution_source, test_source):
    import json
    from pathlib import Path

    messages = json.loads(Path(__file__).with_name("id_success_messages.json").read_text(encoding="utf-8"))
    topic_messages = messages.get(topic_id, {})
    import pybryt
    namespace = {"std_id3n": 0, "__name__": "__id_reference_preview__"}
    exec(solution_source, namespace)
    exec(test_source, namespace)
    cache = {}
    annotations = []
    for checkpoint in namespace["_id_observations"]:
        initial = pybryt.InitialCondition("cq_user_id")
        transform = make_expected_transform(solution_source, test_source, checkpoint, cache)
        annotations.append(pybryt.Value(
            initial.apply(transform), name=topic_messages.get(checkpoint, checkpoint),
            success_message="通過",
            failure_message=f"{checkpoint} 未通過，請依本次輸入計算，並保留邊界與錯誤處理。",
            atol=1e-6, rtol=1e-6,
        ))
    return pybryt.ReferenceImplementation(topic_id, annotations)
