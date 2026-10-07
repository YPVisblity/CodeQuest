test_root = None
for value in [8, 3, 10, 1, 6, 14, 4, 7]:
    test_root = insert(test_root, value)

test_root = delete_node(test_root, 3)   # 刪除有兩個子節點的節點
assert inorder_values(test_root) == [1, 4, 6, 7, 8, 10, 14]

test_root = delete_node(test_root, 14)  # 刪除只有一個子節點（或葉節點）的節點
assert inorder_values(test_root) == [1, 4, 6, 7, 8, 10]

print("進階挑戰通過！你已經取得「神殿守護者」進階徽章！")