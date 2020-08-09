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

If you don't enter a base url, it assumes Sakai on port 8080

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

Press "refresh" as `smoker.py` runs to see broken links.

Important Notes
---------------

Some of the errors are due to the fact that this tool does two things obsessively that
users seldom if ever do.  In effect it reads a page and book marks every URL on the page
and then makes a note and comes back to every URL.  Sometimes URLs have state in them
(looking at Wicket) and sometimes the session needs some data for URL to work (looking
at Assignments) and sometimes the "Back" button is contraindicated :)  Anyhing that uses 
a helper tool like the Resourse picker will happen out of order.

These "out of order clicks" show up as 404's or log tracebacks often - they are not a
bug per se.  It would be nice to find a way to do things in the right order - but that
is difficult to do without apriori scripts being written.

TODO
----

It would be nice to mark certain urls as "not to worry" in the flask app and have it so 
repeated smoker runs don't flag something that is known wonky over and over we we can 
see real, new problems.

It would be nice to run it and then run it again and call out anything that changed.  
(regressions or bug fixes).

I wold like to fix a few of the tracebacks that don't seem to harm functionality but
theu clog up the logs a bit :)

