import pickle

from LinkedList import LinkedList


def load_data():
    with open('saved_dictionary.pkl', 'rb') as f:
        dictionary, docId_to_doc, doc_to_docId = pickle.load(f)
        for i in range(len(dictionary)):
            dictionary[i][1] = LinkedList.from_list(dictionary[i][1])
        print()


load_data()
