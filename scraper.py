import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from crawler.database import DataBase
from crawler.worker import tokenizer, computeWordFrequencies

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
    DataBase.add_scraped(url)

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
            parsed.path.lower() + parsed.query.lower()
        ):
            return False

        '''
        Searches the path and the query to find out if there are dates.
        It only find dates like 2004-05-1990 and 2004-05.
        After running it looks like it does not get stuck in the calendar anymore
        '''
        if re.search(r"\d{4}-\d{2}-\d{2}|\b\d{4}-\d{2}\b|login", parsed.path + parsed.query):
            return False
        if re.search(r"filter", parsed.query):
            return False

        

        #Look into checking for links that are single paged pdf files. Files that return replacement letters.
        
        valid_domains = {"ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu", "today.uci.edu/department/information_computer_sciences"}
        for domains in valid_domains:
            if domains in parsed.netloc:
                return True

    except TypeError:
        print ("TypeError for ", parsed)
        raise
