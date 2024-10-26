import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from bs4 import Comment


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


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
        if values not in tokenMap:
            tokenMap[values] = 0
        tokenMap[values] += 1
    
    tokenMap = dict(sorted(tokenMap.items(), key=lambda x: x[1], reverse=True)) 
    return tokenMap


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
    url_list = []
    if (resp and resp.raw_response):
        soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
        #Stripped Strings is used to get all the string content out of the webpage. Check BeautifulSoup4 docs
        #tokens = tokenizer(list(soup.stripped_strings)) #I will leave this here and use it later to keep track of the word frequency of each url.
        #freq = computeWordFrequencies(tokens)
        for link in soup.find_all('a'):
            if link.get('href'):
                url_list.append(link.get('href').split('#')[0])
    return url_list

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", 
            parsed.path.lower()
        ):
            return False

        '''
        Searches the path and the query to find out if there are dates.
        It only find dates like 2004-05-1990 and 2004-05.
        After running it looks like it does not get stuck in the calendar anymore
        '''
        if re.search(r"\d{4}-\d{2}-\d{2}|\b\d{4}-\d{2}\b", parsed.path + parsed.query):
            return False

        

        #Look into checking for links that are single paged pdf files. Files that return replacement letters.
        
        valid_domains = {"ics.uci.edu", "www.cs.uci.edu", "www.informatics.uci.edu", "www.stat.uci.edu", "today.uci.edu/department/information_computer_sciences"}
        if parsed.netloc in valid_domains:
                return True

    except TypeError:
        print ("TypeError for ", parsed)
        raise
