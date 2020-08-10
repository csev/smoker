Simple Python Smoke Tester
==========================

This is a general purpose smoke tester.  The idea is to spider the application
like it is spidering a web site - retrieving every link, reading the HTML, 
finding every anchor tag and adding those links to a "to retrieve" queue.

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

    python3 smoker.py http://localhost:8080 5 depth
    1 0 http://localhost:8080 (124) 200 1
    2 1 http://localhost:8080/portal (42145) 200 47
    3 2 http://localhost:8080/portal/site/!gateway/page-reset/!gateway-100 (42145) 200 47
    4 2 http://localhost:8080/portal/site/!gateway/page/!gateway-200 (38455) 200 47
    47 3 http://localhost:8080/portal/site/!gateway/page-reset/!gateway-200 (38455) 200 47

It can work with any web tool / web site.  The site can be running locally or
on the Internet:

    python3 smoker.py https://www.tsugicloud.org 5 breadth
    1 0 https://www.tsugicloud.org (13589) 200 22
    2 1 https://www.tsugicloud.org/about/policies/privacy (15633) 200 22
    3 1 https://www.tsugicloud.org/about/policies/data-retention (10035) 200 22
    4 1 https://www.tsugicloud.org/about/policies/service-level-agreement (9994) 200 22
    5 1 https://www.tsugicloud.org/about/documentation/howto (10571) 200 27

The third parameter is how the pages are walked it can be:

* `depth` - go deep down a chain of links and finish a subtree before moving on, depth-first

* `breadth`  - Go across all the "1 deep" links then go the to the "2 deep", breadth-first

* `random` - Pick the "next link" randomly from all the "to be loaded" links

To view the results - even while it is running, use

    python3 broken.py

Add `html` if you want to see the HTML:

    python3 broken.py html

It shows you the URL, where it was linked from, the error code, etc.

Some Fun things to Smoke Test
-----------------------------

Nightly Master 

python3 sakai-smoker.py https://trunk-mysql.nightly.sakaiproject.org 40000 breadth

The 20.x branch

python3 sakai-smoker.py https://qa20-mysql.nightly.sakaiproject.org/ 40000 breadth

The 19.x branch

python3 sakai-smoker.py https://qa19-mysql.nightly.sakaiproject.org/ 40000 breadth

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

