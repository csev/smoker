# https://stackoverflow.com/a/12523416/1994792

fn = 'apache-tomcat-8.0.30/logs/catalina.out'
f = open(fn)
p = 0
while True:
    f.seek(p)
    latest_data = f.read()
    p = f.tell()
    if latest_data:
        print latest_data
