import sqlite3

conn = sqlite3.connect('smoker.sqlite')
cur = conn.cursor()

cur.execute('''SELECT count(*) FROM pages''')
row = cur.fetchone()
total = row[0]

cur.execute('''SELECT Bad.url AS bad_url, Bad.code, Bad.size, Bad.content_type, Fr.url AS from_url
     FROM Pages AS Bad
     JOIN Links ON Bad.id = Links.to_id
     JOIN Pages AS Fr ON Links.from_id = Fr.id
     WHERE Bad.code <> 200''')

count = 0
found = list()
for row in cur :
    url = row[0]
    if url in found : continue
    found.append(url)
    print()
    print(url)
    print("Linked from:")
    print(row[4])
    print(row[1],row[2],row[3])
    count = count + 1

print(total,'pages visited')
print(count, 'pages with error')
cur.close()
