from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
from bs4 import BeautifulSoup
import hashlib




class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.uniqueURLs = 0
        self.uniqueSet = set()       
        self.hashes = set() 
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)

        
    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            if (resp and resp.raw_response):
                soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
                tokens = tokenizer(list(soup.stripped_strings))
                freq = computeWordFrequencies(tokens)
                hashNum = simHash(freq)
                if not checkSimilar(self.hashes, hashNum):
                    scraped_urls = scraper.scraper(tbd_url, soup)
                    self.hashes.add(hashNum)
                else:
                    scraped_urls = []
            for scraped_url in scraped_urls:
                '''
                Added by Rudy. This part of the code keeps track of the UNIQUE URLS
                '''
                if scraped_url not in self.uniqueSet:
                    self.uniqueSet.add(scraped_url)
                    self.uniqueURLs += 1
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
        print(self.uniqueURLs)



def checkSimilar(hashes, currentSimHash):
    if currentSimHash in hashes:
        return True
    for items in hashes:
        x = int(items,2) ^ int(currentSimHash, 2) # XOR to find differing bits
        distance = 0
        while x:
            distance += x & 1  # Count the number of 1's in the result
            x >>= 1
        if distance <= 20:
            print(distance)
            return True
    return False


'''
Tokenizer and Freq added by Rudy. Used for tokenizing the text and checking the freq of each word.
Stop words are not included. The tokenizer is changed a bit so that it also includes some special characters
like ph.d and b.s. where the special characters are used for the meaning.

'''

def tokenizer(listOfWords):
    tokens = []

    stopWords = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no",
    "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our",
    "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd",
    "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that",
    "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this",
    "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't",
    "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's",
    "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom",
    "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll",
    "you're", "you've", "your", "yours", "yourself", "yourselves"
    }

    for words in listOfWords:
        words = words.split()
        for word in words:
            if word not in stopWords and len(word) > 1:
                tokens.append(bin(int(hashlib.sha256(word.encode()).hexdigest(), 16))[2::])
    return tokens

def computeWordFrequencies(tokens: list): 
    '''
    Time Complexity: O(n log n) - Iterates through the tokens list (O(n)) to populate 
    the dictionary, then sorts it using Python's sorted function, which has 
    an average time complexity of O(n log n) (Timsort algorithm).
    '''
    
    tokenMap = {}
    
    for values in tokens:
        if values not in tokenMap:
            tokenMap[values] = 0
        tokenMap[values] += 1
    
    tokenMap = dict(sorted(tokenMap.items(), key=lambda x: x[1], reverse=True)) 
    return tokenMap


'''
SimHashing: (Used for finding if two texts are similar)
To sim hash add or subtract the hashString to the index at hashNum
Go through this with every token and store the result in hashNum
When this is done continue go through the hashNum and append the values to a hashString
Turn the hashString back to hex and return the hex

For better detailed description look up Sim Hashing Algorithm.
'''

def simHash(freq):
    hashNum = [0] * 256 #Initialize a 256 bit array since I use sha256
    for bits,frequency in freq.items():
        for i in range(len(bits)):
            if bits[i] == "1":
                hashNum[i] += (1 * frequency)
            else:
                hashNum[i] -= (1 * frequency)
    hashString = ""
    for i in range(len(hashNum)):
        if hashNum[i] > 0:
            hashString += "1"
        else:
            hashString += "0"
    return hashString
