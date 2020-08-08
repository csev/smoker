
import sqlite3
from app import app



@app.route('/')
@app.route('/index')
def index():
    conn = sqlite3.connect('../smoker.sqlite')
    cur = conn.cursor()

    cur.execute('''SELECT count(id) FROM Pages WHERE code IS NOT NULL''');

    row = cur.fetchone();
    retval = '<p>Pages retrieved: '+str(row[0])+'</p>\n'

    cur.execute('''SELECT Bad.url AS bad_url, Bad.size, Bad.code, Bad.content_type, Fr.url AS from_url
        FROM Pages AS Bad
        JOIN Links ON Bad.id = Links.to_id
        JOIN Pages AS Fr ON Links.from_id = Fr.id
        WHERE Bad.code <> 200''')

    count = 0
    urls = list()
    retval = retval + '<ul>\n'
    for row in cur :
        if count < 50 and row[0] not in urls :
            retval = retval + '<li>'
            retval = retval + 'Bad Url: <a href="' + row[0] + '" target="_blank">Broken url</a>\n';
            retval = retval + ' / <a href="' + row[4] + '" target="_blank">Calling URL</a><br/>\n';
            retval = retval + row[0] + '<br/>\n';
            retval = retval + 'Code=' + str(row[2]) + ' Bytes=' + str(row[1]) + ' Type=' + row[3] + '<br/>\n';
            retval = retval + '</li>\n'
            urls.append(row[0])
            count = count + 1

    retval = retval + '</ul>\n'

    if count == 0 : retval = "No errors found."
    cur.close()
    conn.close()

    return retval
