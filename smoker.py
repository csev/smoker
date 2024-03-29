import os, sys
import sqlite3
import requests
import re
from urllib.parse import urljoin
from urllib.parse import urlparse
from time import time
from bs4 import BeautifulSoup

class Smoker :

    database = 'smoker.sqlite'
    baseurl = 'http://localhost:8080'
    walk = 'random'   # Or breadth or depth
    maxdepth = 15
    useragent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:79.0) Gecko/20100101 Firefox/79.0'
    timeout = 240  # Broken.py sometimes take 10-20 seconds to scan the DB, default is 5 seconds

    def __init__(self, baseurl, database, walk=False) :
        self.baseurl = baseurl
        self.database = database
        self.walk = walk

    # If there are some extra starting points we want to add to the crawl that are not linked in the UI
    def extraStartingPoints(self, baseurl) :
        retval = list()
        return retval

    # Returns the cookies to use if login is successful
    def loginUser(self, baseurl) :
        return None

    # Some URLs we don't care if we get a particular kinf of error
    def ignoreError(self, code, url) :
        return False

    # When looking at a page with urls, which should not be added to the queue
    def dontVisit(self, href):
        return False

    # Once a page as been retrieved, we might look at the test for a traceback or erorr page
    def adjustCode(self, code, html, url) :
        return code

    # The main event
    def run(self, many) :
        conn = sqlite3.connect(self.database, timeout=self.timeout)
        cur = conn.cursor()

        cur.execute('''CREATE TABLE IF NOT EXISTS Pages
            (id INTEGER PRIMARY KEY, url TEXT UNIQUE, size INTEGER,
             code INTEGER, depth INTEGER, content_type TEXT, bad_id STRING, insert_at DOUBLE)''')

        cur.execute('''CREATE TABLE IF NOT EXISTS Html
            (id INTEGER PRIMARY KEY, url TEXT UNIQUE, html TEXT)''')

        cur.execute('''CREATE TABLE IF NOT EXISTS Links
            (from_id INTEGER, to_id INTEGER, UNIQUE(from_id, to_id))''')

        # Check to see if we are already in progress...
        # cur.execute('SELECT id,url FROM Pages WHERE html is NULL and code is NULL LIMIT 1')
        cur.execute('SELECT id,url FROM Pages WHERE code is NULL LIMIT 1')

        row = cur.fetchone()
        if row is not None:
            print("Restarting existing crawl.  Remove",self.database,"to start a 100% fresh crawl.")
        else:
            cur.execute('INSERT OR IGNORE INTO Pages (url, depth, insert_at) VALUES ( ?, ?, ? )', ( self.baseurl, 0, time()) )
            points = self.extraStartingPoints(self.baseurl)
            for point in points:
                cur.execute('INSERT OR IGNORE INTO Pages (url, depth, insert_at) VALUES ( ?, ?, ? )', ( point, 0, time()) )
            conn.commit()

        cookies = None
        ck = self.loginUser(self.baseurl)
        if ck != None : cookies = ck

        while True:
            many = many - 1
            if many < 0 : return

            if self.walk == 'depth':
                cur.execute('SELECT id,url,depth FROM Pages WHERE code is NULL ORDER BY depth DESC, insert_at, id LIMIT 1')
            elif self.walk == 'breadth' :
                cur.execute('SELECT id,url,depth FROM Pages WHERE code is NULL ORDER BY depth ASC, insert_at, id LIMIT 1')
            else :
                cur.execute('SELECT id,url,depth FROM Pages WHERE code is NULL ORDER BY random() LIMIT 1')
            try:
                row = cur.fetchone()
                # print row
                fromid = row[0]
                url = row[1]
                depth = row[2]
            except:
                print('No unretrieved HTML pages found')
                cur.execute('''SELECT count(*) FROM Pages''')
                row = cur.fetchone()
                total = row[0]
                print('Total pages:', total)
                cur.execute('''SELECT count(*) FROM Pages WHERE code <> 200''')
                row = cur.fetchone()
                ecount = row[0]
                print('Error pages:', ecount)
                many = 0
                break

            print(fromid, depth, url, end=' ')
            actualurl = url

            # If we are retrieving this page, there should be no links from it
            cur.execute('DELETE from Links WHERE from_id=?', (fromid, ) )
            try:
                hdrs = {"User-Agent": self.useragent}
                r = requests.get(url, cookies=cookies, headers=hdrs)

                actualurl = r.url
                code = r.status_code
                content_type = r.headers.get('Content-Type', False)
                content_length = int(r.headers.get('Content-Length', -1))

                # Is this a code from a url that we don't even want to bother recording
                if self.ignoreError(code, url):
                    cur.execute('DELETE from Pages WHERE url=?', (url, ) )
                    conn.commit()
                    continue

                cur.execute('UPDATE Pages SET code=?, size=?, content_type=?, insert_at=? WHERE url=?',
                        (code, content_length, content_type, time(), url) )

                if content_type is False or not content_type.startswith('text/html'):
                    print("Note non text/html page")
                    conn.commit()
                    continue

            except KeyboardInterrupt:
                print('')
                print('Program interrupted by user...')
                break
            except Exception as exc:
                print("Unexpected error")
                print(exc)
                cur.execute('UPDATE Pages SET code=?, size=?, content_type=?, insert_at=? WHERE url=?',
                        (999, 0, 'Exception', time(), url) )
                # cur.execute('UPDATE Pages SET code=?, size=?, content_type=?, html=?, insert_at=? WHERE url=?',
                        # (999, 0, 'Exception', str(exc), time(), url) )
                conn.commit()
                cur.execute('REPLACE INTO Html (url, html) VALUES (?, ?)', (url, str(exc)))
                conn.commit()
                continue

            # Actually get the material
            html = r.text
            if content_length < 0 : content_length = len(html)

            code = self.adjustCode(code, html, url)

            # Check for duplicate ids
            soup = BeautifulSoup(html, "html.parser")

            ids = dict()
            bad_id = None
            for x in soup():
                # print(x)
                the_id = x.get('id', None)
                # print(the_id)
                if the_id is not None :
                    if ids.get(the_id, None) is not None :
                        bad_id = the_id
                    else :
                        ids[the_id] = x

            print('('+str(len(html))+')', code, end=' ')
            # cur.execute('UPDATE Pages SET html=?, code=?, size=?, insert_at=? WHERE url=?', (html, code, content_length, time(), url) )
            cur.execute('UPDATE Pages SET code=?, size=?, insert_at=?, bad_id=? WHERE url=?', (code, content_length, time(), bad_id, url) )
            conn.commit()
            cur.execute('REPLACE INTO Html (url, html) VALUES (?, ?)', (url, html))
            conn.commit()

            # some pages make slightly new links that ultimately form a circle and so
            # we seem them as infinite depth - a cut off solves this
            if depth > self.maxdepth : continue

            # Retrieve all of the external links
            count = 0
            hrefs = list()
            tags = soup('a')
            for tag in tags:

                href = tag.get('href', None)
                if ( href is None ) : continue

                if self.dontVisit(href) :
                    # print('Skipping', href)
                    continue

                hrefs.append(href)

            tags = soup('link')
            for tag in tags:
                href = tag.get('href', None)
                if ( href is None ) : continue
                hrefs.append(href)

            tags = soup('script')
            for tag in tags:
                href = tag.get('src', None)
                if ( href is None ) : continue
                if href.startswith('javascript:') : continue
                hrefs.append(href)

            tags = soup('iframe')
            for tag in tags:
                href = tag.get('src', None)
                if ( href is None ) : continue
                hrefs.append(href)


            # Special for lines of the form
            # <meta http-equiv="refresh" content="0;url=/portal">
            check = '<meta http-equiv="refresh" content="0;url='
            pos = html.find(check)
            if pos > 1 :
                pos = pos + len(check)
                pos2 = html.find('"', pos)
                if pos2 > 0 :
                    href = html[pos+1:pos2]
                    hrefs.append(href)

            for href in hrefs:
                if href.startswith('javascript:') : continue
                if href.startswith('#') : continue

                # hrefs look like
                # - global with http or https
                # - relative and absolute like /abc
                # - relative without a slash
                # Current url may or may not end in a slash
                up = urlparse(href)
                aup = urlparse(actualurl)
                actualroot = aup.scheme + '://' + aup.netloc # No slash
                # print(href, up)
                # print(actualurl, actualroot)
                if ( len(up.scheme) > 1 ) :
                    pass  # Global href
                elif href.startswith("/") :
                    href = urljoin(actualroot, href)
                elif actualurl.endswith("/") : # in same folder
                    href = urljoin(actualurl, href)
                else : # Need to trim off the last path bit
                    pos = actualurl.rindex('/')
                    if pos > 0 :
                        href = actualurl[:pos+1] + href
                    else : # Hopefully never
                        print("WTF ??? ",actualurl,href)

                # Remove '/./' and '/../' before recording the URL
                pieces = href.split('/')
                newpieces = list()
                querystring = False
                for piece in pieces:
                    if querystring :
                        newpieces.append(piece)
                        continue

                    if '?' in piece:
                        newpieces.append(piece)
                        querystring = True
                        continue

                    if piece == '.' :
                        continue;

                    if piece == '..' :
                        if len(newpieces) > 0 :
                            newpieces.pop()
                            continue
                        continue;
                    newpieces.append(piece)

                newhref = '/'.join(newpieces)
                # if newhref != href: print('!!! ', href, newhref)
                href = newhref

                ipos = href.find('#')
                if ( ipos > 1 ) : href = href[:ipos]
                if ( href.endswith('/') ) : href = href[:-1]
                if ( len(href) < 1 ) : continue

        	# Check if the URL is in our spac2
                found = False
                if not href.startswith(self.baseurl) : continue

                # print('new link', href)
                cur.execute('INSERT OR IGNORE INTO Pages (url, depth, insert_at) VALUES ( ?, ?, ? )', ( href, depth+1, time()) )
                count = count + 1

                cur.execute('SELECT id FROM Pages WHERE url=? LIMIT 1', ( href, ))
                try:
                    row = cur.fetchone()
                    toid = row[0]
                except:
                    print('Could not retrieve id')
                    continue
                # print fromid, toid
                cur.execute('INSERT OR IGNORE INTO Links (from_id, to_id) VALUES ( ?, ? )', ( fromid, toid ) )

            conn.commit()

            print(count)

        cur.close()


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print()
        print("Example usage: smoker.py http://localhost:8080 100 depth|breadth|random")
        print()

    base = 'http://localhost:8080'
    many = 100
    walk = 'random'

    if len(sys.argv) > 1:
        base = sys.argv[1]

    if len(sys.argv) > 2:
        many = int(sys.argv[2])

    if len(sys.argv) > 3:
        walk = sys.argv[3]

    try:
        os.remove('smoker.sqlite')
    except OSError:
        pass

    app = Smoker(base, 'smoker.sqlite', walk)
    app.run(many);
