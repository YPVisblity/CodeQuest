from collections import deque

def bfs(graph, start):
    """廣度優先搜尋，回傳依拜訪順序排列的節點 list"""
    visited = {start}
    result = []
    queue = deque([start])
    # TODO: 請完成這個函式
    return result

#自我檢測
assert bfs(graph, "A") == ["A", "B", "C", "D", "E"]

print("恭喜！基礎任務全部通過，可以繼續挑戰進階任務。")