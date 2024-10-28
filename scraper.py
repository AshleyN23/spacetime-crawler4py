import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from crawler.database import DataBase
import hashlib

def scraper(url, resp):
    # links = extract_next_links(url, soup)
    # return [link for link in links if is_valid(link)]

    # parse the response content with beautiful soup
    # soup = BeautifulSoup(resp.raw_response.content, "lxml")
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)] if links else []



def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content


    # check if URL has been scraped or if the response status isn't OK (not 200)
    if resp.status != 200 or DataBase.is_scraped(url) or DataBase.is_blacklisted(url):
        DataBase.blacklist_url(url)
        return []
    
    # parse response with beautiful soup
    soup = BeautifulSoup(resp.raw_response.content, "lxml")

    # Get page text and token count
    # TODO: check if this counts html comments
    text = soup.get_text()
    space_delemited_text = re.sub('\s+',' ',text)

    # Tokenize and store tokens in the database
    tokens = tokenizer(space_delemited_text)
    freq = computeWordFrequencies(tokens)
    hashNum = simHash(freq)
    if checkSimilar(DataBase.hashes, hashNum):
        DataBase.blacklist_url(url)
        return []
    DataBase.add_hash(hashNum)
    DataBase.add_tokens(tokens)
    # updates max words if total amount of tokens is greater than previous max word count
    DataBase.update_max_words(url, len(tokens))

    # Initialize a set for unique, valid links
    valid_links = set()

    # Extract and validate hyperlinks
    for link in soup.find_all('a', href=True):
        child_url = link.get('href').split('#')[0]  # Remove fragments

        # Resolve relative URLs and add valid URLs to the set
        if child_url and is_valid(child_url) and not DataBase.is_seen(child_url):
            valid_links.add(child_url)
            DataBase.add_seen(child_url)  # Mark URL as seen

    # Add the URL to the scraped set
    DataBase.add_scraped(urlparse(url).netloc)
    

    return list(valid_links)


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        
        if parsed.scheme not in set(["http", "https"]):
            return False
        if re.match(
            r".*\b(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4|ppsx|rpm"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)\b.*", 
            parsed.path.lower() + parsed.query.lower() #Check if the path or the query contains any of these words
        ):
            return False

        '''
        Searches the path and the query to find out if there are dates.
        It only find dates like 2004-05-1990 and 2004-05.
        
        '''
        if re.search(r"\d{4}-\d{2}-\d{2}|\b\d{4}-\d{2}\b|login", parsed.path + parsed.query):
            return False
        if re.search(r"filter|post_type=tribe_events&eventDisplay", parsed.query):
            return False

        

        
        valid_domains = {"ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu", "today.uci.edu/department/information_computer_sciences"}
        for domains in valid_domains:
            if domains in parsed.netloc:
                #Add unique URL
                DataBase.add_unique_url(parsed.netloc)
                return True

    except TypeError:
        print ("TypeError for ", parsed)
        raise



def checkSimilar(hashes, currentSimHash):
    if currentSimHash in hashes:
        return True
    for items in hashes:
        x = int(items,2) ^ int(currentSimHash, 2) # XOR to find differing bits
        distance = 0
        while x:
            distance += x & 1  # Count the number of 1's in the result
            x >>= 1
        if distance <= 3:
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

    for word in listOfWords.split():
        if len(word) > 1 and word not in stopWords:
            tokens.append(word.lower())
    return tokens

def computeWordFrequencies(tokens: list): 
    '''
    Time Complexity: O(n log n) - Iterates through the tokens list (O(n)) to populate 
    the dictionary, then sorts it using Python's sorted function, which has 
    an average time complexity of O(n log n) (Timsort algorithm).
    '''
    
    tokenMap = {}
    
    for values in tokens:
        values = bin(int(hashlib.sha256(values.encode()).hexdigest(), 16))[2::]
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
