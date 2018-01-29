What was the most difficult part of this assignment? 

	Figuring out the regular expression. Figuring out how to print files in runtime.  

To run the script, enter the command like so: 

	python RunCrawler.py "https://en.wikipedia.org/wiki/Gerard_Salton" 10 

You should then get the following string when the crawling is complete:
The runtime is about 10-15 minutes for 800 urls.  

	Crawling Complete.
 	You can find the folder in the current directory
 	named with the crawl start time. 

A folder with the timestamp of the start time of the crawling is created (about 150MB for 800 urls). 
Within this folder you should find "URLsCrawled.txt" and "stats.txt" 

You could also find a folder called "crawled_pages" which contains the html string of each
page that was crawled. 

