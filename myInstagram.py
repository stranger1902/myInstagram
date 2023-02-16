from ENDPOINTS import friendship_endpoint, user_endpoint, feed_endpoint
from datetime import datetime

import myInfoSession as S
import myException as EX
import myDatabase as DB
import costants as C
import utils as U
import requests
import json

class MyInstagram:

    def __init__(self): 

        self.MyDB = DB.MyDatabase(C.DATABASE_FILENAME)
        self.MyDB.connectDB()
        
        self.sessionContext = S.MyInfoSession()

    def LoginByCookies(self, username):
 
        ResultQuery = self.MyDB.executeQuery(DB.QUERY_DB.SELECT_LAST_AVAILABLE_SESSION, (username, username, username)).fetchall()

        if len(ResultQuery) == 0: 
            U.ScriviLog(f"Attempt to login by cookies failed - No sessions available. It will make a new login", U.LEVEL.INFO)
            return False

        if len(ResultQuery) > 1: raise EX.MyLoginException("Anomalia sui dati. Troppe sessioni precedenti disponibili da disconnettere")

        sessionData = json.loads(ResultQuery[0]["COOKIES"])
        prgSession = ResultQuery[0]["NEW_PRG"] 

        self.sessionContext.addCookies(json.loads(json.dumps(sessionData["cookies"])))

        self.sessionContext.X_Instagram_AJAX = sessionData["session"]["x_instagram_ajax"]
        self.sessionContext.X_IG_WWW_Claim = sessionData["session"]["x_ig_www_claim"]
        self.sessionContext.X_CSRF_Token = sessionData["session"]["csrf_token"]
        self.sessionContext.SessionID = sessionData["session"]["session_id"]
        self.sessionContext.Device_ID = sessionData["session"]["device_id"]
        self.sessionContext.AppID = sessionData["session"]["x_asbd_id"]
        self.sessionContext.IG_DID = sessionData["session"]["ig_did"]
        self.sessionContext.MID = sessionData["session"]["mid"]

        try: self.sessionContext.LoggedUser = self.callAPI(U.API_ENDPOINTS.GET_USER_BY_USERNAME, username=sessionData["user"]["username"])

        except EX.MyLoginRequiredException as err:
            U.ScriviLog("Attempt to login by cookies failed - Stored session is NOT available anymore. It will make a new login", U.LEVEL.INFO)
            self.MyDB.executeQuery(DB.QUERY_DB.UPDATE_LOGOUT_SESSION, (datetime.today(), self.sessionContext.SessionID), True)
            self.sessionContext = S.MyInfoSession()
            return False

        U.ScriviLog(f"Login SUCCESSFUL as '{self.sessionContext.LoggedUser['username']}' by cookies", U.LEVEL.INFO)

        return True
    
    def sendVerificationCode(self, username, identifier, verification_code, verification_method):

        header = {"referer" : "https://www.instagram.com/accounts/login/two_factor?next=/",
                  "X-Instagram-AJAX" : self.sessionContext.X_Instagram_AJAX,
                  "X-IG-WWW-Claim" : self.sessionContext.X_IG_WWW_Claim,
                  "X-CSRFToken" : self.sessionContext.X_CSRF_Token,
                  "X-ASBD-ID" : self.sessionContext.AppID,
                  "DNT" : 1
                  }

        payload = {"verification_method" : verification_method,
                   "verificationCode" : verification_code,
                   "queryParams" : '{"next" : "/"}',
                   "identifier" : identifier,
                   "trust_signal" : "true",         # True per salvare il dispositivo tra i trusted device e non richiedere più il codice di sicurezza per tale dispositivo
                   "username" : username              
                   }

        return self.sessionContext.makeRequest(S.TYPE_REQUEST.POST, *[U.LOGIN_URL.LOGIN_TWO_FACTOR_URL], headers=header, payloads=payload, login_required=False)
        
    def TwoFactorLogin(self, responseJSON, username):

        resendSmsDelay = responseJSON["data"]["phone_verification_settings"]["resend_sms_delay_sec"]
        twoFactorIdentifier = responseJSON["data"]["two_factor_info"]["two_factor_identifier"]
        maxSmsRetry = responseJSON["data"]["phone_verification_settings"]["max_sms_count"]

        OtpMode = (responseJSON["data"]["two_factor_info"]["totp_two_factor_on"], "App di autenticazione (es. DuoMobile)", 3)
        WhatsAppMode = (responseJSON["data"]["two_factor_info"]["whatsapp_two_factor_on"], "Whatsapp", 999)                        #TODO: scoprire il codice della modalità da inserire nel payload
        SmsMode = (responseJSON["data"]["two_factor_info"]["sms_two_factor_on"], "SMS", 1)
        RecoveryMode = (True, "Codice di Recupero", 2)

        ModesOn = []

        if WhatsAppMode[0]: ModesOn.append(WhatsAppMode)
        if RecoveryMode[0]: ModesOn.append(RecoveryMode)
        if SmsMode[0]: ModesOn.append(SmsMode)
        if OtpMode[0]: ModesOn.append(OtpMode)

        U.ScriviLog("Two-Factor Authentication Mode available:", U.LEVEL.INFO)

        for index, mode in enumerate(ModesOn): U.ScriviLog("\t" + str(index + 1) + ": " + mode[1], U.LEVEL.INFO)

        inputText = U.myInput("Choose one of Two-Factor Authentication Mode available: ")

        while not ( len(inputText) == 1 and ord(inputText) >= ord("1") and ord(inputText) <= ord(str(len(ModesOn))) ):
            inputText = U.myInput("Input is NOT valid. Choose one of Two-Factor Authentication Mode available: ")
            
        modeTwoFactor = ModesOn[int(inputText) - 1][2]

        for count in range(0, C.MAX_RETRY_TWO_FACTOR_LOGIN):

            if modeTwoFactor == 1: inputText = U.myInput(f"Inserisci ('exit' to quit - 'new' to send another verification code) il codice di sicurezza (tentativi {count + 1} di {C.MAX_RETRY_TWO_FACTOR_LOGIN}): ")
            
            elif modeTwoFactor == 3: inputText = U.myInput(f"Inserisci ('exit' to quit) il codice di sicurezza restituito dall'app di autenticazione a 2 fattori configurata (es. DuoMobile) (tentativi {count + 1} di {C.MAX_RETRY_TWO_FACTOR_LOGIN}): ")

            #TODO: scoprire il codice della modalità da inserire nel payload
            elif modeTwoFactor == 999: inputText = U.myInput(f"Inserisci ('exit' to quit) il codice di sicurezza restituito da Whatsapp (tentativi {count + 1} di {C.MAX_RETRY_TWO_FACTOR_LOGIN}): ")
            
            else: inputText = U.myInput(f"Inserisci ('exit' to quit) uno tra i codici di recupero ad 8 cifre disponibili (tentativi {count + 1} di {C.MAX_RETRY_TWO_FACTOR_LOGIN}): ")

            if inputText == "EXIT": raise EX.MyLoginException("Login failed 1")

            while modeTwoFactor == 1 and maxSmsRetry > 0 and inputText == "NEW": 
                
                if inputText == "EXIT": raise EX.MyLoginException("Login Failed 2")
                
                maxSmsRetry -= 1

                header = {"referer" : "https://www.instagram.com/accounts/login/two_factor?next=/",
                          "X-Instagram-AJAX" : self.sessionContext.X_Instagram_AJAX,
                          "X-IG-WWW-Claim" : self.sessionContext.X_IG_WWW_Claim,
                          "X-CSRFToken" : self.sessionContext.X_CSRF_Token,
                          "X-ASBD-ID" : self.sessionContext.AppID,
                          "DNT" : 1
                          }

                payload = {"identifier" : twoFactorIdentifier,
                           "username" : username
                           }
                
                ResponseTwoFactorSms, ResponseTwoFactorSmsJSON = self.sessionContext.makeRequest(S.TYPE_REQUEST.POST, *[U.LOGIN_URL.SMS_TWO_FACTOR_URL], headers=header, payloads=payload, login_required=False)

                if not ResponseTwoFactorSmsJSON["error"] == "try_later": twoFactorIdentifier = ResponseTwoFactorSmsJSON["data"]["two_factor_info"]["two_factor_identifier"]

                inputText = U.myInput(f"Inserisci il codice di sicurezza ('exit' to quit - 'new' to send another verification code) (tentativi {count + 1} di {C.MAX_RETRY_TWO_FACTOR_LOGIN}): ")

            ResponseTwoFactorLogin, ResponseTwoFactorLoginJSON = self.sendVerificationCode(username, twoFactorIdentifier, inputText.replace(" ", ""), modeTwoFactor)
            
            #TODO: fare un giro di prova inserendo un codice errato
            if ResponseTwoFactorLoginJSON["error"] == "sms_code_invalid": continue

            else: return ResponseTwoFactorLogin, ResponseTwoFactorLoginJSON

        recoveryMode = U.myInput("Do you have a recovery code? S/N: ")

        while recoveryMode not in ["N", "S"]: recoveryMode = U.myInput("Input is NOT valid. Do you have a recovery code? S/N: ")

        if recoveryMode == "S":

            inputText = U.myInput(f"Inserisci uno tra i codici di recupero ad 8 cifre disponibili ('exit' to quit): ")

            if inputText == "EXIT": raise EX.MyLoginException("Login Failed 3")
    
            ResponseTwoFactorLogin, ResponseTwoFactorLoginJSON = self.sendVerificationCode(username, twoFactorIdentifier, inputText.replace(" ", ""), "2")

            #TODO: fare un giro di prova inserendo un codice errato
            if ResponseTwoFactorLoginJSON["error"] == "sms_code_invalid": raise EX.MyLoginException("Too many attemps done. Try later (maybe after 12-24h) to avoid account will be blocked")
            
            else: return ResponseTwoFactorLogin, ResponseTwoFactorLoginJSON

    def checkpointRequired(self, responseJSON):

        flowRenderType = responseJSON["data"]["flow_render_type"]
        checkpointURL = responseJSON["data"]["checkpoint_url"]

        ModesOn = [("via e-mail", 1), ("via SMS", 0)]   #TODO: qual è il codice via email???

        U.ScriviLog("Modalità di invio codice di sicurezza disponibili:", U.LEVEL.INFO)

        for index, mode in enumerate(ModesOn): U.ScriviLog("\t" + str(index + 1) + ": " + mode[0], U.LEVEL.INFO)

        inputText = U.myInput("Scegli una modalità di invio codice di sicurezza tra quelle disponibili:")

        while not ( len(inputText) == 1 and ord(inputText) >= ord("1") and ord(inputText) <= ord(str(len(ModesOn))) ):
            inputText = U.myInput("Valore inserito NON valido. Scegli una modalità di invio codice di sicurezza tra quelle disponibili: ")

        modeVerification = ModesOn[int(inputText) - 1][1]
        
        header = {"X-Instagram-AJAX" : self.sessionContext.X_Instagram_AJAX,
                  "referer" : "https://www.instagram.com/" + checkpointURL,
                  "X-IG-WWW-Claim" : self.sessionContext.X_IG_WWW_Claim,
                  "X-CSRFToken" : self.sessionContext.X_CSRF_Token,
                  "X-ASBD-ID" : self.sessionContext.AppID,
                  }

        payload = {"choice" : modeVerification}

        ResponseChallenge, ResponseChallengeJSON = self.sessionContext.makeRequest(S.TYPE_REQUEST.POST, *[U.LOGIN_URL.CHALLENGE_ACTION_URL, checkpointURL], headers=header, payloads=payload, login_required=False)

        challenge_context = ResponseChallengeJSON["data"]["challenge_context"]
        challenge_type = ResponseChallengeJSON["data"]["challenge_type"]

        #TODO: gestire caso new + gestire inserimenti multipli per maxRetry volte 
        inputText = U.myInput(f"Inserisci il codice di sicurezza ('exit' per uscire): ")

        if inputText == "EXIT": raise EX.MyLoginException("Challenge Failed 1")


        #TODO: implementare richiesta nuovo codice di verifica...


        payload = {"security_code" : inputText.replace(" ", "")}

        ResponseChallenge, ResponseChallengeJSON = self.sessionContext.makeRequest(S.TYPE_REQUEST.POST, *[U.LOGIN_URL.CHALLENGE_ACTION_URL, checkpointURL], headers=header, payloads=payload, login_required=False)

        U.ScriviLog(ResponseChallengeJSON, U.LEVEL.INFO)

        return ResponseChallenge, ResponseChallengeJSON

    def Login(self, username, password, useCookies=True):
        
        if not isinstance(useCookies, bool): raise EX.MyTypeException(f"The parameter 'useCookies' is NOT a Boolean --> {type(useCookies)}")
        
        if useCookies and self.LoginByCookies(username): return
   
        ResultQuery = self.MyDB.executeQuery(DB.QUERY_DB.SELECT_LAST_AVAILABLE_SESSION, (username, username, username)).fetchall()

        if len(ResultQuery) == 0: U.ScriviLog("There are NO previous sessions to disconnect", U.LEVEL.INFO)

        elif len(ResultQuery) > 1: raise EX.MyLoginException("Anomalia sui dati. Troppe sessioni precedenti disponibili da disconnettere")

        else:
            
            U.ScriviLog("Previous session disconnession in progress...", U.LEVEL.INFO)

            Cookies = json.loads(ResultQuery[0]["COOKIES"])

            self.sessionContext.addCookies(json.loads(json.dumps(Cookies["cookies"])))
            
            self.sessionContext.X_Instagram_AJAX = Cookies["session"]["x_instagram_ajax"]
            self.sessionContext.X_IG_WWW_Claim = Cookies["session"]["x_ig_www_claim"]
            self.sessionContext.X_CSRF_Token = Cookies["session"]["csrf_token"]
            self.sessionContext.SessionID = Cookies["session"]["session_id"]

            self.sessionContext.LoggedUser = {"id" : Cookies["user"]["id"]}

            self.Logout()

        self.sessionContext.initializeData()

        header = {"X-Instagram-AJAX" : self.sessionContext.X_Instagram_AJAX,
                  "X-IG-WWW-Claim" : self.sessionContext.X_IG_WWW_Claim,
                  "X-CSRFToken" : self.sessionContext.X_CSRF_Token,
                  "X-ASBD-ID" : self.sessionContext.AppID,
                  "referer" : "https://www.instagram.com/"
                  }

        payload = {"enc_password" : f"#PWD_INSTAGRAM_BROWSER:0:{int(datetime.now().timestamp())}:{password}",
                   "trustedDeviceRecords" : {},
                   "optIntoOneTap" : "false",
                   "username" : username,
                   "queryParams" : {}
                   }

        ResponseLogin, ResponseLoginJSON = self.sessionContext.makeRequest(S.TYPE_REQUEST.POST, *[U.LOGIN_URL.LOGIN_URL], headers=header, payloads=payload, login_required=False)
        
        if ResponseLoginJSON["error"] == "checkpoint": self.checkpointRequired(responseJSON)

        if ResponseLoginJSON["error"] == "two_factor_required": 
            ResponseLogin, ResponseLoginJSON = self.TwoFactorLogin(ResponseLoginJSON, username)
            if ResponseLoginJSON["error"] == "checkpoint": 
                self.checkpointRequired(ResponseLoginJSON)

        if not ResponseLoginJSON["data"]["authenticated"]: raise EX.MyLoginException("username/password is NOT valid to login")

        self.sessionContext.X_IG_WWW_Claim = ResponseLogin.headers["x-ig-set-www-claim"]
        self.sessionContext.X_CSRF_Token = ResponseLogin.cookies["csrftoken"]                   # viene restituito un nuovo Token CSRF
        self.sessionContext.SessionID = ResponseLogin.cookies["sessionid"]

        self.sessionContext.LoggedUser = self.callAPI(U.API_ENDPOINTS.GET_USER_BY_ID, user_id=ResponseLoginJSON["data"]["userId"])

        additionalInfoEndpoint = user_endpoint.userEndpointAPI(self.sessionContext, self.MyDB, user_endpoint.USER_URL.ADDITIONAL_INFO_URL)
        additionalInfoJSON = additionalInfoEndpoint.getAdditionalInfo()

        email, phoneNumber = additionalInfoJSON["email"], additionalInfoJSON["phone_number"]

        Cookies = {"user" : {"username" : self.sessionContext.LoggedUser["username"],
                             "id" : self.sessionContext.LoggedUser["id"],
                             "phone" : phoneNumber,
                             "email" : email
                             },
                   "session" : {"trusted_device_nonce" : ResponseLoginJSON["data"].get("trustedDeviceNonce"),
                                "x_instagram_ajax" : self.sessionContext.X_Instagram_AJAX,
                                "x_ig_www_claim" : self.sessionContext.X_IG_WWW_Claim,
                                "csrf_token" : self.sessionContext.X_CSRF_Token,
                                "session_id" : self.sessionContext.SessionID,
                                "device_id" : self.sessionContext.Device_ID,
                                "x_asbd_id" : self.sessionContext.AppID,
                                "ig_did" : self.sessionContext.IG_DID,
                                "mid" : self.sessionContext.MID
                                },
                   "cookies" : self.sessionContext.MySession.cookies.get_dict()
                   }

        ResultQuery = self.MyDB.executeQuery(DB.QUERY_DB.SELECT_LAST_SESSION, (self.sessionContext.SessionID, self.sessionContext.LoggedUser["id"], self.sessionContext.SessionID, self.sessionContext.LoggedUser["id"])).fetchall()

        prgSession = 1 if len(ResultQuery) == 0 else ResultQuery[0]["NEW_PRG"] 

        parameters = (self.sessionContext.SessionID, prgSession, self.sessionContext.LoggedUser["id"], email, phoneNumber, json.dumps(Cookies), datetime.today(), None)

        self.MyDB.executeQuery(DB.QUERY_DB.INSERT_INFO_SESSION, parameters, True)

        U.ScriviLog(f"Login SUCCESSFUL as '{self.sessionContext.LoggedUser['username']}'", U.LEVEL.INFO)

    def Logout(self):
        
        header = {"X-Instagram-AJAX" : self.sessionContext.X_Instagram_AJAX,
                  "X-IG-WWW-Claim" : self.sessionContext.X_IG_WWW_Claim,
                  "X-CSRFToken" : self.sessionContext.X_CSRF_Token,
                  "referer" : "https://www.instagram.com/",
                  "X-ASBD-ID" : self.sessionContext.AppID,
                  }

        payload = {"user_id": self.sessionContext.LoggedUser["id"],
                   "one_tap_app_login" : "0"
                   }

        try: 
            
            ResponseLogout, ResponseLogoutJSON = self.sessionContext.makeRequest(S.TYPE_REQUEST.POST, *[U.LOGIN_URL.LOGOUT_URL], headers=header, payloads=payload)
            
        except EX.MyLoginRequiredException as err: 
    
            U.ScriviLog("Logout failed - La sessione salvata era già stata disconnessa manualmente", U.LEVEL.INFO)

        self.MyDB.executeQuery(DB.QUERY_DB.UPDATE_LOGOUT_SESSION, (datetime.today(), self.sessionContext.SessionID), True)

        self.sessionContext = S.MyInfoSession()

        U.ScriviLog(f"Logout SUCCESSFUL", U.LEVEL.INFO)

    def callAPI(self, codeAPI, **kwargs): 
        
        if not isinstance(codeAPI, U.API_ENDPOINTS): raise EX.MyTypeException(f"The parameter 'codeAPI' is NOT an Endpoint object --> {type(codeAPI)}")

        if codeAPI == U.API_ENDPOINTS.GET_USER_BY_USERNAME: 
            
            endpoint = user_endpoint.userEndpointAPI(self.sessionContext, self.MyDB, U.API_ENDPOINTS.GET_USER_BY_USERNAME)

        if codeAPI == U.API_ENDPOINTS.GET_USER_BY_ID: 

            endpoint = user_endpoint.userEndpointAPI(self.sessionContext, self.MyDB, U.API_ENDPOINTS.GET_USER_BY_ID)

        if codeAPI == U.API_ENDPOINTS.GET_FOLLOWINGS: 

            endpoint = friendship_endpoint.friendshipEndpointAPI(self.sessionContext, self.MyDB, U.API_ENDPOINTS.GET_FOLLOWINGS)

        if codeAPI == U.API_ENDPOINTS.GET_FOLLOWERS: 

            endpoint = friendship_endpoint.friendshipEndpointAPI(self.sessionContext, self.MyDB, U.API_ENDPOINTS.GET_FOLLOWERS)

        if codeAPI == U.API_ENDPOINTS.GET_FRIENDSHIP_STATUS: 

            endpoint = friendship_endpoint.friendshipEndpointAPI(self.sessionContext, self.MyDB, U.API_ENDPOINTS.GET_FRIENDSHIP_STATUS)
            
        if codeAPI == U.API_ENDPOINTS.GET_STORIES: 

            endpoint = feed_endpoint.feedEndpointAPI(self.sessionContext, self.MyDB, U.API_ENDPOINTS.GET_STORIES)

        if codeAPI == U.API_ENDPOINTS.GET_POSTS: 

            endpoint = feed_endpoint.feedEndpointAPI(self.sessionContext, self.MyDB, U.API_ENDPOINTS.GET_POSTS)

        if codeAPI == U.API_ENDPOINTS.UNFOLLOW_USER: pass

        if codeAPI == U.API_ENDPOINTS.FOLLOW_USER: 

            endpoint = friendship_endpoint.friendshipEndpointAPI(self.sessionContext, self.MyDB, U.API_ENDPOINTS.FOLLOW_USER)

        if codeAPI == U.API_ENDPOINTS.ACCEPT_FOLLOW: pass

        if codeAPI == U.API_ENDPOINTS.REJECT_FOLLOW: pass

        return endpoint.execute(**kwargs)
