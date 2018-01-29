#given a term, returns the index of the term
def get_term_index(term):
    index_mapping=[] 
    with open('TermIDFile.txt', 'rt', encoding='utf-8') as file:
        for line in file.readlines():
            line = line.strip('\n')
            index_mapping.append(eval(line))
    for term_map in index_mapping:
        if term_map[1] == term:
            return term_map[0] 
        
#given a document Id, returns the name of the document
def get_doc_name(docId):
    doc_mapping=[] 
    with open('DocumentIDFile.txt', 'rt', encoding='utf-8') as file:
        for line in file.readlines():
            line = line.strip('\n')
            doc_mapping.append(eval(line))
    for doc_map in doc_mapping:
        if doc_map[0] == docId:
            return doc_map[1] 

def get_term_docs(term):
    document_list = []
    index = str(get_term_index(term))
    with open('InvertedIndex.txt', 'rt', encoding='utf-8') as file:
        inv_index = eval(file.read())
    for item in inv_index[index]:
        document_list.append(get_doc_name(item[0]))
    return document_list 