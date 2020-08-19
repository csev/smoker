import os, requests, sys
import re

from smoker import Smoker

class TsugiSmoker(Smoker):
    def loginUser(self, web) :
        print("setting up tsugi")
        admin = web
        if 'tsugi' not in admin: admin = admin + '/tsugi'
        print(admin)
        r = requests.get(admin)
        cookies = r.cookies
        print(cookies)
        admin = admin + "/admin/";
        payload = {'passphrase': 'short'}
        r = requests.post(admin, cookies=cookies, data=payload)
        return cookies

    def extraStartingPoints(self, web) :
        retval = list()
        if 'tsugi' not in web: 
            web = web + '/tsugi'
            retval.append(web)
        web = web + '/admin'
        retval.append(web)
        return retval

    def dontVisit(self, href):
        # Neither log out nor log in
        if 'logout' in href : return True
        if 'login' in href : return True
        return False

    # Mostly look for errors in the body that are not in the status code
    def adjustCode(self, code, html, url) :

        # if '/tsugi/admin' in url : 
            # print(html)

        retval = re.search('<b>Parse error</b>:.*on line', html)
        if retval:
            print('\n\n')
            print(retval.group(0));
            return 450

        retval = re.search('<b>Notice</b>:.* in .* on line', html)
        if retval:
            print('\n\n')
            print(retval.group(0));
            return 450

        return code

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print()
        print("Example usage: python3 tsugi-smoker.py http://localhost:8888/tsugi 20000 depth")
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

    app = TsugiSmoker(base, 'smoker.sqlite', walk)
    app.run(many);

