# class used to store all things necessary for report

class DataBase:
    # Class-level variables
    allTokens = dict()  # {token: frequency}
    scraped = set()  # URLs we've successfully extracted from or blacklisted
    seen = set()  # URLs that we've visited
    unique_urls = dict() # Unique subdomains encountered and its pages{domain: size}
    blacklistURL = set()  # Blacklisted URLs
    hashes = set() #Previous hashes (Used to check similarity)

    maxWords = ["", 0]  # [URL with max words, word count]

    @staticmethod
    def add_scraped(url):
        DataBase.unique_urls[url] += 1
        DataBase.scraped.add(url)

    @staticmethod
    def is_scraped(url):
        return url in DataBase.scraped

    @staticmethod
    def add_seen(url):
        DataBase.seen.add(url)

    @staticmethod
    def is_seen(url):
        return url in DataBase.seen

    @staticmethod
    def blacklist_url(url):
        DataBase.blacklistURL.add(url)

    @staticmethod
    def is_blacklisted(url):
        return url in DataBase.blacklistURL

    @staticmethod
    def add_unique_url(url):
        if url not in DataBase.unique_urls:
            DataBase.unique_urls[url] = 1

    @staticmethod
    def update_max_words(url, word_count):
        if word_count > DataBase.maxWords[1]:
            DataBase.maxWords = [url, word_count]

    @staticmethod
    def add_tokens(tokens):
        for token in tokens:
            if token in DataBase.allTokens:
                DataBase.allTokens[token] += 1
            else:
                DataBase.allTokens[token] = 1

    @staticmethod
    def add_hash(hash):
        DataBase.hashes.add(hash)
    

    @staticmethod
    def export_report(filename="URLS.txt"):
        with open(filename, "w") as f:
            f.write("SCRAPED URLs:\n")
            for url in DataBase.scraped:
                f.write(f"{url}\n")

            f.write("\n\nUNIQUE DOMAINS:\n")
            for url in DataBase.unique_urls:
                f.write(f"{url}\n")

            f.write("\n\nBLACKLISTED URLs:\n")
            for url in DataBase.blacklistURL:
                f.write(f"{url}\n")

            f.write("\n\nLONGEST PAGE (IN TERMS OF WORD COUNT):\n")
            f.write(f"Website URL: {DataBase.maxWords[0]}\n")
            f.write(f"Number of words: {DataBase.maxWords[1]}\n")

            f.write("\n\nTOKEN FREQUENCIES:\n")
            for token, count in DataBase.allTokens.items():
                f.write(f"{token}: {count}\n")
