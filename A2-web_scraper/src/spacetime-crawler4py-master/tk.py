import re
import sys

class Tokenizer():
    stopWordSet = {'nonetheless', 'some', 'hence', 'youre', 'becomes', 'rather', 'afterwards', 'mostly', 'run', 'actually', 'every', 'f', 'because', 'immediate', 'vs', 'twice', 'truly', 'says', 'went', 'here', 'don', 'll', 'few', 'shes', 'date', 'where', 'seems', 'na', 'said', 'v', 'your', 'beforehand', 'important', 'made', 'about', 'need', 'those', 'everyone', 'six', 'try', 'placed', 'whim', 'thanks', 'very', 'beyond', 'nobody', 'theyre', 'vol', 'please', 'out', 'resulting', 'let', 'already', 'que', 'soon', 'new', 'until', 'showed', 'were', 'the', 'somehow', 'meantime', 'anything', 'besides', 'do', 'ed', 'look', 'liked', 'when', 'regardless', 'more', 'brief', 'fix', 'whereby', 'sent', 'l', 'g', 'goes', 'inward', 'z', 'quite', 'following', 'relatively', 'someone', 'unless', 'shed', 'whatever', 'knows', 'therein', 'four', 'know', 'whom', 'no', 'specifically', 'related', 'somewhat', 'hers', 'significantly', 'above', 'n', 'pages', 'wherein', 'whole', 'eight', 'before', 'just', 'kept', 'us', 'end', 'somewhere', 'miss', 'trying', 'what', 'nos', 'themselves', 'at', 'value', 'it', 'you', 'strongly', 'necessary', 'seeing', 'other', 'wouldnt', 'last', 'uses', 'qv', 'mug', 'becoming', 'with', 'whence', 'immediately', 'nothing', 'a', 'affected', 'certainly', 'have', 'five', 'keep', 'widely', 'several', 'shall', 'k', 'et', 'thru', 'was', 'affects', 'overall', 'viz', 'of', 'primarily', 'given', 'million', 'unlikely', 'yet', 'plus', 'used', 'again', 'approximately', 'from', 'there', 'means', 'why', 'hes', 'often', 'able', 'mainly', 'only', 'apparently', 'yours', 'others', 'across', 'whos', 'though', 'might', 'lets', 'formerly', 'towards', 'shows', 'get', 'old', 'doing', 'after', 'omitted', 'any', 'necessarily', 'importance', 'abst', 'ts', 'wed', 'shown', 'ff', 'had', 'y', 'own', 'gives', 'below', 'alone', 'each', 'still', 'something', 'thereto', 'name', 'readily', 'during', 'come', 'inc', 'next', 'elsewhere', 'keeps', 'thereafter', 'amongst', 'among', 'seeming', 'take', 'didn', 'provides', 'edu', 'former', 'using', 'kg', 'potentially', 'many', 'wants', 'that', 'anyway', 'neither', 'containing', 'd', 'least', 'home', 'ours', 'til', 'thereof', 'me', 'near', 'use', 'probably', 'according', 'sec', 'been', 'act', 'latter', 'research', 'wherever', 'either', 'otherwise', 'therere', 'far', 'for', 'useful', 'also', 'causes', 'be', 'successfully', 'heres', 'his', 'w', 'ending', 'or', 'thereupon', 'has', 'theres', 'noone', 'poorly', 'mean', 'really', 'enough', 'unlike', 'got', 'whoever', 'thered', 'put', 'slightly', 'begins', 'follows', 'behind', 'having', 'even', 'ought', 'yourselves', 'such', 'thats', 'whereupon', 'believe', 'my', 'particularly', 'obtained', 'took', 'herself', 'ml', 'biol', 'line', 'oh', 'nay', 'whose', 'hereby', 'certain', 'eg', 'say', 'specify', 'similarly', 'welcome', 'else', 'our', 'right', 'wasnt', 'per', 'somethan', 'ok', 'meanwhile', 'aside', 'gotten', 'these', 'should', 'beginnings', 'isn', 'between', 'cause', 'invention', 'youd', 'nor', 'go', 'must', 'although', 'usually', 't', 'known', 'everybody', 'hereupon', 'hardly', 'through', 'little', 'did', 'sufficiently', 'u', 'who', 'think', 'm', 'myself', 'sub', 'him', 'happens', 'both', 'instead', 'another', 'o', 'anyways', 'adj', 'same', 'lest', 'ran', 'self', 'to', 'almost', 'wheres', 'may', 'an', 'anymore', 'noted', 'namely', 'normally', 'words', 'world', 'latterly', 'past', 'sometimes', 'unto', 'via', 'whereas', 'proud', 'anyhow', 'and', 'effect', 'al', 'than', 'this', 'results', 'down', 'getting', 'once', 'never', 'nine', 'nearly', 'id', 'anywhere', 'tell', 'x', 'whereafter', 'upon', 'can', 'throughout', 'done', 'first', 'whomever', 'by', 'km', 'however', 'itd', 'since', 'everywhere', 'could', 'ourselves', 'merely', 'werent', 'refs', 'he', 'therefore', 'contains', 'vols', 'perhaps', 'owing', 'predominantly', 'added', 'substantially', 'th', 'co', 'seemed', 'ord', 'mg', 'together', 'then', 'himself', 'make', 'see', 'usefulness', 'forth', 'obtain', 'needs', 'un', 'ups', 'moreover', 'briefly', 'nd', 'resulted', 'tries', 'e', 'im', 'does', 'regards', 'arent', 'www', 'tends', 'beside', 'due', 'into', 'quickly', 'ltd', 'too', 'comes', 'promptly', 'tip', 'begin', 've', 'beginning', 'showns', 'somebody', 'gone', 'whither', 'c', 'ah', 'haven', 'all', 'yes', 'furthermore', 'wont', 'seven', 'unfortunately', 'information', 'now', 'com', 'throug', 'previously', 'saw', 'anyone', 're', 'so', 'anybody', 'r', 'her', 'later', 'they', 'recent', 'wish', 'ever', 'under', 'am', 'available', 'become', 'way', 'usefully', 'announce', 'is', 'seem', 'theyd', 'contain', 'outside', 'pp', 'index', 'maybe', 'hed', 'accordingly', 'regarding', 'them', 'came', 'specified', 'would', 'on', 'hereafter', 'possibly', 'onto', 'like', 'around', 'section', 'thousand', 'off', 'asking', 'its', 'non', 'theirs', 'auth', 'similar', 'thanx', 'different', 'looks', 'toward', 'we', 'ask', 'significant', 'shouldn', 'much', 'accordance', 'sup', 'herein', 'gave', 'sorry', 'etc', 'how', 'found', 'not', 'selves', 'none', 'recently', 'thoughh', 'ref', 'show', 'page', 'zero', 'their', 'i', 'respectively', 'yourself', 'h', 'tried', 'thank', 'especially', 'mr', 'hasn', 'giving', 'up', 'affecting', 'looking', 'obviously', 'always', 'nowhere', 'along', 'sure', 'while', 'nevertheless', 'howbeit', 'hither', 'gets', 'ca', 'back', 'whod', 'lately', 'less', 'specifying', 'give', 'stop', 'as', 'okay', 'awfully', 'taken', 'further', 'without', 'makes', 'which', 'are', 'b', 'thou', 'whenever', 'two', 'if', 'possible', 'q', 'most', 'everything', 'likely', 'various', 'j', 'hid', 'hundred', 'indeed', 'suggest', 'fifth', 'ie', 'ex', 'aren', 'but', 'whats', 'couldnt', 'sometime', 'seen', 'one', 'she', 'against', 'particular', 'cannot', 'followed', 'hi', 'being', 'ones', 'saying', 'itself', 'in', 'eighty', 'taking', 'thereby', 'became', 'p', 'thus', 'mrs', 'over', 'doesn', 'part', 'willing', 'rd', 'within', 'ninety', 's', 'want', 'arise', 'away', 'thence', 'whether', 'downwards', 'except', 'largely', 'present'}

    def __init__(self):
        pass

    def tokenize(self, page_text: str) -> list:
        ''' Time Complexity O(n^2) (nested for-loop) '''
        totalResult = []
        tokenResult = []

        # Treat the file as an interator to efficiently read large text
        for line in page_text.split('\n'):
            # split line on all non alphanumeric chars (A-Z and 0-9)
            for word in re.split('[^A-Z0-9a-z]', line):
                # if it is an empty string it provides no value so ignore
                if len(word) > 0:
                    cleaned_word = word.lower()
                    totalResult.append(cleaned_word)
                    # if word not a stop word, append to tokenResult
                    if cleaned_word not in Tokenizer.stopWordSet:
                        tokenResult.append(cleaned_word)

        return totalResult, tokenResult

    def computeWordFrequencies(self, tokens: list, commonWords: dict):
        ''' Time Complexity O(n) '''
        for token in tokens:
            
            if token in commonWords:
                commonWords[token]+=1
            else:
                commonWords[token] = 1


    def printFrequencies(self, frequencies: dict) -> None:
        ''' Time Complexity O(n*logn) (sorting the tuple list) '''
        sorted_freqs = sorted(frequencies.items(), key=lambda x: x[1], reverse=True) # sort in decreasing order by value

        for token, freq in sorted_freqs:
            print(token+" => "+str(freq))

if __name__ == '__main__':
    pass