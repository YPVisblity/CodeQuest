# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('bonus-data-structures-12', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

names = {x:f'{x}_{user_id}' for x in 'ABCDE'}
base_graph = {'A':['B','C'],'B':['A','D'],'C':['A','D'],'D':['B','C','E'],'E':['D']}
graph = {names[k]:[names[x] for x in vs] for k,vs in base_graph.items()}

path = shortest_path(graph,names['A'],names['E'])
valid_paths = [[names[x] for x in 'ABDE'],[names[x] for x in 'ACDE']]
observe('shortest_path_valid',path in valid_paths)
observe('same_node',shortest_path(graph,names['A'],names['A']))
isolated = dict(graph)
isolated[names['E']] = []
observe('unreachable',shortest_path(isolated,names['E'],names['A']))
