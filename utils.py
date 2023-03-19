import myException as EX
import costants as C
import traceback
import requests
import json
import os
import io

from datetime import datetime
from enum import Enum
from PIL import Image

class PATH(Enum): 

    STORIES_FILE_PATH = C.CURRENT_PATH + C.SEPARATOR + "STORIES" + C.SEPARATOR
    LIMITS_FILE_PATH = C.CURRENT_PATH + C.SEPARATOR + "LIMITS" + C.SEPARATOR
    POSTS_FILE_PATH = C.CURRENT_PATH + C.SEPARATOR + "POSTS" + C.SEPARATOR
    LOG_FILE_PATH = C.CURRENT_PATH + C.SEPARATOR + "LOGS" + C.SEPARATOR

class FILENAME(Enum): 

    LOG_FILE = f"log_{C.CURRENT_DATE}.txt"
    NOMEDIA_FILE = ".nomedia"

class LEVEL(Enum):

    INPUT = "INPUT"
    DEBUG = "DEBUG"
    ERROR = "ERROR"
    INFO = "INFO"

class LOGIN_URL(Enum):

    TAKE_CHALLENGE_URL = C.API_BASE_URL + "bloks/apps/com.instagram.challenge.navigation.take_challenge/"
    SMS_TWO_FACTOR_URL = C.API_BASE_URL + "web/accounts/send_two_factor_login_sms/"
    LOGIN_TWO_FACTOR_URL = C.API_BASE_URL + "web/accounts/login/ajax/two_factor/"
    SHARED_DATA_URL = C.API_BASE_URL + "web/data/shared_data/"
    LOGOUT_URL = C.API_BASE_URL + "web/accounts/logout/ajax/" 
    LOGIN_URL = C.API_BASE_URL + "web/accounts/login/ajax/"
    CHALLENGE_ACTION_URL = C.BASE_URL + "{}"

class API_ENDPOINTS(Enum):

    # users endpoints
    GET_USER_BY_USERNAME = C.API_BASE_URL + "users/web_profile_info/?username={}"
    GET_USER_BY_ID = C.API_BASE_URL + "users/{}/info/"
    # friendships endpoints
    GET_FOLLOWINGS = C.API_BASE_URL + "friendships/{}/following/?count={}{}"
    GET_FOLLOWERS = C.API_BASE_URL + "friendships/{}/followers/?count={}{}"
    GET_FRIENDSHIP_STATUS = C.API_BASE_URL + "friendships/show/{}/"
    UNFOLLOW_USER = C.API_BASE_URL + "friendships/destroy/{}/"
    FOLLOW_USER = C.API_BASE_URL + "friendships/create/{}/"
    ACCEPT_FOLLOW = None                                                                    #TODO: da implementare metodo
    REJECT_FOLLOW = None                                                                    #TODO: da implementare metodo
    # feeds endpoints
    GET_POSTS = C.API_BASE_URL + "feed/user/{}/username/?count={}{}"
    GET_STORIES = C.API_BASE_URL + "feed/reels_media/?reel_ids={}"

CRITICAL_REQUESTS = [API_ENDPOINTS.FOLLOW_USER, API_ENDPOINTS.UNFOLLOW_USER, API_ENDPOINTS.ACCEPT_FOLLOW, API_ENDPOINTS.REJECT_FOLLOW]

def ScriviLog(msg, level, color=None, verbose=False):

    if not isinstance(level, LEVEL): raise Exception(f"The parameter 'level' is NOT a LEVEL object --> {type(level)}")

    if not isinstance(verbose, bool): raise Exception(f"The parameter 'verbose' is NOT a Boolean --> {type(verbose)}")

    if not os.path.exists(PATH.LOG_FILE_PATH.value): raise Exception(f"Il percorso '{PATH.LOG_FILE_PATH.value}' NON esiste. Creare la cartella 'LOGS'")

    if verbose and level is LEVEL.ERROR: traceback.print_stack()

    msg = "\n" + json.dumps(msg, indent=4) if isinstance(msg, dict) or isinstance(msg, list) else str(msg)

    with open(PATH.LOG_FILE_PATH.value + FILENAME.LOG_FILE.value, "a") as fileLog: fileLog.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t[{level.value}]\t\t{msg}\n")

    if color: print(color + datetime.now().strftime("%d-%m-%Y %H:%M:%S") + "\t[" + f"{level.value}" + "]\t\t" + f"{msg}", Style.RESET_ALL)
    
    else: print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\t[" + f"{level.value}" + "]\t\t" + f"{msg}")

def myInput(msg, no_upper=False): 
    
    if no_upper: return input(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t[{LEVEL.INPUT.value}]\t\t{msg}").strip()
    
    return input(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t[{LEVEL.INPUT.value}]\t\t{msg}").strip().upper()
    
def createFolders():
    
    if not os.path.exists(PATH.STORIES_FILE_PATH.value): os.mkdir(PATH.STORIES_FILE_PATH.value)

    #if not os.path.exists(PATH.LIMITS_FILE_PATH.value): os.mkdir(PATH.LIMITS_FILE_PATH.value)

    if not os.path.exists(PATH.POSTS_FILE_PATH.value): os.mkdir(PATH.POSTS_FILE_PATH.value)

    if not os.path.exists(PATH.LOG_FILE_PATH.value): os.mkdir(PATH.LOG_FILE_PATH.value)

def downloadImage(url, path_destination, filename, format_image="jpg"):

    FILE_PATH = path_destination + C.SEPARATOR + f"{filename}.{format_image}"

    if os.path.exists(FILE_PATH): return ScriviLog(f"File '{FILE_PATH}' is already downloaded", LEVEL.INFO)

    ResponseImageStory = requests.get(url, headers={"user-agent" : C.USER_AGENT_DEVICE})

    with Image.open(io.BytesIO(ResponseImageStory.content)) as image: image.save(FILE_PATH)
    
    ScriviLog(f"File '{FILE_PATH}' downloaded", LEVEL.INFO)

def downloadVideo(url, path_destination, filename, format_video="mp4"):

    FILE_PATH = path_destination + C.SEPARATOR + f"{filename}.{format_video}"

    if os.path.exists(FILE_PATH): return ScriviLog(f"File '{FILE_PATH}' is already downloaded", LEVEL.INFO)

    ResponseVideoStory = requests.get(url, headers={"user-agent" : C.USER_AGENT_DEVICE}, stream=True)

    with open(FILE_PATH, 'wb') as video:
        for chunk in ResponseVideoStory.iter_content(chunk_size=1024): video.write(chunk)
        
    ScriviLog(f"File '{FILE_PATH}' downloaded", LEVEL.INFO)