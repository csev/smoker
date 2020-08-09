import sqlite3

conn = sqlite3.connect('smoker.sqlite')
cur = conn.cursor()

cur.execute('''SELECT Bad.url AS bad_url, Bad.size, Bad.code, Bad.content_type, Fr.url AS from_url
     FROM Pages AS Bad
     JOIN Links ON Bad.id = Links.to_id
     JOIN Pages AS Fr ON Links.from_id = Fr.id
     WHERE Bad.code <> 200''')

count = 0
for row in cur :
    if count < 50 : print(row)
    count = count + 1
print(count, 'rows.')
cur.close()
