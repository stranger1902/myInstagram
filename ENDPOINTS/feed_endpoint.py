from . import media_endpoint, user_endpoint
from datetime import datetime

import myInfoSession as S
import myException as EX
import myDatabase as DB
import costants as C
import utils as U
import json
import os 

class feedEndpointAPI():

    def __init__(self, sessionContext, database, url):

        if not isinstance(sessionContext, S.MyInfoSession): raise MyTypeException(f"The parameter 'sessionContext' is NOT a myInfoSession object --> {type(sessionContext)}")

        if not isinstance(database, DB.MyDatabase): raise MyTypeException(f"The parameter 'database' is NOT a Database object --> {type(database)}")

        self.sessionContext = sessionContext
        self.MyDB = database
        self.URL = url

    def execute(self, **kwargs):

        if self.URL is U.API_ENDPOINTS.GET_STORIES: return self.getStories(**kwargs)

        if self.URL is U.API_ENDPOINTS.GET_POSTS: return self.getPosts(**kwargs)

        else: raise EX.MyInstagramException(f"Endpoint {self.URL} is NOT a valid feedEndpointAPI")

    #TODO: gestire la paginazione???
    def getStories(self, username):
        
        userByUsernameEndpoint = user_endpoint.userEndpointAPI(self.sessionContext, self.MyDB, U.API_ENDPOINTS.GET_USER_BY_USERNAME)

        currentUser = userByUsernameEndpoint.execute(username=username)
        
        if currentUser["friendship"]["is_private"] and not currentUser["friendship"]["you_follow_it"]:
            return U.ScriviLog(f"Impossible to get Stories. '{username}' has a Private Account", U.LEVEL.INFO)

        header = {"X-Instagram-AJAX" : self.sessionContext.X_Instagram_AJAX,
                  "X-IG-WWW-Claim" : self.sessionContext.X_IG_WWW_Claim,
                  "X-CSRFToken" : self.sessionContext.X_CSRF_Token,
                  "X-ASBD-ID" : self.sessionContext.AppID,
                  "Referer" : "https://www.instagram.com/"
                  }

        ResponseStories, ResponseStoriesJSON = self.sessionContext.makeRequest(S.TYPE_REQUEST.GET, *[U.API_ENDPOINTS.GET_STORIES, currentUser["id"]], headers=header)
        
        if not ResponseStoriesJSON["data"]["reels"]: return U.ScriviLog(f"User '{username}' has NO Stories", U.LEVEL.INFO)
 
        USER_FOLDER_PATH = U.PATH.STORIES_FILE_PATH.value + username
        DATE_PATH = USER_FOLDER_PATH + C.SEPARATOR + datetime.now().strftime('%d.%m.%Y')
        
        if not os.path.exists(USER_FOLDER_PATH): os.mkdir(USER_FOLDER_PATH)

        if not os.path.exists(DATE_PATH): os.mkdir(DATE_PATH)

        open(DATE_PATH + C.SEPARATOR + U.FILENAME.NOMEDIA_FILE.value, "w").close()
        
        for story in ResponseStoriesJSON["data"]["reels"][currentUser["id"]]["items"]:                

            storyID = story["pk"]

            publicationDate = datetime.fromtimestamp(story["taken_at"]).strftime('%d.%m.%Y_%Hh%Mm')
            filename = f"{storyID}_{publicationDate}"
            
            if self.sessionContext.LoggedUser["id"] == currentUser["id"]: 
                
                mediaEndpoint = media_endpoint.mediaEndpointAPI(self.sessionContext, self.MyDB, media_endpoint.MEDIA_URL.GET_VIEWERS_STORY)

                mediaEndpoint.getViewersStory(storyID, DATE_PATH + C.SEPARATOR + str(storyID) + ".txt")

            if story["media_type"] == 1: U.downloadImage(story["image_versions2"]["candidates"][0]["url"], DATE_PATH, filename)
            
            elif story["media_type"] == 2: U.downloadVideo(story["video_versions"][0]["url"], DATE_PATH, filename)
            
            else: raise EX.MyInstagramException("Tipo Media NON gestito: " + story["media_type"])

    #TODO: gestire numero limite posts da scaricare 
    def getPosts(self, username, num_posts_returned=20, limit_posts=0): 
        
        userByUsernameEndpoint = user_endpoint.userEndpointAPI(self.sessionContext, self.MyDB, U.API_ENDPOINTS.GET_USER_BY_USERNAME)

        currentUser = userByUsernameEndpoint.execute(username=username)
        
        if currentUser["friendship"]["is_private"] and not currentUser["friendship"]["you_follow_it"]:
            return U.ScriviLog(f"Impossible to get Posts. '{username}' has a Private Account", U.LEVEL.INFO)

        header = {"X-Instagram-AJAX" : self.sessionContext.X_Instagram_AJAX,
                  "X-IG-WWW-Claim" : self.sessionContext.X_IG_WWW_Claim,
                  "X-CSRFToken" : self.sessionContext.X_CSRF_Token,
                  "X-ASBD-ID" : self.sessionContext.AppID,
                  "Referer" : "https://www.instagram.com/"
                  }

        USER_FOLDER_PATH = U.PATH.POSTS_FILE_PATH.value + username

        if not os.path.exists(USER_FOLDER_PATH): os.mkdir(USER_FOLDER_PATH)

        open(USER_FOLDER_PATH + C.SEPARATOR + U.FILENAME.NOMEDIA_FILE.value, "w").close()

        next_max_id = ""

        while(next_max_id is not None):

            queryParams = f"&max_id={next_max_id}" if next_max_id != "" else ""

            LINK = [U.API_ENDPOINTS.GET_POSTS, currentUser["username"], num_posts_returned, queryParams]

            ResponsePosts, ResponsePostsJSON = self.sessionContext.makeRequest(S.TYPE_REQUEST.GET, *LINK, headers=header)
            
            next_max_id = ResponsePostsJSON.get("next_max_id")

            for post in ResponsePostsJSON["data"]["items"]:
                
                publicationDate = datetime.fromtimestamp(post["taken_at"]).strftime('%d.%m.%Y_%Hh%Mm')
                filename = f"{post['pk']}_{publicationDate}"
                
                if post["media_type"] == 1: U.downloadImage(post["image_versions2"]["candidates"][0]["url"], USER_FOLDER_PATH, filename)
                
                elif post["media_type"] == 2: U.downloadVideo(post["video_versions"][0]["url"], USER_FOLDER_PATH, filename)
                
                elif post["media_type"] == 8:

                    for index, post in enumerate(post["carousel_media"]):

                        filename = f"{str(post['pk']) + '_' + str(index + 1)}_{publicationDate}"

                        if post["media_type"] == 1: U.downloadImage(post["image_versions2"]["candidates"][0]["url"], USER_FOLDER_PATH, filename)
                        
                        elif post["media_type"] == 2: U.downloadVideo(post["video_versions"][0]["url"], USER_FOLDER_PATH, filename)
                        
                        else: raise EX.MyInstagramException(post)

                else: raise EX.MyInstagramException(ResponsePostsJSON)
