# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('bonus-data-structures-7', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

root = TreeNode(f'A_{user_id}')
root.left = TreeNode(f'B_{user_id}')
root.right = TreeNode(f'C_{user_id}')
root.left.left = TreeNode(f'D_{user_id}')
root.left.right = TreeNode(f'E_{user_id}')
observe('inorder',inorder(root))
observe('postorder',postorder(root))
