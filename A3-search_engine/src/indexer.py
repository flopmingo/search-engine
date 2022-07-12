import os
import re
import json
import nltk
nltk.download('punkt')
from bs4 import BeautifulSoup
import lxml
from nltk.stem.snowball import EnglishStemmer
import sys
from math import log, sqrt


class Indexer:
    def __init__(self):
        self.tokenizer = nltk.word_tokenize
        self.stemmer = EnglishStemmer()
        self.important_tags = ['title', 'h1', 'h2', 'h3', 'strong', 'b']
       
        self.partial_Index = dict()
        
        self.folderList = []
        self.dictID = {}
        self.fileCounter = 0
        
        self.dictPos = {}
        
    def getFiles(self, folder_name: str) -> None:
        ''' Navigate the folder to get all the files we need to tokenize+index '''
        
        # current directory
        cdir = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

        # dev folder
        dev_folder = os.path.join(cdir, folder_name)
        
        # sort folder names in DEV 
        self.sortFolderList(dev_folder)

        # Use to check track of how many folders of web pages have been indexed
        folderCounter = 0
        pNum = 0

        # iterate through all folders in the DEV folder
        for folder in self.folderList:
            print(f'Entering folder: ', folder, '\n')
            
            dev_sub = os.path.join(dev_folder, folder)

            # ignore non directory trap
            if '.DS_Store' not in dev_sub:

                # iterate through all files in each folder
                for file in os.listdir(dev_sub):
                    print('\tEntering file: ', file)
                
                    # build full path to the file
                    json_file = os.path.join(dev_sub, file)
                    
                    # open file, load json, close file
                    with open(json_file, 'r') as f:
                        data = json.load(f)


                    # url of this content
                    page_url = data['url']

                    # get a tuple with two lists of tokens
                    page_tokens = self.getTokenList(data)

                    high_value_tokens = page_tokens[0] # title, h1, h2, h3, bold, strong
                    normal_tokens = page_tokens[1]    # everything

                    # Assign docID
                    self.fileCounter += 1
                    self.dictID[self.fileCounter] = page_url

                    # here we would take these tokens and insert them in the correct index file
                    self.insertTermsIntoIndex(high_value_tokens, normal_tokens)
                   
            
            folderCounter += 1
            # After entering 30 folders, will dump data in a new json file 
            if folderCounter > 30:
                pi_folder_path = os.path.join(cdir, 'Partial_IndexM4')
                
                # if Partial_Index folder does not exist, create one 
                if not os.path.isdir(pi_folder_path):
                    os.mkdir(pi_folder_path)

                pNum += 1
                folderCounter = 0
                # Create partial index text and json file
                self.setPartialFile(pi_folder_path, pNum)
        
          
        # At end of for loop, remaining folders that did not pass the folderCounter
        pNum += 1
        self.setPartialFile(pi_folder_path, pNum)
        
        # Create docID.json file to store mappings of docID to url 
        with open('docIDM4.json', 'w') as outFile:
            json.dump(self.dictID, outFile)
    
    
    def sortFolderList(self, dev_folder: str) -> None:       
        ''' Sorts the folders in DEV folder ''' 
        
        for folder in os.listdir(dev_folder):
            # ignore non directory trap
            if folder != '.DS_Store':
                self.folderList.append(folder)
            
        self.folderList.sort()
        
                    
    def getTokenList(self, page_data: dict) -> tuple:
        ''' Tokenize the given html content into two lists (important tags, normal_tags) '''

        # parse HTML content
        soup = BeautifulSoup(page_data['content'],'lxml')

        # Lets parse the higher value terms first
        important_tokens = []

        for tag in self.important_tags:
            current_tag = soup.find(tag)
            if current_tag != None:
                cleaned_tag = re.sub('[^A-Za-z0-9]+', ' ', current_tag.text)
                # tokenize
                tag_tokens = nltk.word_tokenize(cleaned_tag.lower())
                important_tokens+=tag_tokens
                

        # Now we can get all the rest of the terms
        normal_terms = []
        # avoid html tags and syntax 
        raw_text = soup.get_text()
        # strip non-alpanumeric chars
        cleaned_txt = re.sub('[^A-Za-z0-9]+', ' ', raw_text)
        # tokenize into terms
        normal_terms+=(nltk.word_tokenize(cleaned_txt.lower()))

        return (important_tokens, normal_terms)


    def insertTermsIntoIndex(self, special_tokens: list, normal_tokens: list) -> None:
        ''' Stem tokens and insert into the index.
            Also, calculate docFreq and unweighted tf (idf and weighted tf will be calculated in...)
        '''

        # stem special tokens
        special_tokens = { self.stemmer.stem(token) for token in special_tokens }
        
        # During the 1st for loop, add the terms into the partial_index dictionary. Also, doc_tf stores word frequency atm
        for token in normal_tokens:
            token = self.stemmer.stem(token)
            
            ''' {term : {docFreq: 5, posting : {champList: [...], lowList : [...]} }}
                    - champList : [{docID, docNorm, idf}]
                
                for now
                {term : {docFreq: 5, idf: 0, posting : [{docID, doc_tf, tags_contain}]}}
            '''       

            # 1st time adding token 
            if token not in self.partial_Index:
                self.partial_Index[token] = {'docFreq' : 0, 'idf' : 0, 'posting' : []}
                   
            # If list of posting for this token is empty or 1st time incrementing freq for this doc ID 
            if (self.partial_Index[token]['posting'] == []) or (self.partial_Index[token]['posting'][-1]['docID'] != self.fileCounter):
                tokenDict = {'docID' : self.fileCounter, 'doc_tf' : 1, 'tags_contain' : False }
                self.partial_Index[token]['posting'].append(tokenDict)
            # During this function call, the doc ID is the same so... 
            #     If token exists and has recorded in this function call, the current docID's  posting should be the last element of the list of postings
            else:
                self.partial_Index[token]['posting'][-1]['doc_tf'] += 1
                
            # Check if token is important
            if token in special_tokens:
                self.partial_Index[token]['posting'][-1]['tags_contain'] = True
                
        # doc_tf currently stores word freq --> calculate unweighted tf 
        # Also calculate docLength
        docLength = 0
        for token in set(normal_tokens):
            token = self.stemmer.stem(token)
            self.partial_Index[token]['docFreq'] += 1 # increment doc frequency to calculate idf later
            
            docPost = self.partial_Index[token]['posting'][-1] # docPost is current docID's posting
            docPost['doc_tf'] = 1 + log(docPost['doc_tf'])     # Calculate unweighted doc_tf
            docLength += (docPost['doc_tf'])**2                # Calculate docLength    
            
        
        # Calculate weighted doc tf 
        docLength = sqrt(docLength)
        for token in set(normal_tokens):
            token = self.stemmer.stem(token)
            
            docPost = self.partial_Index[token]['posting'][-1]
            docPost['doc_tf'] = docPost['doc_tf']/docLength         # Calculate weighted doc_tf 
            
            # If token was in special tag, increment score
            if docPost['tags_contain'] == True:
                docPost['doc_tf'] += 1
            docPost['tags_contain'] = None
      
            
                
                
    def setPartialFile(self, pi_folder_path : str, pNum : int) -> None:
        ''' Creates partial index text and json files, offloading 3 times '''
        seekNum = 0
        pi_txt_name = os.path.join(pi_folder_path, f'part{pNum}.txt')
        open(pi_txt_name, 'a').close()  # need to create txt file before opening it with 'r+'
        with open(pi_txt_name, 'r+') as ptxt:
            for k, v in self.partial_Index.items():
                # Writing each {token : list of postings} on a new line in the partial text file
                dictStr = '{' + f"'{k}' : {v}" + '}'
                ptxt.write(f'{dictStr}\n')
                
                # Mapping term and position in the text file
                self.dictPos[k] = [seekNum]
                ptxt.seek(seekNum)          # set input stream at seekNum (beginning of a line)
                ptxt.readline()             # readline() to get input stream at the beginning of the next line
                seekNum = ptxt.tell()       # set seekNum to the beginning of the next line 

        # Dumping out the {token : position} in the partial json file
        pi_json_name = os.path.join(pi_folder_path, f'part{pNum}.json')
        with open(pi_json_name, 'w') as pjson:
            json.dump(self.dictPos, pjson)
        
        # Empty out dictionary and resetting seekNum
        self.partial_Index.clear()
        self.dictPos.clear()
        print(f'Finished creating partial index json and text file for part {pNum}')
                
  
    def mergeTermDict(self, folder_name : str):
        # current directory
        cdir = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        
        # pi folder
        pi_folder = os.path.join(cdir, folder_name)
        
        # Separate the Partial_Index files 
        txtFilePath = []
        jsonFilePath = []
        
        for file in os.listdir(pi_folder):
            if file[-4:] == '.txt':
                txtFilePath.append(os.path.join(pi_folder, file))
            else:
                jsonFilePath.append(os.path.join(pi_folder, file))   
                
        # Merge the partial json files that hold {term : position} into a single file
        # Ex. {'cat' : [0, 123, 567]} means cat starts on pos 0 in part1.txt, pos 123 in part2.txt, pos 567 in part3.txt
        self.mergePositionDict(jsonFilePath)
        with open('mergedPosM4.json', 'r') as f:
            mergedTokPos = json.load(f)
        
        self.createFinalIndex(mergedTokPos, txtFilePath)
                        
    def mergePositionDict(self, jsonFilePath : list):
        ''' Merging the partial json files that hold the position of each term corresponding to their partial text file '''
        
        # Load the 1st partial json file as starting point for merged json file
        with open(jsonFilePath[0], 'r') as f:
            mergedTokPos = json.load(f)
        
        # Merges in 2nd & 3rd json file 
        for i in range(len(jsonFilePath) - 1):
            with open(jsonFilePath[i+1], 'r') as f:
                partTokPos = json.load(f)
                
            for token, pos in partTokPos.items():
                # if the token in 2nd/3rd partial json file exists in merged json file
                if token in mergedTokPos:
                    if i == 1 and len(mergedTokPos[token]) == 1:  # [1st, None, 3rd]
                        mergedTokPos[token].append(None)
                        mergedTokPos[token].append(pos[0])
                    else:
                        mergedTokPos[token].append(pos[0])
                # if the token in 2nd/3rd doesn't exist in merged json file
                else:
                    if i == 0: # [None, 2nd]
                        mergedTokPos[token] = [None, pos[0]]
                    if i == 1: # [None, None, 3rd]
                        mergedTokPos[token] = [None, None, pos[0]]

                    
        ''' 
        [None, 2nd]
        [1st, None, 3rd]
        [None, None, 3rd]
        '''
                    
        with open('mergedPosM4.json', 'w') as f:
            json.dump(mergedTokPos, f)
            
            
    def createFinalIndex(self, mergedTokPos : dict, txtFilePath : list):
        finalTokPos = {}      # Map {tokens : position} in final index text file
        seekNum = 0           # keep track of position 
        
        open('finalTermIndexM4.txt', 'a').close()        # Need to create finalTermIndex.txt file before opening in 'r+' mode
        with open('finalTermIndexM4.txt', 'r+') as ftxt:
            ''' {token : {docFreq: 2, idf: 0, posting: [{docID, doc_tf : 123, tags_contains}]}}'''
            for token, listOfPos in mergedTokPos.items():            
                startDictStr = '{' + f"'{token}' : "
                ftxt.write(startDictStr)
                
                innerDict = {'docFreq' : 0, 'idf' : 0, 'posting' : {'champList' : [], 'lowList' : []}}
                # For each position number corresponding to the partial text file 
                for i in range(len(listOfPos)):
                    if listOfPos[i] != None:
       
                        fpos = open(txtFilePath[i])          # Open the partial txt file (but not loading into memory)
                        fpos.seek(listOfPos[i])              # Seek the position to get to the line that holds the dictionary {term : posting}

                        tokDict = eval(fpos.readline().strip('\n'))      # str --> dict
                        fpos.close()
                        
                        innerDict['docFreq'] += tokDict[token]['docFreq'] # Combine the doc frequency 
                        innerDict['posting']['lowList'] += tokDict[token]['posting'] # Combine posting lists inside lowlist
                
                            
                innerDict['posting']['lowList'].sort(key = lambda x : x.get('doc_tf'), reverse = True)   # Sort posting by descending order of weighted doc tf
                innerDict['posting']['champList'] = innerDict['posting']['lowList'][:50]
                innerDict['posting']['lowList'] = innerDict['posting']['lowList'][50:]
                innerDict['idf'] = log(self.fileCounter / innerDict['docFreq'])               # Calculate idf for query 
                ftxt.write(str(innerDict) + "}\n")
                    
                # Map token & position for final index text
                finalTokPos[token] = seekNum
                
                
                # Set seekNum to the start of the next line
                ftxt.seek(seekNum)
                ftxt.readline()
                seekNum = ftxt.tell()
        
        # Dump the mappings of token & position for final index txt file in json file
        with open('finalPosM4.json', 'w') as fPos:
            json.dump(finalTokPos, fPos)
            
   

if __name__ == '__main__':
    obj = Indexer()

    # walk through dev folder
    obj.getFiles('DEV')
    #print(obj.fileCounter)
    obj.mergeTermDict('Partial_IndexM4')
    
