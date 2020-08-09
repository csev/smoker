Simple Python Smoke Tester
==========================

This is a general purpose smoke tester.  There are some special 
things it does for Sakai that will be eventually factored out into plug ins.

The idea is to spider the application like it is a web site - retrieving every file,
prettying every anchor tag and finding new links and following those links.

In its current form it can be used to smoke test things like

https://www.tsugicloud.org/

It is most fun if you point it at a Sakai running on localhost:8080 - it will log
in as admin and proceed to beat the Sakai up pretty hard :)

Pre-requisites
--------------

pip3 install < requirements.txt

Running the smoke tester
------------------------

If you don't enter a base url, ir assumed Sakai on port 8080

rm smoker.sqlite
python3 smoker.py 
Enter web url or enter: 
setting up sakai
<RequestsCookieJar[<Cookie JSESSIONID=e1d7d538-9c75-4e8b-8c9f-5e76e698fb81.MacBook-Pro-186.local for localhost.local/>]>
['http://localhost:8080']
How many pages:5
1 http://localhost:8080 (124) 200 1
2 http://localhost:8080/portal (79301) 200 71
3 http://localhost:8080/portal/site/%7Eadmin/page-reset/%7Eadmin-100 (79329) 200 71
4 http://localhost:8080/portal/site/%7Eadmin/page/%7Eadmin-1120 (81891) 200 73
5 http://localhost:8080/portal/site/%7Eadmin (81891) 200 73
How many pages: 100000


It is restartable and if aborted or finished it will pick up where it leaves off.  To 
completely rtestart the crawl `rm smoker.sqlite` and run `smoker.py` again.

It can work with any web tool / web site.  The site can be running locally or
on the Internet:

rm smoker.sqlite
python3 smoker.py 
Enter web url or enter: https://www.tsugicloud.org/
['https://www.tsugicloud.org']
How many pages:1000
1 https://www.tsugicloud.org (13589) 200 22
2 https://www.tsugicloud.org/about/policies/privacy (15633) 200 22
3 https://www.tsugicloud.org/about/policies/data-retention (10035) 200 22
..
68 https://www.tsugicloud.org/mod/iframe/register.json Note non text/html page
69 https://www.tsugicloud.org/mod/gift/canvas-config.xml Note non text/html page
70 https://www.tsugicloud.org/mod/gift/register.json Note non text/html page
No unretrieved HTML pages found

To view the results - even while it is running, use

python3 broken.py

It shows you the URL, where it was linked from, the error code, etc.

Viewing in a Browser
--------------------

Also you can see the errors and click on them in a browser using a simple
Flask application:

cd app
export FLASK_APP=smoker.py
flash run

Then go to 

http://127.0.0.1:5000/

Press "refresh" as smoker runs to see broken links.


