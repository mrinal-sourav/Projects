
from sys import argv
import numpy as np
import math 
import re

#initializing arguments and constants
script_name, IndexFolderName, CrawledPagesFolder, Max_Results = argv 

K = int(Max_Results)

#bring data to ram

#read the queries
list_of_queries = []
with open('Query.txt', 'rt', encoding='utf-8') as file:
    for line in file.readlines():
        line = line.strip('\n')
        list_of_queries.append(eval(line))

#read document details
doc_mapping=[] 
with open(IndexFolderName + '/' + 'DocumentIDFile.txt', 'rt', encoding='utf-8') as file:
    for line in file.readlines():
        line = line.strip('\n')
        doc_mapping.append(eval(line))
        
#read term details
index_mapping=[] 
with open(IndexFolderName + '/' + 'TermIDFile.txt', 'rt', encoding='utf-8') as file:
    for line in file.readlines():
        line = line.strip('\n')
        index_mapping.append(eval(line))
        
#read the inverted index file: 
with open(IndexFolderName + '/' + 'InvertedIndex.txt', 'rt', encoding='utf-8') as file:
    inverted_index = eval(file.read())

######################################################################### helper functions ############################################

#given a term, returns the index of the term
def get_term_index(term):
    for term_map in index_mapping:
        if term_map[1] == term:
            return term_map[0] 
        
#given a document Id, returns the word count of the document   
def get_doc_wordcount(docId):
    for doc_map in doc_mapping:
        if doc_map[0] == docId:
            return doc_map[2]   

#given a document Id, returns the name of the document 
def get_doc_name(docId):
    for doc_map in doc_mapping:
        if doc_map[0] == docId:
            return doc_map[1] 

#helper function for normalization
def normalize_vector(array):
    y = [a**2 for a in array]
    z = sum(y)
    l2 = z**0.5
    res = array / l2
    return res 

#helper function to calculate score
def calculate_score(query, doc):
    score = 0
    for i in range(len(query)):
        score+= query[i] * doc[i]
    return score

#helper function to retrieve results
def retrieve(normalized_query, tf_idf_matrix, documents):
    Score_list = {}
    for i in range(len(documents)):
        Score_list[documents[i]] = calculate_score(normalized_query, tf_idf_matrix[:,i])
    res = sorted(Score_list.items(), key=lambda x: x[1], reverse = True)
    return res

#helper function to extract paragraph texts from the site 
#inputs - the html text of the sites in "crawled_pages" folder 
#outputs - the title and the first 2 paragraph text of the page being crawled
def get_para(theSite): 
    #get the title
    title = re.findall('''<title>(.+?)</title>''',theSite,re.DOTALL)[0]
    paragraphs = re.findall('''<p(.+?)\/p>''', theSite, re.DOTALL)  
    para_texts = []
    paragraph = []
    #further filteration of paragraphs
    for para in paragraphs[:1]: 
        para_text = re.findall('''>(?!<)(.+?)<''', para, re.DOTALL)
        for phrase in para_text:
            words = re.findall('''(?!\w+\\\\'\w)\w+''', phrase, re.DOTALL)
            para_texts.append(' '.join(words))
        paragraph.append(' '.join(para_texts))
    return (title, paragraph) 

########################################################################### main code ###################################################

#the major part of the code still written as one large helper function
#inputs  - a query and the top k limit on search
#outputs - the result of the search in the form of a list of tuple
def process_query(query, k):
    query_set = set(query) #does away with duplicates
    query_index = {} #holds the inverted index data but for only the query terms
    for term in query_set:
        index = str(get_term_index(term))
        query_index[term] = inverted_index[index]
    
    doc_ids = [] #holds the doc id information
    doc_term_freq = {} #holds the term frequence for each term in the query
    for term in query_index:
        for item in query_index[term]:
            doc_ids.append(item[0])
        doc_term_freq[term] = len(query_index[term])
    
    documents = list(set(doc_ids)) 
    doc_word_count = {} #to calculate the term frequency we need the total words in the document
    for doc_id in documents:
        doc_word_count[doc_id] = get_doc_wordcount(doc_id) 
        
    #initialize the tf_idf matrix
    tf_idf_matrix = np.zeros((len(query_index), len(documents)), dtype=float)
    i = 0
    N = 200 #total number of documents in the processed collection
    
    #we process the query separately and then continue with the tf_idf for each document
    query_vector = np.zeros(len(query_index), dtype=float)
    for term in query_index:
        query_tf = 1 / len(query_index)
        query_weighted_tf = math.log10(1 + query_tf)
        df = doc_term_freq[term]
        idf = math.log10(N / df)
        query_vector[i] = query_weighted_tf * idf
        for item in query_index[term]:
            if item[0] in documents: 
                tf = item[1] / doc_word_count[item[0]]
                tf_weighted = math.log10(1 + tf)
                tf_idf_matrix[i][documents.index(item[0])] = tf_weighted * idf
        i+=1 
        
    #normalize the query using helper function
    normalized_query = normalize_vector(query_vector) 
    #normalize the rest of the tf_idf matrix
    for i in range(len(documents)):
        tf_idf_matrix[:,i] = normalize_vector(tf_idf_matrix[:,i])

    #retieve results for the query
    Score_list = retrieve(normalized_query, tf_idf_matrix, documents)
    final_res = Score_list[:k] #select top k
    
    return (final_res, normalized_query) 

############################################################# putting it all together######################################################

with open('output.txt','wt') as d:
    for query in list_of_queries: 
        query_result, query_contrib = process_query(query, K)
        d.write("\n\n{}\n\n".format(query))

        for doc_id, cos_score in query_result:
            doc_name = get_doc_name(doc_id)
            with open(CrawledPagesFolder + '/' + doc_name + '.txt', 'rt', encoding='utf-8') as file:
                theSite = file.read()
                (title, para) = get_para(theSite)
            d.write("\t{}\n".format(doc_id))
            d.write("\t{}\n".format(title))
            d.write("\t{}\n".format(cos_score))
            for string in para:
                d.write("\t{:^10}\n".format(string))

        contribution_dict = {}
        for i in range(len(set(query))):
            contribution_dict[query[i]] = query_contrib[i]
        #prints the contribution of each term in the query for the result    
        d.write("\n\n{}\n\n".format(contribution_dict))