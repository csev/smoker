import sqlite3
import sys

if len(sys.argv) < 3 : 
    print("Two databases parameters needed")
    print()
    print("python3 delta.py smoker.sqlite previous.sqlite");
    quit()

conn = sqlite3.connect(sys.argv[1])
cur = conn.cursor()

query = '''SELECT Bad.url AS bad_url, Bad.code, Bad.size, Bad.content_type, Fr.url AS from_url
     FROM Pages AS Bad
     JOIN Links ON Bad.id = Links.to_id
     JOIN Pages AS Fr ON Links.from_id = Fr.id
     WHERE Bad.code <> 200'''

cur.execute(query)
rows = cur.fetchall()
cur.close()
conn.close()

new_errors = dict()
for row in rows:
    url = row[0]
    new_errors[url] = row[1:]

print("Errors "+sys.argv[1]+"="+str(len(new_errors)))

conn = sqlite3.connect(sys.argv[2])
cur = conn.cursor()

query = '''SELECT Bad.url AS bad_url, Bad.code, Bad.size, Bad.content_type, Fr.url AS from_url
     FROM Pages AS Bad
     JOIN Links ON Bad.id = Links.to_id
     JOIN Pages AS Fr ON Links.from_id = Fr.id
     WHERE Bad.code <> 200'''

cur.execute(query)
rows = cur.fetchall()
cur.close()
conn.close()

old_errors = dict()
for row in rows:
    url = row[0]
    old_errors[url] = row[1:]


print("Errors "+sys.argv[2]+"="+str(len(old_errors)))

delta = dict()
for url, row in new_errors.items():
    new_code = row[0]
    new_size = row[1]
    new_content_type = row[2]
    new_from = row[3]
    old_row = old_errors.get(url, None)
    old_code = -1
    if old_row == None :
        print(url, 9999, new_code)
        delta[url] = (url, old_code, new_code)
        continue

    old_code = old_row[0]
    if new_code != old_code :
        print(url, old_code, new_code)
        delta[url] = (url, old_code, new_code)

print('New errors',len(delta))

