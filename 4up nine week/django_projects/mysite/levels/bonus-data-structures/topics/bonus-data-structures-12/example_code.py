graph = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A", "D"],
    "D": ["B", "C", "E"],
    "E": ["D"],
}

# 範例：DFS（遞迴實作，已完成，供參考）
def dfs(graph, start, visited=None, result=None):
    if visited is None:
        visited = set()
        result = []
    visited.add(start)
    result.append(start)
    for neighbor in graph[start]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited, result)
    return result

print(dfs(graph, "A"))   # 可能輸出：['A', 'B', 'D', 'C', 'E']（依鄰接順序而定）
