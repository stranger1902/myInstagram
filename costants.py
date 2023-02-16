from datetime import datetime

import platform
import os

SEPARATOR = "\\" if platform.system() == "Windows" else "/"

CURRENT_DATE = datetime.today().strftime("%d_%m_%Y")
CURRENT_PATH = os.getcwd()

DATABASE_FILENAME = "InstagramDB.db"

X_IG_APP_ID = "936619743392459"

MAX_RETRY_TWO_FACTOR_LOGIN = 3

VERSION_API = "v1"

API_BASE_URL = "https://www.instagram.com/api/" + VERSION_API + "/"
BASE_URL = "https://www.instagram.com"

IG_APP_VERSION = "264.0.0.22.106"
PHONE_RESOLUTION = "1080x2280"
PHONE_MANUFACTURER = "samsung"
PHONE_CODE_MODEL = "BOT-1234"       # es. SM-G970F
VERSION_CODE = "366409693"
ANDROID_API_LEVEL = "24"
ANDROID_RELEASE = "12"
PHONE_CHIPSET = "qcom"
PHONE_MODEL = "s10e"
PHONE_DPI = "438dpi"
LANGUAGE = "it_IT"

USER_AGENT_IG_FORMAT = f"Instagram {IG_APP_VERSION} Android ({ANDROID_API_LEVEL}/{ANDROID_RELEASE}; {PHONE_DPI}; {PHONE_RESOLUTION}; {PHONE_MANUFACTURER}; {PHONE_CODE_MODEL}; {PHONE_MODEL}; {PHONE_CHIPSET}; {LANGUAGE}; {VERSION_CODE})"
USER_AGENT_BROWSER = f"Mozilla/5.0 (Linux; Android {ANDROID_RELEASE}; {PHONE_CODE_MODEL}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36"

USER_AGENT_DEVICE = USER_AGENT_BROWSER + " " + USER_AGENT_IG_FORMAT

HEADER = {"Accept-Encoding" : "gzip, deflate, br",
          "Origin" : "https://www.instagram.com",
          "X-Requested-With" : "XMLHttpRequest",
          "Sec-Fetch-Site" : "same-origin",
          "user-agent" : USER_AGENT_DEVICE,
          "Host" : "www.instagram.com",
          "X-IG-App-ID" : X_IG_APP_ID,
          "Connection" : "keep-alive",
          "Sec-Fetch-Dest" : "empty",
          "Sec-Fetch-Mode" : "cors",
          "Accept" : "*/*"
          }