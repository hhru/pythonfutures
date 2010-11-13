"""Compare the speed of downloading URLs sequentially vs. using futures."""

import datetime
import functools
import futures.thread
import time
import timeit
import urllib2

URLS = ['http://www.google.com/',
        'http://www.apple.com/',
        'http://www.ibm.com',
        'http://www.thisurlprobablydoesnotexist.com',
        'http://www.slashdot.org/',
        'http://www.python.org/',
        'http://www.bing.com/',
        'http://www.facebook.com/',
        'http://www.yahoo.com/',
        'http://www.youtube.com/',
        'http://www.blogger.com/']

def load_url(url, timeout):
    return urllib2.urlopen(url, timeout=timeout).read()

def download_urls_sequential(urls, timeout=60):
    url_to_content = {}
    for url in urls:
        try:
            url_to_content[url] = load_url(url, timeout=timeout)
        except:
            pass
    return url_to_content

def download_urls_with_executor(urls, executor, timeout=60):
    try:
        url_to_content = {}
        future_to_url = dict((executor.submit(load_url, url, timeout), url)
                             for url in urls)

        for future in futures.as_completed(future_to_url):
            try:
                url_to_content[future_to_url[future]] = future.result()
            except:
                pass
        return url_to_content
    finally:
        executor.shutdown()

def main():
    for name, fn in [('sequential',
                      functools.partial(download_urls_sequential, URLS)),
                     ('processes',
                      functools.partial(download_urls_with_executor,
                                        URLS,
                                        futures.ProcessPoolExecutor(10))),
                     ('threads',
                      functools.partial(download_urls_with_executor,
                                        URLS,
                                        futures.ThreadPoolExecutor(10)))]:
        print name.ljust(12),
        start = time.time()
        url_map = fn()
        print '%.2f seconds (%d of %d downloaded)' % (time.time() - start,
                                                      len(url_map),
                                                      len(URLS))

if __name__ == '__main__':
    main()
