path_result = shortest_path(graph, "A", "E")
path_is_valid = path_result in (["A", "B", "D", "E"], ["A", "C", "D", "E"])

same_node_result = shortest_path(graph, "A", "A")
same_node_is_valid = (same_node_result == ["A"])

# 也可以順便驗證長度而非精確路徑，對未來換圖也比較穩健
path_length_valid = path_result is not None and len(path_result) == 4