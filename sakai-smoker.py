import os, requests, re

from smoker import Smoker

class SakaiSmoker(Smoker):
    def loginUser(self, web) :
        print("setting up sakai")
        portal = web + "/portal";
        r = requests.get(portal)
        cookies = r.cookies
        print(cookies)
        login = "http://localhost:8080/portal/relogin";
        # payload = {'eid': 'hirouki', 'pw': 'p', 'submit': 'Log in'}
        payload = {'eid': 'admin', 'pw': 'admin', 'submit': 'Log in'}
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
            code = 450
        elif code == 200 and re.search('HTTP Status 404.*Apache Tomcat', html) :
            print("\nHTTP Status 404.*Apache Tomcat\n")
            code = 404
        elif code == 200 and re.search('Apache Tomcat', html) :
            print("\nApache Tomcat\n")
            code = 454

os.unlink('smoker.sqlite')
app = SakaiSmoker('http://localhost:8080', 'smoker.sqlite')
app.run(20000);
