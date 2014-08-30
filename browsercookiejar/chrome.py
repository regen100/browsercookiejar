import os
import sys
import sqlite3
import cookielib

sql = """
SELECT
    host_key, name, path, secure,
    to_epoch(expires_utc) as expires,
    CASE
        WHEN encrypted_value != '' THEN decrypt(encrypted_value)
        ELSE value
    END as value
FROM cookies
"""


def dpapi_decrypt(encrypted):
    import ctypes
    import ctypes.wintypes

    class DATA_BLOB(ctypes.Structure):
        _fields_ = [('cbData', ctypes.wintypes.DWORD),
                    ('pbData', ctypes.POINTER(ctypes.c_char))]

    p = ctypes.create_string_buffer(str(encrypted), len(encrypted))
    blobin = DATA_BLOB(ctypes.sizeof(p), p)
    blobout = DATA_BLOB()
    retval = ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(blobin), None, None, None, None, 0, ctypes.byref(blobout))
    if not retval:
        raise ctypes.WinError()
    result = ctypes.string_at(blobout.pbData, blobout.cbData)
    ctypes.windll.kernel32.LocalFree(blobout.pbData)
    return result


def unix_decrypt(encrypted):
    if sys.platform.startswith('linux'):
        password = 'peanuts'
        iterations = 1
    else:
        raise NotImplemented

    from Crypto.Cipher import AES
    from Crypto.Protocol.KDF import PBKDF2

    salt = 'saltysalt'
    iv = ' ' * 16
    length = 16
    key = PBKDF2(password, salt, length, iterations)
    cipher = AES.new(key, AES.MODE_CBC, IV=iv)
    decrypted = cipher.decrypt(encrypted[3:])
    return decrypted[:-ord(decrypted[-1])]


def chrome_decrypt(encrypted):
    if sys.platform == 'win32':
        try:
            return dpapi_decrypt(encrypted)
        except WindowsError:
            return None
    else:
        try:
            return unix_decrypt(encrypted)
        except NotImplemented:
            return None


def to_epoch(chrome_ts):
    if chrome_ts:
        return chrome_ts - 11644473600 * 1000 * 1000
    else:
        return None


class ChromeCookieJar(cookielib.FileCookieJar):
    def __init__(self, filename=None, delayload=False, policy=None):
        if filename is None:
            if sys.platform == 'win32':
                filename = os.path.join(
                    os.environ['USERPROFILE'],
                    r'AppData\Local\Google\Chrome\User Data\Default\Cookies')
            elif sys.platform.startswith('linux'):
                filename = os.path.expanduser(
                    '~/.config/google-chrome/Default/Cookies')
                if not os.path.exists(filename):
                    filename = os.path.expanduser(
                        '~/.config/chromium/Default/Cookies')
            if not os.path.exists(filename):
                filename = None

        cookielib.FileCookieJar.__init__(self, filename, delayload, policy)

    def _really_load(self, f, filename, ignore_discard, ignore_expires):
        con = sqlite3.connect(filename)
        con.row_factory = sqlite3.Row
        con.create_function('decrypt', 1, chrome_decrypt)
        con.create_function('to_epoch', 1, to_epoch)

        cur = con.cursor()
        cur.execute(sql)
        for row in cur:
            if row['value'] is not None:
                name = row['name']
                value = row['value']
                host = row['host_key']
                path = row['path']
                secure = bool(row['secure'])
                expires = row['expires']

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
    jar = ChromeCookieJar()
    jar.load(sys.argv[1] if len(sys.argv) == 2 else None)
    for c in jar:
        print c
