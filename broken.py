import sqlite3
import sys

conn = sqlite3.connect('smoker.sqlite')
cur = conn.cursor()

cur.execute('''SELECT count(*) FROM pages''')
row = cur.fetchone()
total = row[0]

cur.execute('''SELECT Bad.url AS bad_url, Bad.code, Bad.size, Bad.content_type, Fr.url AS from_url, Bad.html
     FROM Pages AS Bad
     JOIN Links ON Bad.id = Links.to_id
     JOIN Pages AS Fr ON Links.from_id = Fr.id
     WHERE Bad.code <> 200''')

print(total,'pages visited')
rows = cur.fetchall()
if not rows : 
    print('No errors')
    quit()

count = 0
found = list()
for row in rows :
    url = row[0]
    if url in found : continue
    found.append(url)
    print('=============================')
    print(url)
    print("Linked from:")
    print(row[4])
    print(row[1],row[2],row[3])
    if len(sys.argv) > 1 : print(row[5])
    count = count + 1

print(count, 'pages with error')
cur.close()
