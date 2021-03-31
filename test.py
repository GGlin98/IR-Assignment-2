import pickle

from LinkedList import LinkedList


# x = 214577
# vb = int_to_vb(x)
# print(vb)
# print(bytes_to_bitstring(vb))
#
# x = vb_to_int(vb)
# print(x)

# for i in range(10000):
#     vb = int_to_vb(i)
#     x = vb_to_int(vb)
#     print(x)


def intersect(l1, l2):
    p1 = l1.head
    p2 = l2.head
    ret = LinkedList()
    while p1 and p2:
        if p1.data == p2.data:
            ret.append(p1.data)
            p1 = p1.next
            p2 = p2.next
        elif p1.data < p2.data:
            p1 = p1.next
        else:
            p2 = p2.next
    return ret


l1 = LinkedList()
l2 = LinkedList()
l1.append(1)
l1.append(3)
l1.append(5)
l1.append(7)
l2.append(1)
l2.append(2)
l2.append(3)
l2.append(4)
l2.append(6)
l2.append(7)
l3 = intersect(l1, l2)
print(l3)
