import csv 
import re
import urllib.request 
import time 
import re 
import numpy as np 
import pandas as pd
from collections import deque
from sys import argv 

#initializing arguments and constants
script_name, SeedUrl, numpages = argv 

list_of_site_size =[]
num_pages = 0
max_pages = int(numpages)
prepend = "https://www.youtube.com/watch?v="
urllist = []  
scored_list = []

#frontier is defined as a queue and the seed url is added to it
frontier = deque() 
frontier.append(SeedUrl) 
#the depth queue keeps track of the depth
depth_queue = deque()
depth_queue.append(1) 

#get SeedUrl title 

with urllib.request.urlopen(SeedUrl) as url:
    theSite=str(url.read()) #theSite contains all the text read from current_url 
    seed_title = re.findall('''<title>(.+?)</title>''',theSite,re.DOTALL)[0]
    
seed_title = re.sub(r'\W+',' ', seed_title)
#iteration starts with atleast one element in frontier 
#iteration continues till num_pages reaches the max_pages (defined earlier) 
#the loop is structured like bfs using a queue starting from the seed url. 
while frontier and num_pages < max_pages:
    links = [] 
    current_url = frontier.popleft() #current_url is populated starting with the seed url
    depth = depth_queue.popleft()
    time.sleep(2) #wait time is added for politeness policy while crawling
    with urllib.request.urlopen(current_url) as url:
        theSite=str(url.read()) #theSite contains all the text read from current_url 
        links = re.findall('''<a href="/watch\?v=(.[^;]+?)"''',theSite,re.DOTALL)
        links = list(set(links))
    for link in links:
        complete_link = prepend + link #as urls are relative, the domain is prepended to make them absolute. 
        if complete_link not in urllist: #checks for only unique urls
            frontier.append(complete_link)
            depth_queue.append(depth+1)
            urllist.append(complete_link) #keeps a permanent list of unique urls
            num_pages+=1 
            if num_pages >= max_pages: #break when max_pages are reached. 
                break 
            
for link in urllist:
    time.sleep(2)
    with urllib.request.urlopen(link) as url:
        theSite=str(url.read()) 
        
        title = re.findall('''<title>(.+?)</title>''',theSite,re.DOTALL)[0] 
        title = re.sub(r'\W+', ' ', title)
        
        if re.findall('''<div class="watch-view-count">(.+?) views</div>''',theSite,re.DOTALL):
            views = re.findall('''<div class="watch-view-count">(.+?) views</div>''',theSite,re.DOTALL)[0]
        else:
            views = '1'
        
        if re.findall('''"like this video along with (.+?) other people"''',theSite,re.DOTALL):
            likes= re.findall('''"like this video along with (.+?) other people"''',theSite,re.DOTALL)[0]
        else:
            likes = '1'
            
        if re.findall('''"dislike this video along with (.[^person]+?) other people"''',theSite,re.DOTALL):
            dislikes = re.findall('''"dislike this video along with (.+?) other people"''',theSite,re.DOTALL)[0]
        else:
            dislikes = '0' 
        
        title = title[:100]
        views=int(views.replace(',', ''))
        try:
            likes=int(likes.replace(',', ''))
            dislikes=int(dislikes.replace(',', ''))
        except: 
            likes = 1 
            dislikes = 0 
        
        if likes == dislikes or likes == 0:
            likes+=1
        score = views/(likes-dislikes)
        row = [title, link, views, likes, dislikes, score]
        scored_list.append(row) 
        
df = pd.DataFrame(scored_list, columns=['Title', 'URL', 'Views', 'Likes', 'Dislikes', 'Score']) 
df = df.sort_values('Score')
df = df.reset_index(drop=True)  

df.to_csv('%s.csv' %seed_title[:50])