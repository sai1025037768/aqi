import re
import Spider
import urllib.request,urllib.robotparser,urllib.error,chardet
from urllib import parse

def link_crawler(seed_url, link_regex):
    """Crawl from the given seed URL following links matched by link_regex
    """
    crawl_queue = [seed_url]
    seen = set(crawl_queue)
    while crawl_queue:
        url = crawl_queue.pop()
        html = download(url)

        for link in get_links(html):

            if re.match(link_regex, link):
                link = parse.urljoin(seed_url, link)
                print(link)
                if link not in seen:
                    seen.add(link)
                    # crawl_queue.append(link)




def get_links(html):
    """Return a list of links from html
        """
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return  webpage_regex.findall(html)


def download(url, user_agent='wswp', num_retries = 2):
    print('Downloading:', url)
    headers = {'User-agent' : user_agent}
    request = urllib.request.Request(url, headers = headers)

    try:
        html = urllib.request.urlopen(request).read()
        charset = chardet.detect(html)['encoding']
        html = html.decode(charset)
        # if charset == 'GB2312' or charset == 'gb2312':
        #     html = html.decode('GBK').encode('UTF-8')
        # else:
    except urllib.error.URLError as e:
        print('Download error', e.reason)
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 6:
                return download(url, user_agent, num_retries - 1)
    return html