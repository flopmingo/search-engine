import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup # HTML parser
import lxml
import tk
import collections

#Interview Question #1
seen_links = set()

# Interview Question #2
longCount = 0
longUrl = ""

#Interview Question #3
commonDict = {}

#Interview Question #4
icsFreq = {}

def scraper(url, resp):
    links = extract_next_links(url, resp) # links = list of valid, unique, defrag links 
    return [link for link in links if is_valid(link)] # return the links if they're also valid as well


def extract_next_links(url, resp):
    # Implementation requred.

    # store our defragmented urls to return to the scraper method
    defragmented_links = []
    
    # GitHub repo says statuses 400-599 are errors so 200-399 are valid and worth checking
    if (200 <= resp.status and resp.status < 400) and is_valid(url):
        # Use BS4 to make the HTML content parseable
        raw_text = resp.raw_response.text
        soup = BeautifulSoup(raw_text, 'lxml')
        
        tok = tk.Tokenizer()
        totalWordList, tokenList = tok.tokenize(soup.get_text())   # returns list of tokens that do not include stop words
        
        # Check if token link has more than 100 tokens, if not it is considered low textual information
        if len(tokenList) > 100: 
        
            # search for all links in the html
            for link in soup.findAll('a'):
                # check that there is an href (link) in the a tag
                if link.get('href'):
                    # later -- check if page has high textual info

                    # defragment the link
                    cleaned_link = link.get('href').split('#')[0]
                    # check that we have not seen this link already (O(1) lookup via a set)
                    if cleaned_link not in seen_links:
                        a = defragmented_links.append(cleaned_link)
                        seen_links.add(cleaned_link)

            # Store all the url crawler has crawled 
            storeUrl(url)
            
            # Find longest page
            findLongest(totalWordList, url)
            
            # Find top 50 common words
            findCommon(tokenList, tok)

            #Store icsDomain frequencies
            findICSFreq(url)

    return defragmented_links

    

def is_valid(url):
    try:
        parsed = urlparse(url)
        
        #Scheme check
        if parsed.scheme not in set(["http", "https"]):
            return False

        # Domain Check
        domain_check = re.match(r"((.*\.(ics\.uci\.edu|cs\.uci\.edu|informatics\.uci\.edu|stat\.uci\.edu)))", parsed.netloc)

        if not (domain_check or ('today.uci.edu' == parsed.netloc and re.match(r"\/department\/information_computer_sciences\/.*", 
                parsed.path))):
            return False
       
        if re.match(r".*wics\.ics\.uci\.edu", parsed.netloc) and '/events' in parsed.path:
            return False
    
        # Path Check
        paths = parsed.path.split('/')
        check_paths = {'css', 'js', 'gif', 'jpe?g', 'ico', 'wav', 'avi', 'mov', 'mpeg', 'ram', 'm4v', 'mkv', 'ogg', 'pdf', 'ps',
                       'eps', 'tex', 'ppt', 'pptx', 'doc', 'docx', 'xls', 'xlsx', 'names', 'data', 'dat', 'exe', 'bz2', 'tar', 'msi',
                       'bin', '7z', 'psd', 'dmg', 'iso', 'epub', 'dll', 'cnf', 'tgz', 'sha1', 'thmx', 'mso', 'arff', 'rtf', 'jar',
                       'csv', 'rm', 'smil', 'wmv', 'swf', 'wma', 'zip', 'rar', 'gx', 'wp-content', 'wp-login'}
                        # included wp-content for pdfs 
        for i in paths:
            if i in check_paths:
                return False

        # get rid of comments, share links, download calendar, action queries that return 403 (lost password, download, login)
        if re.match(r"((replytocom|share|ical)=.*)|action=.*", parsed.query): 
            return False
        
        # idk how to get out ;u;
        if url == "http://www.ics.uci.edu/~shantas/publications/20-secret-sharing-aggregation-TKDE-shantanu":
            return False
        
        # our link is not one of these file extensions
        return not re.match(r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|ppsx|r|py|odc|txt|java|c|cpp)$", parsed.path.lower())


    except TypeError:
        print ("TypeError for ", parsed)
        raise
        
# Output links that are valid & have been parsed // Interview Question #1
def storeUrl(url):
    with open('url5.txt', 'a', encoding = 'utf8') as urlFile:
        urlFile.write(url + '\n')
    urlFile.close()
        
# Outputs longest page & 50 most common words // Interview Question #2 
def findLongest(totalWordList, url):    
    # Find longest page
    global longCount
    
    # if length of total word list (including stop words) > longCount, update longCount and longUrl
    if len(totalWordList) > longCount:   
        longCount = len(totalWordList)
        
        global longUrl
        longUrl = url
        
        # output the current longCount & longUrl into a file
        with open('longest.txt5', 'a', encoding = 'utf8') as longestFile:
            longestFile.write(str(longCount) + ' : ' + longUrl + '\n')  
        longestFile.close()
    

def findCommon(tokenList, tok):
    # Find most common words which excludes stop words
    global commonDict
    
    # Updates word frequencies in commonDict 
    tok.computeWordFrequencies(tokenList, commonDict)  
    
    # sorts dictionary items based on decreasing frequency then alphabetical order
    sorted_common = sorted(commonDict.items(), key = (lambda x : (-x[1], x[0])))

    # Output current, sorted dictionary items into file
    with open('common.txt5', 'w', encoding = 'utf8') as commonFile:
        commonFile.write(str(sorted_common))
    commonFile.close()
    

def findICSFreq(url):
    global icsFreq
    parsed = urlparse(url)
    
    # if the link is in the ics.uci.edu domain, add/update the link's frequency in icsFreq dictionary
    if re.match(r".*ics\.uci\.edu.*", parsed.netloc):
        if parsed.netloc.lower() in icsFreq:
            icsFreq[parsed.netloc.lower()] += 1
        else:
            icsFreq[parsed.netloc.lower()] = 1
    
    # Sort icsFreq items in alphabetical order and output into file
    sorted_ics = sorted(icsFreq.items(), key = (lambda x : x[0]))
    with open('icsFreq5.txt', 'w', encoding = 'utf8') as icsFile:
        icsFile.write(str(sorted_ics))
    icsFile.close()
    