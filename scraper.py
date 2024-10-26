import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup

def scraper(url, soup):
    links = extract_next_links(url, soup)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, soup):
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
        #Stripped Strings is used to get all the string content out of the webpage. Check BeautifulSoup4 docs

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
        if re.search(r"\d{4}-\d{2}-\d{2}|\b\d{4}-\d{2}\b", parsed.path):
            return False
        if re.search(r"filter", parsed.query):

            return False

        

        #Look into checking for links that are single paged pdf files. Files that return replacement letters.
        
        valid_domains = {"ics.uci.edu", "www.cs.uci.edu", "www.informatics.uci.edu", "www.stat.uci.edu", "today.uci.edu/department/information_computer_sciences"}
        if parsed.netloc in valid_domains:
                return True

    except TypeError:
        print ("TypeError for ", parsed)
        raise
