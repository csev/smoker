Simple Python Smoke Tester

Pre-requisites

pip3 install < requirements.tx

Running the smoke tester

rm smoker.sqlite
python3 smoker.py
Enter web url or enter: [enter]
setting up sakai
<RequestsCookieJar[<Cookie JSESSIONID=fd74e6f9-9052-4be5-8400-ae913c5ac47c.MacBook-Pro-186.local for localhost.local/>]>
['http://localhost:8080/', 'http://localhost:8080/portal']
How many pages:10
1 http://localhost:8080/portal (79301) 71
2 http://localhost:8080/portal/site/%7Eadmin/page-reset/%7Eadmin-100 (79329) 71
3 http://localhost:8080/portal/site/%7Eadmin/page/%7Eadmin-1120 (81889) 73
4 http://localhost:8080/portal/site/%7Eadmin (81889) 73
5 http://localhost:8080/portal/site/b67e17ab-f6a3-47e3-ac82-eac00bbc7eb7 (73538) 64
6 http://localhost:8080/portal/site/citationsAdmin (103733) 66
7 http://localhost:8080/portal/site/!admin (84451) 78
8 http://localhost:8080/portal/site/mercury (88341) 72
9 http://localhost:8080/portal/site/%7Eadmin/tool-reset/%7Eadmin-365 (110634) 101
10 http://localhost:8080/portal/site/%7Eadmin/tool-reset/%7Eadmin-365?panel=Shortcut&sakai_action=doNew_site& (78360) 72
How many pages:

To view the results

cd app
export FLASK_APP=smoker.py
flash run

Then go to 

http://127.0.0.1:5000/

Press "refresh" as smoker runs to see broken links.


