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
        login = "http://localhost:8080/portal/relogin";
        payload = {'eid': 'hirouki', 'pw': 'p', 'submit': 'Log in'}
        # payload = {'eid': 'admin', 'pw': 'admin', 'submit': 'Log in'}
        r = requests.post(login, cookies=cookies, data=payload)
        return cookies

    def ignoreError(self, code, url) :
        if url.find('ILinkListener') > 0 : return True
        if re.search('\?[0-9]+-[0-9]+', url) : return True
        return False
    
    def dontVisit(self, href):
        # Lets keep as much state as we can
        if re.search('/portal/site/[^/]*/tool-reset/', href) : return True
        if re.search('/portal/site/[^/]*/page-reset/', href) : return True

        # Neither log out nor log in
        if '/portal/logout' in href : return True
        if '/portal/login' in href : return True

        # Helpers usually need way too much state to work
        if 'ResourcePicker/tool' in href : return True
        if re.search('/portal/site/[^/]*/tool/[^/]*.PermissionsHelper', href) : return True
        return False

    def adjustCode(self, code, html, url) :
        if re.search('NullPointerException', html) :
            print("\nNullPointerException\n")
            return 450
        elif re.search('HTTP Status 404.*Apache Tomcat', html) :
            return 404
        elif re.search('Apache Tomcat', html) :
            return 454
        elif re.search('To send a bug report, describe what you were doing when the problem occurred, in the space below, and press the submit button.',html) :
            print("\nBug Report\n")
            return 453
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

