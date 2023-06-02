import requests
import os
import json
import logging
import re


class Login:
    def __init__(self, email: str, passwd: str) -> None:
        self.COOKIE_DIR = os.path.dirname(os.path.abspath(__file__)) + "/usercookies"
        self.COOKIE_PATH = self.COOKIE_DIR + f"/{email}.json"
        if not os.path.exists(self.COOKIE_DIR):
            logging.debug("Cookie directory not found, creating...")
            os.makedirs(self.COOKIE_DIR)
        logging.debug(f"Cookie store path: {self.COOKIE_DIR}")

        self.email: str = email
        self.passwd: str = passwd
        self.headers = {
            "Referer": "https://huggingface.co/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.64",
        }
        self.cookies = requests.sessions.RequestsCookieJar()
        
    def requestsGet(self, url:str, params=None, allow_redirects=True) -> requests.Response:
        res = requests.get(
            url,
            params=params, 
            headers=self.headers, 
            cookies=self.cookies, 
            allow_redirects=allow_redirects,
            )
        self.refreshCookies(res.cookies)
        return res
    
    def requestsPost(self, url:str, headers=None, params=None, data=None, stream=False, allow_redirects=True) -> requests.Response:
        res = requests.post(
            url,
            stream=stream, 
            params=params, 
            data=data, 
            headers=self.headers if headers == None else headers, 
            cookies=self.cookies, 
            allow_redirects=allow_redirects
            )
        self.refreshCookies(res.cookies)
        return res
                
    def refreshCookies(self, cookies:requests.sessions.RequestsCookieJar):
        dic = cookies.get_dict()
        for i in dic:
            self.cookies.set(i, dic[i])

    def SigninWithEmail(self):
        """
        Login through your email and password.
        PS: I found that it doesn't have any type of encrytion till now,
        which could expose your password to the internet.
        """
        url = "https://huggingface.co/login"
        data = {
            "username": self.email,
            "password": self.passwd,
        }
        res = self.requestsPost(url=url, data=data, allow_redirects=False)
        if res.status_code == 400:
            raise Exception("wrong username or password")

    def getAuthURL(self):
        url = "https://huggingface.co/chat/login"
        headers = {
            "Referer": "https://huggingface.co/chat/login",
            "User-Agent": self.headers["User-Agent"],
            "Content-Type": "application/x-www-form-urlencoded"
        }
        res = self.requestsPost(url, headers=headers, allow_redirects=False)
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
    
    def grantAuth(self, url: str) -> int:
        """
        Grant auth to huggingchat after login process is done.
        """
        res = self.requestsGet(url)
        if res.status_code != 200:
            raise Exception("Grant auth fatal!")
        csrf = re.findall('/oauth/authorize.*?name="csrf" value="(.*?)"', res.text)
        if len(csrf) == 0:
            raise Exception("No csrf found!")
        data = {
            "csrf":csrf[0]
        }

        res = self.requestsPost(url, data=data, allow_redirects=False)
        if res.status_code != 303:
            raise Exception(f"get hf-chat cookies fatal! - {res.status_code}")
        else:
            location = res.headers.get("Location")
        res = self.requestsGet(location, allow_redirects=False)
        if res.status_code != 302:
            raise Exception(f"get hf-chat cookie fatal! - {res.status_code}")
        else:
            return 1
    
    def login(self) -> requests.sessions.RequestsCookieJar:
        self.SigninWithEmail()
        location = self.getAuthURL()
        if self.grantAuth(location):
            return self.cookies
        else:
            raise Exception(f"Grant auth fatal, please check your email or password\ncookies gained: \n{self.cookies}")
    
    def saveCookies(self) -> str:
        with open(self.COOKIE_PATH, "w", encoding="utf-8")  as f:
            f.write(json.dumps(self.cookies.get_dict(), ensure_ascii=False))
        return self.COOKIE_PATH

    def loadCookies(self) -> requests.sessions.RequestsCookieJar:
        if os.path.exists(self.COOKIE_PATH):
            with open(self.COOKIE_PATH, "r", encoding="utf-8") as f:
                try:
                    js:dict = json.loads(f.read())
                    for i in js.keys():
                        self.cookies.set(i, js[i])
                        logging.debug(f"{i} loaded")
                    return self.cookies
                except:
                    raise Exception("Load cookies from json file fatal. Error while parsing json file")
        else:
            raise Exception(f"{self.COOKIE_PATH} doesn't seem to exist")
