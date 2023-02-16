
from urllib.request import urlopen
from random import randint
from time import sleep
from enum import Enum

import myException as EX
import costants as C
import utils as U
import requests
import json
import re

class TYPE_REQUEST(Enum): 
    
    POST = "POST"
    GET = "GET"

class MyInfoSession():

    def __init__(self): 

        self.MySession = requests.Session()

        self.X_Instagram_AJAX = None
        self.X_IG_WWW_Claim = "0"
        self.X_CSRF_Token = None
        self.LoggedUser = None
        self.Device_ID = None
        self.SessionID = None
        self.IG_DID = None
        self.AppID = None
        self.MID = None

    def checkResponse(self, response): 
        
        typeError = "ok"
        message = "ok"

        if response.status_code != 200 and not (response.headers["content-type"] and "application/json" in response.headers["content-type"].lower()): 
            raise EX.MyInstagramException(str(response.status_code) + ": " + response.reason)

        if response.headers["content-type"] and "application/json" in response.headers["content-type"].lower(): responseJSON = json.loads(response.content)
        
        else: responseJSON = json.loads({"status" : "fail"})

        if not responseJSON.get("status", "ok") == "ok": 

            U.ScriviLog(responseJSON, U.LEVEL.ERROR)

            if responseJSON.get("spam", False): typeError, message = "spam", "Sospected SPAM. It's advisable to retry after 24-48h to avoid permanent block account"
            
            elif responseJSON.get("error_type", False) == "sms_code_validation_code_invalid": typeError, message = "sms_code_invalid", "SMS code is NOT valid"

            elif responseJSON.get("two_factor_required", False): typeError, message = "two_factor_required", "Login failed. Two-Factor login is required"
            
            #elif responseJSON.get("message", False) == "challenge_required": typeError, message = "challange", "Challange is required"

            elif responseJSON.get("error_type", False) == "rate_limit_error": typeError, message = "try_later", "Try later"

            elif responseJSON.get("checkpoint_url", False): typeError, message = "checkpoint", "Checkpoint is required"

            else: raise EX.MyInstagramException("Generic error NOT handled yet")

            U.ScriviLog(message, U.LEVEL.ERROR)

        return response, {"error" : typeError, "message" : message, "data" : responseJSON}

    def makeRequest(self, typeRequests, *url, headers, payloads=None, redirect=True, login_required=True):

        if login_required and not "sessionid" in self.MySession.cookies.get_dict(): raise EX.MyLoginRequiredException(f"User is NOT Logged")

        if not isinstance(typeRequests, TYPE_REQUEST): raise EX.MyTypeException(f"The parameter 'typeRequests' is NOT a TypeRequest object --> {type(typeRequests)}")

        header = C.HEADER
        header.update(headers)

        URL = url[0].value.format(*url[1:])
        
        U.ScriviLog(typeRequests.value + ": " + URL, U.LEVEL.DEBUG)
        '''
        if url[0] in U.CRITICAL_REQUESTS: sleep(60)
        
        else: sleep(randint(5, 10))
        '''
        sleep(randint(5, 10))

        if typeRequests == TYPE_REQUEST.GET: Response = self.MySession.get(URL, headers=header, allow_redirects=redirect)
        
        elif typeRequests == TYPE_REQUEST.POST: Response = self.MySession.post(URL, headers=header, data=payloads, allow_redirects=redirect)
        
        else: raise EX.MyTypeException(f"Request Type {typeRequests} is NOT valid")

        return self.checkResponse(Response)

    def initializeData(self):

        Response, ResponseJSON = self.makeRequest(TYPE_REQUEST.GET, *[U.LOGIN_URL.SHARED_DATA_URL], headers={}, login_required=False)

        self.X_CSRF_Token = ResponseJSON["data"]["config"]["csrf_token"]
        self.X_Instagram_AJAX = ResponseJSON["data"]["rollout_hash"]
        self.Device_ID = ResponseJSON["data"]["device_id"]
        
        # I seguenti 2 campi vengono caricati in sessione dall'istruzione set-cookie della chiamata a SHARED_DATA_API_URL
        self.IG_DID = self.MySession.cookies.get_dict()["ig_did"]
        self.MID = self.MySession.cookies.get_dict()["mid"]

        with urlopen("https://www.instagram.com") as response: body = response.read()

        match = re.search('"appID"\\s*:\\s*\\d*', body.decode(response.headers.get_content_charset()))

        if match: self.AppID = match.group().split(":")[1].strip()
        
        else: raise EX.MyInstagramException("Impossibile trovare l'App ID")

    def addCookies(self, cookies):

        for key, value in cookies.items(): self.MySession.cookies.set_cookie(requests.cookies.create_cookie(domain=".instagram.com", name=key, value=value))
