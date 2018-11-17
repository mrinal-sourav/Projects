 
 - Code requires the following imports:

	import csv 
	import re
	import urllib.request 
	import time 
	import re 
	import numpy as np 
	import pandas as pd
	from collections import deque
 
 - Inputs: 
	A Seed URL from youtube 
	Number of links/videos to crawl

 - Outputs: 
	A sorted csv file with video data in the following format:
		Video Title, Video link, Score, Author, Views, Likes, Dislikes 

	
	Score is calculated by the ratio of:

		No. of Views / (Likes - Dislikes)

	The smaller this number, the "better" the video. 
	If EVERY person who views a video also hits "like", this score will be 1. 
	Justin Bieber may come up in negative (and on the top) as he has more dislikes than likes for 
	some of his videos! Ignore negatives and single digit or wierd looking integers for views/score. 

 - Sample command (Updated 20th March 2018): 

	Open command prompt or terminal and "cd" into the directory with the code, then type and enter:
	
	python you_tube_crawler.py 

        Please enter the seed url for the crawl: https://www.youtube.com/user/TEDtalksDirector/videos?flow=grid&view=0&sort=p

        Enter the number of videos to crawl: 100

                Urls remaining: 80

                Urls remaining: 60

                Urls remaining: 40

                Urls remaining: 20

                Urls remaining: 0

        Crawling complete: CSV file named  TED n YouTube created

 - IMPORTANT NOTES: 

	WAIT TIME IS ADDED FOR "POLITENESS POLICY" WHILE CRAWLING. (updated from 2 seconds to 1.5 seconds) 
	PLEASE DO NOT REDUCE IT LEST YOUTUBE THINKS YOU ARE A BOT. 

	Along with individual videos, code now also works with playlists and sorted channel videos; 
	updated 20th March 2018 - Input method changed

	Doesn't work with live videos. (It will crawl but the numbers wouldn't make sense)

 - TIP: 
	Once you have the csv file from a crawl, look for videos with moderately big numbers
	that appear towards the top. 


