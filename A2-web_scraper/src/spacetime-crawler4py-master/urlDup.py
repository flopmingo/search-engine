stopWordSet = set()

with open('stopwords.txt', 'r', encoding = 'utf8') as stopwords:
    for line in stopwords:
        stopWordSet.add(line)
    