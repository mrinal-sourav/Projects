import re 
from sys import argv, getsizeof
import os 

#initializing arguments and constants
script_name, FolderName, NumFilesToProcess = argv 

documented_tokens = [] #will contain the set of "terms", "tokens", "words" along with filenumber and 
                        #the frequency of occurence of the term in each file. 

#convert input string to int
NumFiles = int(NumFilesToProcess) 

#get to the directory with the files
mydir = os.path.join(os.getcwd(), FolderName)


#helper function to extract header and parahraph texts from the site 
#inputs - the html text of the sites in "crawled_pages" folder 
#outputs - the header and paragraph text of the page being crawled
def get_header_para(theSite): 
    #Some initial regex to filter out jsut the headers and paras from the HTML site documemt
    headers = re.findall('''<h[1-3]>(.+?)<\/h[1-3]>''', theSite, re.DOTALL)
    #regex starts with '<h' could be followed by 1,2, or 3 which is followed by>
    #give me anything in between
    #regex ends with < followed by / (which requires escape sequence \ before it) followed by 
    #rest of the header
    paragraphs = re.findall('''<p(.+?)\/p>''', theSite, re.DOTALL)  
    #similar for paragraphs, only difference is to not check for > and < 
    #this would help in the second stage of filtering text
    header_texts = []
    para_texts = []
    #further filteration of headers and paragraphs
    for header in headers:
        #second stage filtering
        #give me only what starts at > 
        #look ahead for anything like < (which would start some anchor text we dont need)
        #  using ? and escape it with !
        # now give me anything that ends with < 
        header_text = re.findall('''>(?!<)(.+?)<''', header, re.DOTALL)
        header_texts+= header_text
    for para in paragraphs:
        #similar as above. 
        para_text = re.findall('''>(?!<)(.+?)<''', para, re.DOTALL)
        para_texts+= para_text
    return (header_texts, para_texts) 


#helper function to extract token list from paragraphs
#inputs - header and paragraph lists from get_header_para function
#outputs - a list of tokens (header is appended to the tokens from the paragraph)
def extract_tokens(header_texts, para_texts):
    token_list = []
    for phrase in para_texts: 
        #to exclude those words with apostrophes but include normal words
        words = re.findall('''(?!\w+\\\\'\w)\w+''', phrase, re.DOTALL)
        #get numbers
        numbers = re.findall('''[0-9]+''', phrase, re.DOTALL)
        #get special words like apostrophes and accronyms
        special_words = re.findall('''(\w+\\\\'[ st])|(?:[A-Z]\.){2,}''', phrase, re.DOTALL)
        token_list+= words
        token_list+= numbers
        token_list+= special_words
    token_list+= header_texts
    return (token_list)

#helper function to capture details like filename and frequency for each token 
#inputs - the list of tokens generated by extract_tokens function and the file number
#outputs - a list of documented tokens like ('Harvard', 1, 134)
#          here 'Hravard' is the token, '1' is the document number and '134' is the frequecy
#          of the token in this particular document. 
def generate_details(list_of_tokens, file_num):
    set_of_tokens = set(list_of_tokens)
    documented_tokens = []
    #get the token frequency
    for token in set_of_tokens:
        count=0
        for word in list_of_tokens:
            if word == token:
                count+=1
        details = (token, file_num, count)
        documented_tokens.append(details)      
    return documented_tokens

#the files are named as "file_1.txt", "file_2.txt" etc. starting from 1 
#RunCrawler.py should provide those files in "crawled_pages"" folder
documented_tokens = [] #will contain the set of "terms", "tokens", "words" along with filenumber and 
                        #the frequency of occurence of the term in each file. 
#the files are named as "file1.txt", "file2.txt" etc. starting from 1 

total_size_of_docs = 0
total_number_of_tokens = 0 
all_tokens = []
for file_num in range(1,NumFiles+1):
    with open(os.path.join(mydir, "file_" + str(file_num) + ".txt"), mode='rt', encoding='utf-8') as d:
        theSite = d.read()
        total_size_of_docs+= getsizeof(theSite)
        header, para = get_header_para(theSite)
        token_list = extract_tokens(header, para) 
        all_tokens+= token_list
        total_number_of_tokens+= len(token_list)
        documented_tokens+= generate_details(token_list, file_num)
all_unique_tokens = set(all_tokens)

#writing results onto a file 
with open('tokenizer_results.txt', 'wt', encoding='utf-8') as d: 
    for item in documented_tokens:
        d.write("{}\n".format(item))

# write results to stats file 
with open('stats.txt', 'wt', encoding='utf-8') as d: 
    d.write("\n\t Total size of all the input files (in bytes): {} \n".format(total_size_of_docs))
    d.write("\n\t Total number of tokens: {} \n".format(total_number_of_tokens))
    d.write("\n\t Total number of unique tokens: {} \n".format(len(all_unique_tokens)))