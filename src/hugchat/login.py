import requests
import os
import json
import logging
import re


class Login:
    
    def __init__(self, email: str, passwd: str = "") -> None:
        self.DEFAULT_PATH_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "usercookies")
        self.DEFAULT_COOKIE_PATH = self.DEFAULT_PATH_DIR + os.path.join(f"{email}.json")

        self.email: str = email
        self.passwd: str = passwd
        self.headers = {
            "Referer": "https://huggingface.co/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.64",
        }
        self.cookies = requests.sessions.RequestsCookieJar()

    def login(self) -> requests.sessions.RequestsCookieJar:
        self._sign_in_with_email()
        location = self._get_auth_url()
        if self._grant_auth(location):
            return self.cookies
        else:
            raise Exception(f"Grant auth fatal, please check your email or password\ncookies gained: \n{self.cookies}")
        
    def save_cookies_to_dir(self, cookie_dir_path: str = None) -> str:
        '''
        cookies will be saved into: cookie_dir_path/<email>.json
        '''
        return self.saveCookiesToDir(cookie_dir_path)
        
    def saveCookiesToDir(self, cookie_dir_path: str = None) -> str:
        """
        alias of save_cookies_to_dir
        """
        cookie_dir_path = self.DEFAULT_PATH_DIR if not cookie_dir_path else cookie_dir_path
        if not cookie_dir_path.endswith("/"):
            cookie_dir_path += "/"
        cookie_path = cookie_dir_path + f"{self.email}.json"
        if not os.path.exists(cookie_dir_path):
            logging.info("Cookie directory not exist, creating...")
            os.makedirs(cookie_dir_path)
        logging.info(f"Cookie store path: {cookie_path}")

        with open(cookie_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.cookies.get_dict()))
        return cookie_path
    
    def load_cookies_from_dir(self, cookie_dir_path: str = None) -> requests.sessions.RequestsCookieJar:
        '''
        cookies will be loaded from: cookie_dir_path/<email>.json
        '''
        return self.loadCookiesFromDir(cookie_dir_path)
    
    def loadCookiesFromDir(self, cookie_dir_path: str = None) -> requests.sessions.RequestsCookieJar:
        """
        alias of load_cookies_from_dir
        """
        cookie_dir_path = self.DEFAULT_PATH_DIR if not cookie_dir_path else cookie_dir_path
        cookie_path = self._get_cookie_path(cookie_dir_path)
        if not cookie_path:
            raise Exception(f"Cookie not found. please check the path given: {cookie_dir_path}.\n" +
                            f"Cookie file must be named like this: 'your_email'+'.json': '{self.email}.json'")

        with open(cookie_path, "r", encoding="utf-8") as f:
            try:
                js = json.loads(f.read())
                for i in js.keys():
                    self.cookies.set(i, js[i])
                    logging.info(f"{i} loaded")
                return self.cookies
            except:
                raise Exception("load cookies from files fatal. Please check the format")
    
    def _request_get(self, url: str, params=None, allow_redirects=True) -> requests.Response:
        res = requests.get(
            url,
            params=params,
            headers=self.headers,
            cookies=self.cookies,
            allow_redirects=allow_redirects,
        )
        self._refresh_cookies(res.cookies)
        return res

    def _requests_post(self, url: str, headers=None, params=None, data=None, stream=False,
                     allow_redirects=True) -> requests.Response:
        res = requests.post(
            url,
            stream=stream,
            params=params,
            data=data,
            headers=self.headers if headers is None else headers,
            cookies=self.cookies,
            allow_redirects=allow_redirects
        )
        self._refresh_cookies(res.cookies)
        return res

    def _refresh_cookies(self, cookies: requests.sessions.RequestsCookieJar):
        dic = cookies.get_dict()
        for i in dic:
            self.cookies.set(i, dic[i])

    def _sign_in_with_email(self):
        """
        Login through your email and password.
        PS: I found that it doesn't have any type of encryption till now,
        which could expose your password to the internet.
        """
        url = "https://huggingface.co/login"
        data = {
            "username": self.email,
            "password": self.passwd,
        }
        res = self._request_post(url=url, data=data, allow_redirects=False)
        if res.status_code == 400:
            raise Exception("wrong username or password")

    def _get_auth_url(self):
        url = "https://huggingface.co/chat/login"
        headers = {
            "Referer": "https://huggingface.co/chat/login",
            "User-Agent": self.headers["User-Agent"],
            "Content-Type": "application/x-www-form-urlencoded"
        }
        res = self._request_post(url, headers=headers, allow_redirects=False)
        if res.status_code == 200:
            # location = res.headers.get("Location", None)
            location = res.json()["location"]
            if location:
                return location
            else:
                raise Exception("No authorize url found, please check your email or password.")
        elif res.status_code == 303:
            location = res.headers.get("Location")
            if location:
                return location
            else:
                raise Exception("No authorize url found, please check your email or password.")
        else:
            raise Exception("Something went wrong!")

    def _grant_auth(self, url: str) -> int:
        res = self._request_get(url, allow_redirects=False)
        if res.headers.__contains__("location"):
            location = res.headers["location"]
            res = self._request_get(location, allow_redirects=False)
            if res.cookies.__contains__("hf-chat"):
                return 1
        # raise Exception("grantAuth fatal")
        if res.status_code != 200:
            raise Exception("grant auth fatal!")
        csrf = re.findall('/oauth/authorize.*?name="csrf" value="(.*?)"', res.text)
        if len(csrf) == 0:
            raise Exception("No csrf found!")
        data = {
            "csrf": csrf[0]
        }

        res = self._request_post(url, data=data, allow_redirects=False)
        if res.status_code != 303:
            raise Exception(f"get hf-chat cookies fatal! - {res.status_code}")
        else:
            location = res.headers.get("Location")
        res = self._request_get(location, allow_redirects=False)
        if res.status_code != 302:
            raise Exception(f"get hf-chat cookie fatal! - {res.status_code}")
        else:
            return 1

    def _get_cookie_path(self, cookie_dir_path) -> str:
        if not cookie_dir_path.endswith("/"):
            cookie_dir_path += "/"
        if not os.path.exists(cookie_dir_path):
            return ""
        files = os.listdir(cookie_dir_path)
        for i in files:
            if i == f"{self.email}.json":
                return cookie_dir_path + i
        return ""
