import os
import sys
import glob
import cookielib
try:
    import pysqlite2.dbapi2 as sqlite3
except ImportError:
    import sqlite3

sql = """
SELECT host, name, value, path, expiry, isSecure
FROM moz_cookies
"""


class FirefoxCookieJar(cookielib.FileCookieJar):
    def __init__(self, filename=None, delayload=False, policy=None):
        if filename is None:
            if sys.platform == 'win32':
                profiledir = os.path.join(
                    os.environ['USERPROFILE'],
                    r'AppData\Roaming\Mozilla\Firefox\Profiles')
            elif sys.platform.startswith('linux'):
                profiledir = os.path.expanduser('~/.mozilla/firefox')
            else:
                profiledir = ''
            profiles = glob.glob(os.path.join(profiledir, '*.default'))
            if len(profiles) == 1:
                filename = os.path.join(profiles[0], 'cookies.sqlite')
                if not os.path.exists(filename):
                    filename = None

        cookielib.FileCookieJar.__init__(self, filename, delayload, policy)

    def _really_load(self, f, filename, ignore_discard, ignore_expires):
        con = sqlite3.connect(filename)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        try:
            cur.execute(sql)
        except sqlite3.DatabaseError:
            raise ValueError(
                'SQLite v{} is old (>=3.7 needed).'.format(
                    sqlite3.sqlite_version))
        for row in cur:
            name = row['name']
            value = row['value']
            host = row['host']
            path = row['path']
            secure = bool(row['isSecure'])
            expires = row['expiry']

            c = cookielib.Cookie(
                0, name, value,
                None, False,
                host, bool(host), host.startswith('.'),
                path, bool(path),
                secure,
                expires,
                False,
                None,
                None,
                {})
            self.set_cookie(c)
        cur.close()

if __name__ == '__main__':
    jar = FirefoxCookieJar()
    jar.load(sys.argv[1] if len(sys.argv) == 2 else None)
    for c in jar:
        print c
