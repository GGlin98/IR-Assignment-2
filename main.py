import os
import pickle

from LinkedList import LinkedList


def bitstring_to_bytes(s):
    return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder='big')


def bytes_to_bitstring(b):
    return bin(int.from_bytes(b, "big"))


def int_to_vb(x):
    a = []
    bits = bin(x)[2:]
    temp = bits[-7:]
    a.append('1' + temp)
    bits = bits[:-7]
    while bits != '':
        temp = bits[-7:]
        a.append('0' + temp)
        bits = bits[:-7]

    a = [int.from_bytes(bitstring_to_bytes(s), 'big') for s in a]
    vb = bytes(a[::-1])

    return vb


def vb_to_int(vb):
    bits = bytes_to_bitstring(vb)[2:]
    a = ''
    temp = bits[-8:]
    bits = bits[:-8]
    a += temp[1:]
    while bits != '':
        temp = bits[-8:]
        bits = bits[:-8]
        if len(temp) == 8:
            a = temp[1:] + a
        else:
            a = temp + a

    return int.from_bytes(bitstring_to_bytes(a), 'big')


def save_data():
    with open('saved_dictionary.pkl', 'wb') as f:
        dict_cp = dictionary.copy()
        for i in range(len(dict_cp)):
            dict_cp[i][1] = dict_cp[i][1].to_list()
        pickle.dump((dict_cp, docId_to_doc, doc_to_docId), f)


def load_data():
    with open('saved_dictionary.pkl', 'rb') as f:
        dictionary, docId_to_doc, doc_to_docId = pickle.load(f)
        for i in range(len(dictionary)):
            dictionary[i][1] = LinkedList.from_list(dictionary[i][1])
    return dictionary, docId_to_doc, doc_to_docId


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

save = False

if save:
    dictionary = []
    docId_to_doc = {}
    doc_to_docId = {}
    doc_index = 0
    cur_term = ''
    cur_termId = -1
    prev_doc = ''

    for dirpath, dirnames, filenames in os.walk('HillaryEmails'):
        filenames.sort()
        for f in filenames:
            docId_to_doc[doc_index] = f
            doc_to_docId[f] = doc_index
            doc_index += 1

    with open('output.txt', 'rt', encoding='utf-8') as f:
        while True:
            line = f.readline()
            if line == '':
                # EOF
                break

            pair = line.split()
            term = pair[0]
            doc = pair[1]

            if term != cur_term:
                # Frequency & Postings & Term
                dictionary.append([0, LinkedList(), term])
                cur_term = term
                cur_termId += 1
                prev_doc = ''

            if doc != prev_doc:
                # Update dictionary, make sure no repeated doc
                dictionary[cur_termId][0] += 1
                dictionary[cur_termId][1].append(doc_to_docId[doc])
            prev_doc = doc
    save_data()
else:
    dictionary, docId_to_doc, doc_to_docId = load_data()

print()
