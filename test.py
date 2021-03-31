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


def inverse(l):
    ret = LinkedList()
    n = 10
    p = l.head
    i = 0
    while p and i <= n:
        if i < p.data:
            ret.append(i)
        else:
            p = p.next
        i += 1
    while i <= n:
        ret.append(i)
        i += 1

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
print(l1)
print(l2)
print(inverse(l1))
print(inverse(l2))
