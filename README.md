# Search-Engine-Project
### Description
Search engine is built for users to search for webpages in the ICS domain (http://www.ics.uci.edu). Each webpage is tokenized and placed in an inverted index. 

### How to Run Search Engine
* Unzip DEV folder
* Run "pip install nltk", "pip install bs4", "pip install lxml", "pip install flask"
* Run indexer.py to create inverted index for corpus (DEV directory) stored as files in the file system
* Run searcher.py to use search engine in console
* Run search_ui.py and copy and paste link in console to run web interface 

### How Does the Indexer Work?
The DEV directory is a large collection of ICS web pages organized by web domain as folders and pages within the domain as json files that consist of the page url and page content. The indexer begins by going through each json file, creates a dictionary mapping doc ID to page url.

For each page, the getTokenList function will be called on the json file where the page content will be tokenized by BeautifulSoup into two lists: important tokens and normal tokens. 

Next, the two lists of important and normal tokens are stemmed using the English Snowball Stemmer from nltk before being inserted into the index by the insertTermsIntoIndex function. In addition, this function is used to perform some of tf-idf calculations prior to searching in order to employ heuristics to improve relevancy and efficiency. 

After going through 30 folders, the indexer will off load the inverted index from main memory to a partial index on the disk as a text file. During this off load, a dictionary is created to map the term and position of the posting in the text file for fast retrieval. 

Afterwards, the indexer repeats the steps of tokenizing, stemming, and storing the tokens in the inverted index with the next 30 folders. Once all folders have been accessed, the dictionary holding the terms and position of the terms to merge the partial index text files into one final index text file. During this merging, another dictionary is used to map the terms and position of the postings in the final index text file and will be saved as a json file.

The reason for off loading is to minimize the memory footprint.

### How Does the Searcher Work?
The searcher will require the final index text file, json file that maps the terms and position of the postings in the final index text file, and the json file that maps the doc ID to the page url. All the required files were created by the indexer. 

Once the searcher receives a query, the query will be cleaned and stemmed. The query will also be stopped if stopping does not reduce the query to less than 75% of its original size. The tokens in the query are then sorted by their doc frequency which is retreived by the final index text file and position json file by the sortQuery function. 

Next, the set of doc ID of each token in the query are retreived by the doc ID json file and the intersections of all the tokens using the champion list are stored in a set. If the length of the set is less than 10, the low list is used as well to retreive more doc IDs. 

Lastly, the doc IDs are sorted in descending order by the cosine similary score which was calculated throughout the different functions in the searcher (to reduce the number of for loops needed and opening of files). The getUrls function is called to print the url of corresponding doc ID using the doc ID json file.

### Data Structure Used in Inverted Index
A nested dictionary where each key is a term mapped to a dictionary that holds the document frequency, posting list (another dictionary that maps to a champion list and low list).

{
term1 : {docFreq: 5, 
        posting : {champList: [...], 
                   lowList: [...]}
        }, 
term2: ...
}

### Heuristics Measures
Indexer
* tokens were stemmed
* created an index of the index 
     - outer index mapped term and position of posting and used seek() to retreive postings
     - inner index mapped terms and postings saved as a text file (final index text file)
* precalculated the doc tf & idf (for query) 
* increased doc tf score for tokens considered special tags (headers, bold, italicized, etc.) 
* sorted postings based on doc tf-idf scores
* separated postings into champion list and low list 

Searcher
* terms from query are stemmed prior to looking up in index
* eliminated stop words if the original size of query was not reduced to less than 75%
* Found intersection of doc ID sets of tokens in order of smallest to largest doc frequency
    - AND bitwise operator
* ranked results using cosine similarity
    - calculated parts of score in getScore() and getDocID() to reduce number of for loops used
* only returned top 10 results  
