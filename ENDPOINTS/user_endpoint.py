from . import friendship_endpoint
from datetime import datetime
from enum import Enum

import myInfoSession as S
import myException as EX
import myDatabase as DB
import costants as C
import utils as U
import json

class USER_URL(Enum): ADDITIONAL_INFO_URL = C.API_BASE_URL + "accounts/edit/web_form_data/"

class userEndpointAPI():

    def __init__(self, sessionContext, database, url):

        if not isinstance(sessionContext, S.MyInfoSession): raise MyTypeException(f"The parameter 'sessionContext' is NOT a myInfoSession object --> {type(sessionContext)}")

        if not isinstance(database, DB.MyDatabase): raise MyTypeException(f"The parameter 'database' is NOT a Database object --> {type(database)}")

        self.sessionContext = sessionContext
        self.MyDB = database
        self.URL = url

    def execute(self, **kwargs):
        
        if self.URL is U.API_ENDPOINTS.GET_USER_BY_USERNAME: return self.getInfoByNickname(**kwargs)

        if self.URL is U.API_ENDPOINTS.GET_USER_BY_ID: return self.getInfoByID(**kwargs)

        else: raise EX.MyInstagramException(f"Endpoint '{self.URL}' is NOT a valid userEndpointAPI")

    def getInfoByNickname(self, username):
        
        header = {"X-Instagram-AJAX" : self.sessionContext.X_Instagram_AJAX,
                  "X-IG-WWW-Claim" : self.sessionContext.X_IG_WWW_Claim,
                  "X-CSRFToken" : self.sessionContext.X_CSRF_Token,
                  "referer" : "https://www.instagram.com/",
                  "X-ASBD-ID" : self.sessionContext.AppID
                  }

        ResponseUser, ResponseUserJSON = self.sessionContext.makeRequest(S.TYPE_REQUEST.GET, *[self.URL, username], headers=header)
        
        if not ResponseUserJSON["data"]["data"]["user"]: raise EX.MyInstagramException(f"'{username}' has blocked '{self.sessionContext.LoggedUser['username']}'")

        friendshipStatusEndpoint = friendship_endpoint.friendshipEndpointAPI(self.sessionContext, self.MyDB, U.API_ENDPOINTS.GET_FRIENDSHIP_STATUS)

        friendshipStatus = friendshipStatusEndpoint.execute(user_id=ResponseUserJSON["data"]["data"]["user"]["id"])

        userInfo = {"follower_count" : ResponseUserJSON["data"]["data"]["user"]["edge_followed_by"]["count"],
                    "following_count" : ResponseUserJSON["data"]["data"]["user"]["edge_follow"]["count"],
                    "fullname" : ResponseUserJSON["data"]["data"]["user"]["full_name"],
                    "username" : ResponseUserJSON["data"]["data"]["user"]["username"],
                    "id" : ResponseUserJSON["data"]["data"]["user"]["id"],
                    "friendship" : friendshipStatus
                    }

        ResultQuery = self.MyDB.executeQuery(DB.QUERY_DB.SELECT_USER, (userInfo["id"],)).fetchall()

        if len(ResultQuery) > 1: raise EX.MyDatabaseException(f"Esistono più utenti salvati con id '{userInfo['id']}'")

        if len(ResultQuery) == 0: self.MyDB.executeQuery(DB.QUERY_DB.INSERT_USER, (userInfo["id"], userInfo["username"], datetime.today(), datetime.today()), True)

        else: self.MyDB.executeQuery(DB.QUERY_DB.UPDATE_USER, (datetime.today(), userInfo["id"]), True)

        return userInfo

    def getInfoByID(self, user_id):

        header = {"X-Instagram-AJAX" : self.sessionContext.X_Instagram_AJAX,
                  "X-IG-WWW-Claim" : self.sessionContext.X_IG_WWW_Claim,
                  "X-CSRFToken" : self.sessionContext.X_CSRF_Token,
                  "referer" : "https://www.instagram.com/",
                  "X-ASBD-ID" : self.sessionContext.AppID
                  }
            
        ResponseUser, ResponseUserJSON = self.sessionContext.makeRequest(S.TYPE_REQUEST.GET, *[self.URL, user_id], headers=header)
        
        friendshipStatusEndpoint = friendship_endpoint.friendshipEndpointAPI(self.sessionContext, self.MyDB, U.API_ENDPOINTS.GET_FRIENDSHIP_STATUS)

        friendshipStatus = friendshipStatusEndpoint.execute(user_id=user_id)

        userInfo = {"following_count" : ResponseUserJSON["data"]["user"]["following_count"],
                    "follower_count" : ResponseUserJSON["data"]["user"]["follower_count"],
                    "fullname" : ResponseUserJSON["data"]["user"]["full_name"],
                    "username" : ResponseUserJSON["data"]["user"]["username"],
                    "id" : ResponseUserJSON["data"]["user"]["pk"],
                    "friendship" : friendshipStatus
                    }

        ResultQuery = self.MyDB.executeQuery(DB.QUERY_DB.SELECT_USER, (userInfo["id"],)).fetchall()

        if len(ResultQuery) > 1: raise EX.MyDatabaseException(f"Esistono più utenti salvati con id '{userInfo['id']}'")

        if len(ResultQuery) == 0: self.MyDB.executeQuery(DB.QUERY_DB.INSERT_USER, (userInfo["id"], userInfo["username"], datetime.today(), datetime.today()), True)

        else: self.MyDB.executeQuery(DB.QUERY_DB.UPDATE_USER, (datetime.today(), userInfo["id"]), True)

        return userInfo

    def getAdditionalInfo(self):

        header = {"X-Instagram-AJAX" : self.sessionContext.X_Instagram_AJAX,
                  "referer" : "https://www.instagram.com/accounts/edit/",
                  "X-IG-WWW-Claim" : self.sessionContext.X_IG_WWW_Claim,
                  "X-CSRFToken" : self.sessionContext.X_CSRF_Token,
                  "X-ASBD-ID" : self.sessionContext.AppID,
                  "DNT" : "1"
                  }

        ResponseMoreInfoUser, ResponseMoreInfoUserJSON = self.sessionContext.makeRequest(S.TYPE_REQUEST.GET, *[USER_URL.ADDITIONAL_INFO_URL], headers=header)

        return {"phone_number" : ResponseMoreInfoUserJSON["data"]["form_data"]["phone_number"].replace(" ", ""),
                "email" : ResponseMoreInfoUserJSON["data"]["form_data"]["email"]
                }
         