import sqlite3
import requests
import re
from urllib.parse import urljoin
from urllib.parse import urlparse
from time import time
from bs4 import BeautifulSoup

def isWicket(url) :
    if url.find('ILinkListener') > 0 : return True
    if re.search('\?[0-9]+-[0-9]+', url) : return True
    return False

conn = sqlite3.connect('smoker.sqlite')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS Pages
    (id INTEGER PRIMARY KEY, url TEXT UNIQUE, html TEXT, size INTEGER,
     code INTEGER, content_type TEXT, insert_at DOUBLE, old_rank REAL, new_rank REAL)''')

cur.execute('''CREATE TABLE IF NOT EXISTS Links
    (from_id INTEGER, to_id INTEGER, UNIQUE(from_id, to_id))''')

cur.execute('''CREATE TABLE IF NOT EXISTS Webs (url TEXT UNIQUE)''')

# Check to see if we are already in progress...
cur.execute('SELECT id,url FROM Pages WHERE html is NULL and code is NULL ORDER BY insert_at, id LIMIT 1')
row = cur.fetchone()
if row is not None:
    print("Restarting existing crawl.  Remove smoker.sqlite to start a fresh crawl.")
else :
    starturl = input('Enter web url or enter: ')
    if ( len(starturl) < 1 ) : starturl = 'http://localhost:8080'
    # if ( len(starturl) < 1 ) : starturl = 'http://localhost:8888/py4e'
    if ( starturl.endswith('/') ) : starturl = starturl[:-1]
    web = starturl
    if ( starturl.endswith('.htm') or starturl.endswith('.html') ) :
        pos = starturl.rfind('/')
        web = starturl[:pos]

    if ( len(web) > 1 ) :
        cur.execute('INSERT OR IGNORE INTO Webs (url) VALUES ( ? )', ( web, ) )
        cur.execute('INSERT OR IGNORE INTO Pages (url, html, new_rank, insert_at) VALUES ( ?, NULL, 1.0, ? )', ( starturl, time()) )
        conn.commit()

# Get the current webs
cookies = None
cur.execute('''SELECT url FROM Webs''')
webs = list()
for row in cur:
    val = str(row[0])
    if val.startswith('http://localhost:8080') :
        print("setting up sakai")
        portal = "http://localhost:8080/portal";
        r = requests.get(portal)
        cookies = r.cookies
        print(cookies)
        login = "http://localhost:8080/portal/relogin";
        # payload = {'eid': 'hirouki', 'pw': 'p', 'submit': 'Log in'}
        payload = {'eid': 'admin', 'pw': 'admin', 'submit': 'Log in'}
        r = requests.post(login, cookies=cookies, data=payload)
    webs.append(str(row[0]))

print(webs)

many = 0
while True:
    if ( many < 1 ) :
        sval = input('How many pages:')
        if ( len(sval) < 1 ) : break
        many = int(sval)
    many = many - 1

    cur.execute('SELECT id,url FROM Pages WHERE html is NULL and code is NULL ORDER BY insert_at,id LIMIT 1')
    try:
        row = cur.fetchone()
        # print row
        fromid = row[0]
        url = row[1]
    except:
        print('No unretrieved HTML pages found')
        many = 0
        break

    print(fromid, url, end=' ')
    actualurl = url

    # If we are retrieving this page, there should be no links from it
    cur.execute('DELETE from Links WHERE from_id=?', (fromid, ) )
    try: 
        r = requests.get(url, cookies=cookies)

        actualurl = r.url
        code = r.status_code
        content_type = r.headers.get('Content-Type', False)
        content_length = int(r.headers.get('Content-Length', -1))
        
        # Yeah wicket sucks
        if code == 404 and isWicket(url):
            print("Wicket encodes state into URLs which leads to later 404s");
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
        cur.execute('UPDATE Pages SET code=?, size=?, content_type=?, html=?, insert_at=? WHERE url=?',
                (999, 0, 'Exception', str(exc), time(), url) )
        continue

    # Actually get the material
    html = r.text
    if content_length < 0 : content_length = len(html)

    if re.search('NullPointerException', html) :
        print("\nNullPointerException\n")
        code = 450
    elif code == 200 and re.search('HTTP Status 404.*Apache Tomcat', html) :
        print("\nHTTP Status 404.*Apache Tomcat\n")
        code = 404
    elif code == 200 and re.search('Apache Tomcat', html) :
        print("\nApache Tomcat\n")
        code = 454

    print('('+str(len(html))+')', code, end=' ')
    cur.execute('INSERT OR IGNORE INTO Pages (url, html, new_rank, insert_at) VALUES ( ?, NULL, 1.0, ? )', ( url, time()) )
    cur.execute('UPDATE Pages SET html=?, code=?, size=?, insert_at=? WHERE url=?', (html, code, content_length, time(), url) )
    conn.commit()

    soup = BeautifulSoup(html, "html.parser")

    # Retrieve all of the external links
    count = 0
    hrefs = list()
    tags = soup('a')
    for tag in tags:
        href = tag.get('href', None)
        if ( href is None ) : continue

        if '/portal/logout' in href : continue
        # Always a helper
        if 'ResourcePicker/tool' in href : continue
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

        ipos = href.find('#')
        if ( ipos > 1 ) : href = href[:ipos]
        if ( href.endswith('/') ) : href = href[:-1]
        if ( len(href) < 1 ) : continue

	# Check if the URL is in any of the webs
        found = False
        for web in webs:
            if ( href.startswith(web) ) :
                found = True
                break
        if not found : continue

        # print('new link', href)
        cur.execute('INSERT OR IGNORE INTO Pages (url, html, new_rank, insert_at) VALUES ( ?, NULL, 1.0, ? )', ( href, time()) )
        count = count + 1
        conn.commit()

        cur.execute('SELECT id FROM Pages WHERE url=? LIMIT 1', ( href, ))
        try:
            row = cur.fetchone()
            toid = row[0]
        except:
            print('Could not retrieve id')
            continue
        # print fromid, toid
        cur.execute('INSERT OR IGNORE INTO Links (from_id, to_id) VALUES ( ?, ? )', ( fromid, toid ) )


    print(count)

cur.close()
