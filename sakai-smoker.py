import os, requests, sys
import re

from smoker import Smoker

class SakaiSmoker(Smoker):
    def loginUser(self, web) :
        print("setting up sakai")
        portal = web + "/portal";
        r = requests.get(portal)
        cookies = r.cookies
        print(cookies)
        login = web + "/portal/relogin";
        # payload = {'eid': 'hirouki', 'pw': 'p', 'submit': 'Log in'}
        payload = {'eid': 'admin', 'pw': 'admin', 'submit': 'Log in'}
        r = requests.post(login, cookies=cookies, data=payload)
        return cookies

    def ignoreError(self, code, url) :
        # Two common non-idempotent Wicket urls
        # if url.find('ILinkListener') > 0 : return True
        # if re.search('\?[0-9]+-[0-9]+', url) : return True

        # For some reason this tool cannot find these even though a browser can find them
        # if re.search('/wicket/resource/', url) : return True
        return False
    
    def dontVisit(self, href):
        # Lets keep as much state as we can
        if re.search('/portal/site/[^/]*/tool-reset/', href) : return True
        if re.search('/portal/site/[^/]*/page-reset/', href) : return True

        # Neither log out nor log in
        if '/portal/logout' in href : return True
        if '/portal/login' in href : return True

        # Broken things in the admin site
        # http://localhost:8080/portal/site/!admin/tool/!admin-1225/reports?wicket-crypt=r4pLSgXJxv1IAKem2rtXshW-...
        if '/reports?wicket-crypt' in href: return True
        # http://localhost:8080/portal/site/!admin/tool/!admin-1225/admin?wicket-crypt=sNyijE1gL-pZUHNEl
        if '/admin?wicket-crypt' in href: return True

        # Helpers usually need to run in a precise sequence for state
        if 'ResourcePicker/tool' in href : return True
        if re.search('/portal/site/[^/]*/tool/[^/]*.PermissionsHelper', href) : return True
        return False

    # Mostly look for errors in the body that are not in the status code
    def adjustCode(self, code, html, url) :
        if re.search('NullPointerException', html) :
            print("\n\nNullPointerException\n")
            return 450
        elif re.search('HTTP Status 404.*Apache Tomcat', html) :
            return 404
        elif re.search('Apache Tomcat', html) :
            return 454
        elif re.search('To send a bug report, describe what you were doing when the problem occurred, in the space below, and press the submit button.',html) :
            print("\n\nBug Report\n")
            return 453
        # Like if a velocity template goes bad
        elif re.search('<!-- Buffered Body Tool Content -->\s*<!-- End Buffered Body Tool Content -->', html) :
            print("\n\nBlank tool content\n")
            return 455
        return code

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print()
        print("Example usage: python3 sakai-smoker.py http://localhost:8080 20000 depth")
        print()

    base = 'http://localhost:8080'
    many = 20000
    walk = 'depth'  # or breadth or random

    if len(sys.argv) > 1:
        base = sys.argv[1]

    if len(sys.argv) > 2:
        many = int(sys.argv[2])

    if len(sys.argv) > 3:
        walk = sys.argv[3]

    try:
        os.remove('smoker.sqlite')
    except OSError:
        pass

    app = SakaiSmoker(base, 'smoker.sqlite', walk)
    app.run(many);

""" 
root@smoker:/var/www/html# cat aa_readme.txt
Smoker Test Server
------------------

This runs the smoker test on several Sakai servers each night.

https://github.com/csev/smoker

This page shows the results of each run and keeps results of the previous two runs.
It also calcualtes any changes between the previous run and the most recent run (deltas).

For example, here are the files:

    nightly-mysql-0-delta.txt   Errors in the most recent run that were not in the previous run
    nightly-mysql-0-latest.txt	Errors in the most recent run
    nightly-mysql-0-log.txt	Log of the most recent run
    nightly-mysql-1-prev.txt	Errors from the previous run (usually 24 hours earlier)
    nightly-mysql-2-prev.txt	Errors from the run before that (usually 48 hours earlier)

For each entry it looks like:

https://trunk-mysql.nightly.sakaiproject.org/portal/help/TOCDisplay/content.hlp?docId=
Linked from:
https://trunk-mysql.nightly.sakaiproject.org/portal/help/TOCDisplay/content.hlp?docId=accessibilityinformation
454 1123 text/html;charset=ISO-8859-1

This shows that the first link returned 1123 characters and got a "454" error.  The second
link is the page where we found the "broken link".

To reproduce, go the server and login as "admin" and visit the second (source) link.  Find the
reference to the first link (often in the source) and click on it.

Special Error Codes
-------------------

Some of the errors lik 404 and 500 mean what they normally mean - but smoker does some analysis of the text page
looking for sakai specific errors.

404 - Not Found
500 - Server error

450 - NullPointerException
453 - The string "To send a bug report,..." was found on the page
454 - The string "Apache Tomcat" was found somewhere in the page
455 - The string "Blank tool content" was found - usually this is a velocity error

You can see the extra page processing at:

https://github.com/csev/smoker/blob/master/sakai-smoker.py#L49

-----

Questions welcome.

/Chuck

root@smoker:/var/www/html#
"""
