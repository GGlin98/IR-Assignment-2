import os
import pickle
from string import punctuation

from nltk import word_tokenize, PorterStemmer

from LinkedList import LinkedList

PUNCTUATION = punctuation + '-—'
PORTER = PorterStemmer()
BLOCKING_K = 4
INPUT_DIR = 'HillaryEmails'
FILE_TERM_DOC_PAIRS = 'output.txt'
SAVE = False  # Save inverted_index else load


def output(ll):
    if ll is None or len(ll) == 0:
        print('No matched document was found')
        return

    p = ll.head
    print('Found {} documents:'.format(len(ll)))
    while p:
        print(docId_to_doc[vb_to_int(p.data)])
        p = p.next


def calc_size():
    ct = 0
    sz = len(dict_string)
    for x in inverted_index:
        # Frequency in 2 bytes
        sz += 2

        # 2 pointers (head & tail)
        sz += 6
        ll = x[1]

        # Next pointer for each element
        sz += len(ll) * 3

        p = ll.head
        while p:
            # VB code for each element
            sz += len(p.data)
            p = p.next

        if ct == 0:
            # pointer to dict_string
            sz += 3
        ct += 1
        if ct == BLOCKING_K:
            ct = 0
    return sz


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
    with open('saved_data_compressed.pkl', 'wb') as f:
        dict_cp = []
        ct = 0
        for i in range(len(inverted_index)):
            if ct == 0:
                dict_cp.append([inverted_index[i][0], inverted_index[i][1].to_list(), inverted_index[i][2]])
            else:
                dict_cp.append([inverted_index[i][0], inverted_index[i][1].to_list()])
            ct += 1
            if ct == BLOCKING_K:
                ct = 0
        pickle.dump((dict_cp, docId_to_doc, doc_to_docId, dict_string), f)


def load_data():
    with open('saved_data_compressed.pkl', 'rb') as f:
        inverted_index, docId_to_doc, doc_to_docId, dict_string = pickle.load(f)
        for i in range(len(inverted_index)):
            inverted_index[i][1] = LinkedList.from_list(inverted_index[i][1])
    return inverted_index, docId_to_doc, doc_to_docId, dict_string


def preprocess(terms):
    terms = word_tokenize(terms)
    sz = len(terms)
    i = 0
    while i < sz:
        j = 0
        # Remove the terms that consist only punctuations
        for x in terms[i]:
            if x not in PUNCTUATION:
                break
            else:
                j += 1
        else:
            # All characters are punctuations, remove the term
            del terms[i]
            sz -= 1
            continue

        if j != 0:
            # Remove prefix punctuations
            terms[i] = terms[i][j:]

        terms[i] = terms[i].lower()
        terms[i] = PORTER.stem(terms[i])

        i += 1
    return terms


def search(term):
    a = 0
    b = len(inverted_index)
    i = int((a + b) / 2)
    while True:
        j = i
        ct = 0
        while len(inverted_index[j]) == 2:
            j -= 1
            ct += 1
        pos = inverted_index[j][2]
        sz = dict_string[pos]
        while ct != 0:
            pos += (sz + 1)
            sz = dict_string[pos]
            ct -= 1
        ptr = dict_string[pos + 1:pos + 1 + sz].decode('utf-8')

        if ptr == term:
            return i
        elif ptr < term:
            a = i + 1
        else:
            b = i - 1
        if a == b:
            i = a
            continue
        elif a > b:
            return None
        i = int((a + b) / 2)


def intersect(l1, l2):
    p1 = l1.head
    p2 = l2.head
    ret = LinkedList()
    while p1 and p2:
        if vb_to_int(p1.data) == vb_to_int(p2.data):
            ret.append(p1.data)
            p1 = p1.next
            p2 = p2.next
        elif vb_to_int(p1.data) < vb_to_int(p2.data):
            p1 = p1.next
        else:
            p2 = p2.next
    return ret


