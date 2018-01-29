
I have indexed 200 pages and have attached it along with this assignment. 

1. The most difficult part of this assignment was to manage the document number and filenames between documents. 
   The easiest part of the assignment was the regular expressions as they were already done from previous assignments. 

3. Running the script. 
	Use the command like: 
	
	python RunRankedRetrieval.py IndexFiles crawled_pages 5 

	The folders are zipped with the assignment. Number of results (top K can be increased) 

	The ouput does not contain a fixed 200 byte snippet. I substituted that with the first 2 paragraphs. 
	For some queries they return too big a para while for some country names only the Lat-Long comes up. 