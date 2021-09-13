import os
import re
import json
import nltk
import lxml
from nltk.stem.snowball import EnglishStemmer
nltk.download('stopwords')
from nltk.corpus import stopwords
import time
from collections import defaultdict
from math import log, sqrt



class IndexSearch:
    def __init__(self):
        self.tokenizer = nltk.word_tokenize
        self.stemmer = EnglishStemmer()
        self.stopwords = set(stopwords.words('english')) 
        # we cannot store the full thing in memory but for now just testing
        self.invertedIndex = {} #json.load(open('Final_Total_Index.json', 'r'))
        # get line # corresponding to each term
        self.term_positions = json.load(open('finalPosM4.json', 'r'))
        self.docid_to_url = json.load(open('docIDM4.json', 'r'))
        
        # open index file
        self.file = open('finalTermIndexM4.txt', 'r', encoding='utf-8')
        # Stores query term : score 
        self.queryScore = defaultdict(int) 
        self.queryLength = 0
        self.queryTermDict = {}

    def getDocIDs(self, term: str, listType : str) -> set:
        # find if this term is one we have a position for
        if term[0] not in self.term_positions:
            return set()
        
        ''' Sort terms by docFreq then find intersection of docID in that order & return.. later sort docID by cosine scores '''
        result = set()
        
        # add all docid to a set
        for document in self.queryTermDict[term]['posting'][listType]:
            # get document ID
            docID = document['docID']
            result.add(docID)
        ''' 
        Possibly add in parameters whether to choose champList or lowList --> if so need to figure out how to 
        calc queryScore once or when we retreive champList
        '''
        
        # Finish calculating normalized tf-idf query score
        if listType == 'champList':
            self.queryScore[term] = self.queryScore[term]/self.queryLength

        return result
    
    def getUrls(self, docList : list) -> set:
        results = set()
        
        with open('docIDM4.json', 'r') as f:
            data = json.load(f)
        
        if len(docList) < 10:
            for docID in docList:
                results.add(data[str(docID[0])])
        else:
            for docID in range(10):
                # docList = [(id, score), (id, score)]
                #docList[docID][0]
                results.add(data[str(docList[docID][0])])
            #print(data[docID])
        
        
        #print(results)
        return results
    
    

    def searchIndex(self, query) -> set:
        #query = input("Search: ")
        start = time.time()
        # remove alphanumeric characters
        cleaned_txt = re.sub('[^A-Za-z0-9]+', ' ', query.lower())
        
        unstopped = []
        stopped = []

        for word in cleaned_txt.split():
            # Stem the tokens
            stemmed_word = self.stemmer.stem(word)
            
            # Fill in unstopped and stopped list
            unstopped.append(stemmed_word)
            if stemmed_word not in self.stopwords:
                stopped.append(stemmed_word)
               
        # If query was reduced to 75% of its original size after stopping, keep the unstemmed query
        if (len(stopped)/len(unstopped) < 0.75 or len(stopped) == 0):
            query = unstopped
        else:
            query = stopped
            
        ''' need to return docID's that we want to retrieve urls from and print --> fix getDocIDs()'''
        # Calculate tf for query score 
        for term in query:
            self.queryScore[term] += 1
       
        sortedQuery = self.sortQuery(query)
        # Finish calculating queryLength
        self.queryLength = sqrt(self.queryLength)
        
        
        
        # Find intersection of docID in order of increasing docFreq
        docID = set()
        firstLoop = True
        ''' Need to check if len(docID), if < 10 --> use lowList '''
        
        for term in sortedQuery:
            if firstLoop:
                docID = self.getDocIDs(term[0], 'champList')
            else:
                docID = docID.intersection(self.getDocIDs(term[0], 'champList'))
                if len(docID) == 0:
                    break
            firstLoop = False
        
        docIDLow = set()
        # If champList does not return more than 10 docID, check in lowList
        if len(docID) < 10:
            firstLoop = True
            for term in sortedQuery:
                if firstLoop:
                    docIDLow = self.getDocIDs(term[0], 'lowList')
                else:
                    docIDLow = docIDLow.intersection(self.getDocIDs(term[0], 'lowList'))
                    if len(docIDLow) == 0:
                        break
                firstLoop = False
            
        
        
        docList = self.getScore(docID, sortedQuery, 'champList')
        docList += self.getScore(docIDLow, sortedQuery, 'lowList')
        docList.sort(key = lambda x : -x[1]) # Sort by descending order of score
        ''' May in self.getUrls we can do in range(10) instead of slicing but need to account for if out of range '''
   
     
        urls = self.getUrls(docList)
        for i in urls:
            print(i)
        
        end = time.time()
        print(f'Execution time: {(end-start)*1000} ms')
        return urls
        
    def sortQuery(self, query):
        sortedQuery = []
        for term in set(query):
            if term in self.term_positions:
                line_pos = self.term_positions[term]
                self.file.seek(line_pos)
                termDict = eval(self.file.readline())
                
                # Store term & posting in queryTermDict
                self.queryTermDict[term] = termDict[term]
                # Append (term, docFreq) to sort
                sortedQuery.append((term, termDict[term]['docFreq']))
                
                # Calculate weighted tf-idf query score and queryLength
                self.queryScore[term] = 1 + log(self.queryScore[term]) * self.queryTermDict[term]['idf']
                self.queryLength += (self.queryScore[term])**2
                
        # Sort sortedQuery list in ascending order of docFreq 
        sortedQuery.sort(key = lambda x : x[1])
        return sortedQuery
            
        
        ''' 
        Sort the query terms in this list 
        Append the terms in self.queryDict --> easy access it out 
        
        '''
        
            
        
        
    def getScore(self, docIDSet : set, sortedQuery : list, listType : str):
        docList = []
        tf_score = {} # stores {term: {docID : doc_tf, docID : doc_tf...}}
        for term in sortedQuery: # For each term, store all the needed docID & doc_tf 
            tf_score[term[0]] = {}
            for docInfo in self.queryTermDict[term[0]]['posting'][listType]:
                if docInfo['docID'] in docIDSet:
                    tf_score[term[0]][docInfo['docID']] = docInfo['doc_tf']
        
        for id in docIDSet:
            score = 0
            for term, tf_dict in tf_score.items():
                score += self.queryScore[term] * tf_dict[id]
            docList.append((id, score))
        
        
        return docList
                    
                
            
        
    
    
if __name__ == '__main__':
    obj = IndexSearch()
    
    query = input("Search: ")
    obj.searchIndex(query)