def merge(l1, l2):
    p1 = l1.head
    p2 = l2.head
    ret = LinkedList()
    while p1 and p2:
        if vb_to_int(p1.data) == vb_to_int(p2.data):
            ret.append(p1.data)
            p1 = p1.next
            p2 = p2.next
        elif vb_to_int(p1.data) < vb_to_int(p2.data):
            ret.append(p1.data)
            p1 = p1.next
        else:
            ret.append(p2.data)
            p2 = p2.next
    while p1:
        ret.append(p1.data)
        p1 = p1.next
    while p2:
        ret.append(p2.data)
        p2 = p2.next
    return ret


def inverse(l):
    ret = LinkedList()
    n = len(docId_to_doc) - 1
    p = l.head
    i = 0
    while p and i <= n:
        if i < vb_to_int(p.data):
            ret.append(int_to_vb(i))
        else:
            p = p.next
        i += 1
    while i <= n:
        ret.append(int_to_vb(i))
        i += 1

    return ret


def query(option, terms):
    answer = None
    terms = set(preprocess(terms))
    indexes = []
    for term in terms:
        result = search(term)
        if result is not None:
            indexes.append(result)
    indexes.sort(key=lambda i: inverted_index[i][0])
    if option == 'and':
        if len(indexes) < 2 or len(indexes) < len(terms):
            # Only one matched or some terms not found
            return None
        l1 = inverted_index[indexes.pop(0)][1]
        l2 = inverted_index[indexes.pop(0)][1]
        answer = intersect(l1, l2)
        while indexes:
            answer = intersect(answer, inverted_index[indexes.pop(0)][1])
    elif option == 'or':
        if len(indexes) < 1:
            # No matched
            return None
        elif len(indexes) == 1:
            # Skip merging
            return inverted_index[indexes.pop(0)][1]
        l1 = inverted_index[indexes.pop(0)][1]
        l2 = inverted_index[indexes.pop(0)][1]
        answer = merge(l1, l2)
        while indexes:
            answer = merge(answer, inverted_index[indexes.pop(0)][1])
    elif option == 'not':
        if len(terms) != 1:
            return None
        answer = inverse(inverted_index[indexes.pop(0)][1])

    return answer


if SAVE:
    inverted_index = []
    dict_string = bytes(''.encode('utf-8'))
    ct = 0
    ptr = 0
    docId_to_doc = {}
    doc_to_docId = {}
    doc_index = 0
    cur_term = ''
    cur_termId = -1
    prev_doc = ''

    for dirpath, dirnames, filenames in os.walk(INPUT_DIR):
        filenames.sort()
        for f in filenames:
            docId_to_doc[doc_index] = f
            doc_to_docId[f] = doc_index
            doc_index += 1

    with open(FILE_TERM_DOC_PAIRS, 'rt', encoding='utf-8') as f:
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
                term_encoded = term.encode('utf-8')
                sub_string = bytes([len(term_encoded)]) + term_encoded
                dict_string += sub_string
                if ct == 0:
                    inverted_index.append([0, LinkedList(), ptr])
                else:
                    inverted_index.append([0, LinkedList()])
                ct += 1
                if ct == BLOCKING_K:
                    ct = 0
                ptr += len(sub_string)
                cur_term = term
                cur_termId += 1
                prev_doc = ''

            if doc != prev_doc:
                # Update inverted index, make sure no repeated doc
                inverted_index[cur_termId][0] += 1
                inverted_index[cur_termId][1].append(int_to_vb(doc_to_docId[doc]))
            prev_doc = doc
    save_data()
else:
    inverted_index, docId_to_doc, doc_to_docId, dict_string = load_data()

# print(calc_size())

### Sample queries ###
# answer = query('and', 'cat dog')
answer = query('and', 'libya missile Gaddafi')
# answer = query('or', 'cat dog')
# answer = query('not', 'the')

output(answer)
