def shortest_path(graph, start, end):
    """利用 BFS 找出 start 到 end 的最短路徑，回傳節點 list；不連通則回傳 None"""
    if start == end:
        return [start]

    visited = {start}
    queue = deque([start])
    predecessor = {start: None}
    # TODO: 請完成這個函式（BFS 過程中記錄 predecessor，找到 end 後回推路徑）
    return None

# ===== 自我檢查 =====
path = shortest_path(graph, "A", "E")
assert path in (["A", "B", "D", "E"], ["A", "C", "D", "E"])
assert shortest_path(graph, "A", "A") == ["A"]

print("恭喜完成所有關卡！你已經取得「迷宮之城探險家」徽章，正式畢業成為資料結構大師！")