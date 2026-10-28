sll = SinglyLinkedList()

sll.append(10)
sll.append(20)
sll.append(30)
print(sll.to_list())

sll.insert_at(1, 15)
print(sll.to_list())

sll.delete_by_value(15)
print(sll.to_list())