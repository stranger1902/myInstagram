from enum import Enum

import myInfoSession as S
import myException as EX
import myDatabase as DB
import costants as C
import utils as U
import json
import os 

class MEDIA_URL(Enum):

    GET_VIEWERS_STORY = C.API_BASE_URL + "media/{}/list_reel_media_viewer/"

class mediaEndpointAPI():

    def __init__(self, sessionContext, database, url):

        if not isinstance(sessionContext, S.MyInfoSession): raise MyTypeException(f"The parameter 'sessionContext' is NOT a myInfoSession object --> {type(sessionContext)}")

        if not isinstance(database, DB.MyDatabase): raise MyTypeException(f"The parameter 'database' is NOT a Database object --> {type(database)}")

        self.sessionContext = sessionContext
        self.MyDB = database
        self.URL = url

    def execute(self, **kwargs): pass

    def getViewersStory(self, story_id, path_destination):

        viewersList = []
        next_max_id = ""
        counter = 1

        header = {"Referer" : f"https://www.instagram.com/stories/{self.sessionContext.LoggedUser['username']}/{story_id}/",
                  "X-Instagram-AJAX" : self.sessionContext.X_Instagram_AJAX,
                  "X-IG-WWW-Claim" : self.sessionContext.X_IG_WWW_Claim,
                  "X-CSRFToken" : self.sessionContext.X_CSRF_Token,
                  "X-ASBD-ID" : self.sessionContext.AppID,
                  "TE" : "trailers"
                  }

        payload = {"include_blacklist_sample" : "true"}

        while(next_max_id is not None):

            ResponseViewersStory, ResponseViewersStoryJSON = self.sessionContext.makeRequest(S.TYPE_REQUEST.POST, *[MEDIA_URL.GET_VIEWERS_STORY, story_id], headers=header, payloads=payload)

            next_max_id = ResponseViewersStoryJSON["data"].get("next_max_id")

            if next_max_id: payload["max_id"] = next_max_id
            
            for user in ResponseViewersStoryJSON["data"]["viewers"]: 
                
                viewersList.append(str(counter) + ": " + user["user"]["username"] + " - " + str(user["has_liked"]) +  " - " + user["user"]["profile_pic_url"] + "\n")

                counter += 1
        
        if os.path.exists(path_destination): os.remove(path_destination)

        with open(path_destination, "a") as viewerFile: viewerFile.writelines(viewersList)

        return viewersList