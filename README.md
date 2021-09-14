# Search-Engine-Project
### Description
Search engine is built for users to search for webpages in the ICS domain (http://www.ics.uci.edu). Each webpage is tokenized and placed in an inverted index. 

### How to Run Search Engine
* Run indexer.py to create inverted index for corpus (DEV directory) stored as files in the file system
* Run searcher.py to use search engine in console
* Run search_ui.py and copy and paste link in console to run web interface 

### How Does the Indexer Works?
The DEV directory is a large collection of ICS web pages organized by web domain as folders and pages within the domain as json files that consist of the page url and page content. The indexer begins by going through each json file, creates a dictionary mapping doc ID to page url, and use BeautifulSoup to tokenize the html content into two lists: important tokens and normal tokens. 

Next, the two lists of important and normal tokens are stemmed using the English Snowball Stemmer from nltk before being inserted into the index. 6
