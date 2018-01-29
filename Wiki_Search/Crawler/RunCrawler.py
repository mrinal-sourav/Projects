
#Inputs expected by the script: 
#     1. SeedUrl - A url as seed url to start crawling from
#     2. numpages - A positive integer indicating the maximum number of pages to be crawled 

import urllib.request 
import re 
from collections import deque
from sys import argv, getsizeof
import time 
import os, datetime 

#create directory for the crawl with the current timestamp 
mydir = os.path.join(os.getcwd(), datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
os.makedirs(mydir) 

#initializing arguments and constants
script_name, SeedUrl, numpages = argv

list_of_site_size =[]
num_pages = 0
max_pages = int(numpages)
prepend = "https://en.wikipedia.org"
urllist = []  

#frontier is defined as a queue and the seed url is added to it
frontier = deque() 
frontier.append(SeedUrl) 
#the depth queue keeps track of the depth
depth_queue = deque()
depth_queue.append(1)

#iteration starts with atleast one element in frontier 
#iteration continues till num_pages reaches the max_pages (defined earlier) 
#the loop is structured like bfs using a queue starting from the seed url. 
while frontier and num_pages < max_pages:
    links = [] 
    current_url = frontier.popleft() #current_url is populated starting with the seed url
    depth = depth_queue.popleft()
    time.sleep(2) #wait time is added for politeness policy while crawling
    with urllib.request.urlopen(current_url) as url: #urls are opened one at a time here
        theSite=str(url.read()) #theSite contains all the text read from current_url 
        # "re" is used to filter out only urls that are required from theSite
        links=re.findall('''<a href="(/wiki/(?!Main_Page).[^:]+?)"''',theSite,re.DOTALL) 
        #the valid urls are now processed one at a time. 
        for link in links:
            complete_link = prepend + link #as urls are relative, the domain is prepended to make them absolute. 
            if complete_link not in urllist: #checks for only unique urls
                frontier.append(complete_link)
                depth_queue.append(depth+1)
                urllist.append(complete_link) #keeps a permanent list of unique urls
                num_pages+=1 
                if num_pages >= max_pages: #break when max_pages are reached. 
                    break 
                
#to store the files crawled 
crawled_pages_path = os.path.join(mydir, "crawled_pages")
os.makedirs(crawled_pages_path)

count=0
for link in urllist: 
    count+=1
    time.sleep(1)
    with urllib.request.urlopen(link) as url:
        theSite=str(url.read())
        list_of_site_size.append(getsizeof(theSite)) #getsize of pages crawled 
        with open(os.path.join(crawled_pages_path, "file_" + str(count) + ".txt"), mode='wt', encoding='utf-8') as d:
            d.write(theSite)
                          
#preparing URLsCrawled.txt                   
with open(os.path.join(mydir, "URLsCrawled.txt"), mode='wt', encoding='utf-8') as d:
    for link in urllist:
        print (link, file = d)
        
#preparing stats.txt 
max_size = max(list_of_site_size) 
min_size = min(list_of_site_size)
avg_size = sum(list_of_site_size)/len(list_of_site_size)
max_depth = max(depth_queue)

with open(os.path.join(mydir, "stats.txt"), mode='wt', encoding='utf-8') as d:
    print ("Maximum size: ", max_size, " bytes", file = d)
    print ("Minimum size: ", min_size, " bytes", file = d)
    print ("Average size: ", avg_size, " bytes", file = d)
    print ("Maximum depth reached:", max_depth, file = d)  
    
print("Crawling Complete. \n You can find the folder in the current directory \n named with the crawl start time \n")
    