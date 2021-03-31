import os
import pickle

from nltk import word_tokenize, PorterStemmer

from LinkedList import LinkedList
from string import punctuation

PUNCTUATION = punctuation + '-—'
PORTER = PorterStemmer()


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
    with open('saved_data.pkl', 'wb') as f:
        dict_cp = dictionary.copy()
        for i in range(len(dict_cp)):
            dict_cp[i][1] = dict_cp[i][1].to_list()
        pickle.dump((dict_cp, docId_to_doc, doc_to_docId), f)


def load_data():
    with open('saved_data.pkl', 'rb') as f:
        dictionary, docId_to_doc, doc_to_docId = pickle.load(f)
        for i in range(len(dictionary)):
            dictionary[i][1] = LinkedList.from_list(dictionary[i][1])
    return dictionary, docId_to_doc, doc_to_docId


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
    b = len(dictionary)
    i = int((a + b) / 2)
    while True:
        ptr = dictionary[i][2]
        if ptr == term:
            return i
        elif ptr < term:
            a = i + 1
        else:
            b = i - 1
        if a == b:
            if dictionary[a][2] == term:
                return a
            else:
                return None
        elif a > b:
            # Possible?
            return None
        i = int((a + b) / 2)


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


def merge(l1, l2):
    p1 = l1.head
    p2 = l2.head
    ret = LinkedList()
    while p1 and p2:
        if p1.data == p2.data:
            ret.append(p1.data)
            p1 = p1.next
            p2 = p2.next
        elif p1.data < p2.data:
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
        if i < p.data:
            ret.append(i)
        else:
            p = p.next
        i += 1
    while i <= n:
        ret.append(i)
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
    indexes.sort(key=lambda i: dictionary[i][0])
    if option == 'and':
        if len(indexes) < 2:
            # Only one matched
            return None
        l1 = dictionary[indexes.pop(0)][1]
        l2 = dictionary[indexes.pop(0)][1]
        answer = intersect(l1, l2)
        while indexes:
            answer = intersect(answer, dictionary[indexes.pop(0)][1])
    elif option == 'or':
        if len(indexes) < 1:
            # No matched
            return None
        elif len(indexes) == 1:
            # Skip merging
            return dictionary[indexes.pop(0)][1]
        l1 = dictionary[indexes.pop(0)][1]
        l2 = dictionary[indexes.pop(0)][1]
        answer = merge(l1, l2)
        while indexes:
            answer = merge(answer, dictionary[indexes.pop(0)][1])
    elif option == 'not':
        if len(terms) != 1:
            return None
        answer = inverse(dictionary[indexes.pop(0)][1])

    return answer


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

# answer = query('and', 'Wednesday Thinking you')
# answer = query('not', 'the')
answer = query('or', 'libya fuck')
# answer = query('or', 'fasdjfklasjf;eoef gnerwklgn feio2p fuck')
# answer = query('and', 'fasdjfklasjf;eoef gnerwklgn feio2p fuck')

print()
