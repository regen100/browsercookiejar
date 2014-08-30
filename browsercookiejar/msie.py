import os
import glob
import cookielib


def get_cookiedir():
    import _winreg
    path = r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
    with _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, path) as key:
        return _winreg.QueryValueEx(key, 'Cookies')[0]


class MSIECookieJar(cookielib.CookieJar):
    def load(self):
        """Load cookies from a file."""
        self._really_load()

    def revert(self):
        """Clear all cookies and reload cookies from a saved file.

        Raises LoadError (or IOError) if reversion is not successful; the
        object's state will not be altered if this happens.

        """
        self._cookies_lock.acquire()
        try:
            old_state = cookielib.copy.deepcopy(self._cookies)
            self._cookies = {}
            try:
                self.load()
            except (cookielib.LoadError, IOError):
                self._cookies = old_state
                raise

        finally:
            self._cookies_lock.release()

    def _really_load(self):
        pattern = '*.txt'
        dirname = get_cookiedir()
        files = glob.glob(os.path.join(dirname, pattern))
        files += glob.glob(os.path.join(dirname, 'Low', pattern))
        for fname in files:
            with open(fname) as fp:
                for chunk in zip(*[fp] * 9):
                    name = chunk[0][:-1]
                    value = chunk[1][:-1]
                    host, path = chunk[2][:-1].split('/', 1)
                    path = '/' + path
                    flag = int(chunk[3])
                    secure = bool(flag & 1)
                    expires_nt = (long(chunk[5]) << 32) + long(chunk[4])
                    expires = expires_nt / 10000000 - 11644473600

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

if __name__ == '__main__':
    jar = MSIECookieJar()
    jar.load()
    for c in jar:
        print c
