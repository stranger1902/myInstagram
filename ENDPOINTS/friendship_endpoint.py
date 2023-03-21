from . import user_endpoint

import myInfoSession as S
import myException as EX
import myDatabase as DB
import costants as C
import utils as U
import json

class friendshipEndpointAPI():

    def __init__(self, sessionContext, database, url):

        if not isinstance(sessionContext, S.MyInfoSession): raise MyTypeException(f"The parameter 'sessionContext' is NOT a myInfoSession object --> {type(sessionContext)}")

        if not isinstance(database, DB.MyDatabase): raise MyTypeException(f"The parameter 'database' is NOT a Database object --> {type(database)}")

        self.sessionContext = sessionContext
        self.MyDB = database
        self.URL = url

    def execute(self, **kwargs):

        if self.URL is U.API_ENDPOINTS.GET_FRIENDSHIP_STATUS: return self.friendshipStatus(**kwargs)

        if self.URL is U.API_ENDPOINTS.ACCEPT_FOLLOW: return self.acceptFollowRequest(**kwargs)

        if self.URL is U.API_ENDPOINTS.GET_FOLLOWINGS: return self.getFollowings(**kwargs)

        if self.URL is U.API_ENDPOINTS.GET_FOLLOWERS: return self.getFollowers(**kwargs)

        if self.URL is U.API_ENDPOINTS.UNFOLLOW_USER: return self.unfollowUser(**kwargs)

        if self.URL is U.API_ENDPOINTS.FOLLOW_USER: return self.followUser(**kwargs)

        else: raise EX.MyInstagramException(f"Endpoint '{self.URL}' is NOT a valid friendshipEndpointAPI")

    def friendshipStatus(self, user_id):
        
        header = {"X-Instagram-AJAX" : self.sessionContext.X_Instagram_AJAX,
                  "X-IG-WWW-Claim" : self.sessionContext.X_IG_WWW_Claim,
                  "X-CSRFToken" : self.sessionContext.X_CSRF_Token,
                  "referer" : "https://www.instagram.com/",
                  "X-ASBD-ID" : self.sessionContext.AppID,
                  }

        ResponseFriendshipStatus, ResponseFriendshipStatusJSON = self.sessionContext.makeRequest(S.TYPE_REQUEST.GET, *[U.API_ENDPOINTS.GET_FRIENDSHIP_STATUS, user_id], headers=header)

        return {"you_received_request" : ResponseFriendshipStatusJSON["data"]["incoming_request"],
                "you_sent_request" : ResponseFriendshipStatusJSON["data"]["outgoing_request"],
                "it_follows_you" : ResponseFriendshipStatusJSON["data"]["followed_by"],
                "you_follow_it" : ResponseFriendshipStatusJSON["data"]["following"],
                "is_private" : ResponseFriendshipStatusJSON["data"]["is_private"]
                }

    def getFollowers(self, username, num_user_returned=100):

        currentUser = user_endpoint.userEndpointAPI(self.sessionContext, self.MyDB, U.API_ENDPOINTS.GET_USER_BY_USERNAME).execute(username=username)

        listFollowers = []

        if currentUser["friendship"]["is_private"] and not currentUser["friendship"]["you_follow_it"]:
            U.ScriviLog(f"Impossible to get followers list. The User '{username}' has a Private Account", U.LEVEL.INFO)
            return listFollowers

        header = {"Referer" : f"https://www.instagram.com/{currentUser['username']}/followers/",
                  "X-Instagram-AJAX" : self.sessionContext.X_Instagram_AJAX,
                  "X-IG-WWW-Claim" : self.sessionContext.X_IG_WWW_Claim,
                  "X-CSRFToken" : self.sessionContext.X_CSRF_Token,
                  "X-ASBD-ID" : self.sessionContext.AppID
                  }

        next_max_id = ""

        while(next_max_id is not None):
            
            queryParams = f"&max_id={next_max_id}" if next_max_id != "" else ""

            LINK = [U.API_ENDPOINTS.GET_FOLLOWERS, currentUser["id"], num_user_returned, queryParams]
            
            ResponseFollowers, ResponseFollowersJSON = self.sessionContext.makeRequest(S.TYPE_REQUEST.GET, *LINK, headers=header)

            next_max_id = ResponseFollowersJSON["data"].get("next_max_id")

            for user in ResponseFollowersJSON["data"]["users"]: listFollowers.append(user)

            U.ScriviLog(f"Extracted {len(listFollowers)} of {currentUser['follower_count']} Followers", U.LEVEL.INFO)

        U.ScriviLog(f"List of Followers ({len(listFollowers)}) of '{username}' was extracted", U.LEVEL.INFO)

        return listFollowers

    def getFollowings(self, username, num_user_returned=100):

        currentUser = user_endpoint.userEndpointAPI(self.sessionContext, self.MyDB, U.API_ENDPOINTS.GET_USER_BY_USERNAME).execute(username=username)

        listFollowings = []

        if currentUser["friendship"]["is_private"] and not currentUser["friendship"]["you_follow_it"]:
            U.ScriviLog(f"Impossible to get followings list. The User '{username}' has a Private Account", U.LEVEL.INFO)
            return listFollowings

        header = {"referer" : f"https://www.instagram.com/{currentUser['username']}/following/",
                  "X-Instagram-AJAX" : self.sessionContext.X_Instagram_AJAX,
                  "X-IG-WWW-Claim" : self.sessionContext.X_IG_WWW_Claim,
                  "X-CSRFToken" : self.sessionContext.X_CSRF_Token,
                  "X-ASBD-ID" : self.sessionContext.AppID
                  }

        next_max_id = ""

        while(next_max_id is not None):
            
            queryParams = f"&max_id={next_max_id}" if next_max_id != "" else ""

            LINK = [U.API_ENDPOINTS.GET_FOLLOWINGS, currentUser["id"], num_user_returned, queryParams]
            
            ResponseFollowings, ResponseFollowingsJSON = self.sessionContext.makeRequest(S.TYPE_REQUEST.GET, *LINK, headers=header)

            next_max_id = ResponseFollowingsJSON["data"].get("next_max_id")

            for user in ResponseFollowingsJSON["data"]["users"]: listFollowings.append(user)

            U.ScriviLog(f"Extracted {len(listFollowings)} of {currentUser['following_count']} Followings", U.LEVEL.INFO)

        U.ScriviLog(f"List of Followings ({len(listFollowings)}) of '{username}' was extracted", U.LEVEL.INFO)

        return listFollowings

    def followUser(self, username):
                
        if self.sessionContext.LoggedUser["username"] == username: return U.ScriviLog("You are trying to follow yourself", U.LEVEL.ERROR)

        currentUser = user_endpoint.userEndpointAPI(self.sessionContext, self.MyDB, U.API_ENDPOINTS.GET_USER_BY_USERNAME).execute(username=username)

        if currentUser["friendship"]["you_follow_it"]: return U.ScriviLog(f"You already follow '{username}'", U.LEVEL.INFO)

        #TODO: se ho mandato la richiesta e poi questa viene rifiutata, tale campo viene ripristinato a False???
        if currentUser["friendship"]["you_sent_request"]: return U.ScriviLog(f"You have already sent friendship request to '{username}'", U.LEVEL.INFO)

        header = {"referer" : f"https://www.instagram.com/{currentUser['username']}/",
                  "X-Instagram-AJAX" : self.sessionContext.X_Instagram_AJAX,
                  "X-IG-WWW-Claim" : self.sessionContext.X_IG_WWW_Claim,
                  "X-CSRFToken" : self.sessionContext.X_CSRF_Token,
                  "X-ASBD-ID" : self.sessionContext.AppID
                  }

        payload = {"nav_chain" : "PolarisFeedRoot:feedPage:1:via_cold_start,PolarisProfileRoot:profilePage:2:unexpected",
                   "container_module" : "profile",
                   "user_id" : currentUser["id"]
                   }

        ResponseFollowUser, ResponseFollowUserJSON = self.sessionContext.makeRequest(S.TYPE_REQUEST.POST, *[U.API_ENDPOINTS.FOLLOW_USER, currentUser["id"]], headers=header, payloads=payload)

        if not ResponseFollowUserJSON["data"]["status"] == "ok": raise EX.MyInstagramException(f"Request to follow '{username}' is failed")

        friendshipStatus = ResponseFollowUserJSON["data"]["friendship_status"]
       
        if friendshipStatus["following"]: U.ScriviLog(f"Now you follow '{username}'", U.LEVEL.INFO)

        else:
        
            if friendshipStatus["is_private"] and friendshipStatus["outgoing_request"]: U.ScriviLog(f"You sent friendship request to '{username}'", U.LEVEL.INFO)

            else: raise EX.MyInstagramException(ResponseFollowUserJSON)
        
    def unfollowUser(self, username):
        
        if self.sessionContext.LoggedUser["username"] == username: return U.ScriviLog("You are trying to unfollow yourself", U.LEVEL.ERROR)
        
        currentUser = user_endpoint.userEndpointAPI(self.sessionContext, self.MyDB, U.API_ENDPOINTS.GET_USER_BY_USERNAME).execute(username=username)

        if not currentUser["friendship"]["you_follow_it"]: return U.ScriviLog(f"Request to unfollow failed. You don't follow '{username}'", U.LEVEL.INFO)

        header = {"Referer" : f"https://www.instagram.com/{currentUser['username']}/",
                  "X-Instagram-AJAX" : self.sessionContext.X_Instagram_AJAX,
                  "X-IG-WWW-Claim" : self.sessionContext.X_IG_WWW_Claim,
                  "X-CSRFToken" : self.sessionContext.X_CSRF_Token,
                  "X-ASBD-ID" : self.sessionContext.AppID
                  }

        payload = {"nav_chain" : "PolarisFeedRoot:feedPage:1:via_cold_start,PolarisProfileRoot:profilePage:2:unexpected",
                   "container_module" : "profile",
                   "user_id" : currentUser["id"]
                   }

        ResponseUnfollowUser, ResponseUnfollowUserJSON = self.sessionContext.makeRequest(S.TYPE_REQUEST.POST, *[U.API_ENDPOINTS.UNFOLLOW_USER, currentUser["id"]], headers=header, payloads=payload)

        if ResponseUnfollowUserJSON["data"]["status"] == "ok": U.ScriviLog(f"You unfollowed '{username}' correctly", U.LEVEL.INFO)

        else: raise EX.MyInstagramException(ResponseUnfollowUserJSON)

    def acceptFollowRequest(self, username):

        currentUser = user_endpoint.userEndpointAPI(self.sessionContext, self.MyDB, U.API_ENDPOINTS.GET_USER_BY_USERNAME).execute(username=username)

        U.ScriviLog(currentUser, U.LEVEL.INFO)

        if not currentUser["friendship"]["you_received_request"]: return U.ScriviLog(f"You have NOT received follow request by '{username}'", U.LEVEL.INFO)

        header = {"referer" : f"https://www.instagram.com/{currentUser['username']}/",
                  "X-Instagram-AJAX" : self.sessionContext.X_Instagram_AJAX,
                  "X-IG-WWW-Claim" : self.sessionContext.X_IG_WWW_Claim,
                  "X-CSRFToken" : self.sessionContext.X_CSRF_Token,
                  "X-ASBD-ID" : self.sessionContext.AppID
                  }

        ResponseAcceptFollow, ResponseAcceptFollowJSON = self.sessionContext.makeRequest(S.TYPE_REQUEST.POST, *[U.API_ENDPOINTS.ACCEPT_FOLLOW, currentUser["id"]], headers=header, payloads={})

        if ResponseAcceptFollowJSON["data"]["status"] == "ok": U.ScriviLog(f"You accepted follow request received by '{username}' correctly", U.LEVEL.INFO)

        else: raise EX.MyInstagramException(ResponseAcceptFollowJSON)
