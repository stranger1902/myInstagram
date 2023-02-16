import utils as U
import argparse

from myInstagram import MyInstagram
from init import init

if __name__ == "__main__":

    init()
    
    credentials = [input("username: "), input("password: ")]

    myInstaClient = MyInstagram()

    myInstaClient.Login(*credentials)

    U.ScriviLog(myInstaClient.callAPI(U.API_ENDPOINTS.GET_USER_BY_USERNAME, username="my_android_guide"), U.LEVEL.INFO)

    #myInstaClient.callAPI(U.API_ENDPOINTS.GET_FOLLOWINGS, username="my_android_guide")
    #myInstaClient.callAPI(U.API_ENDPOINTS.GET_FOLLOWERS, username="my_android_guide")
    #myInstaClient.callAPI(U.API_ENDPOINTS.FOLLOW_USER, username="my_android_guide")
    #myInstaClient.callAPI(U.API_ENDPOINTS.GET_STORIES, username="my_android_guide")
    #myInstaClient.callAPI(U.API_ENDPOINTS.GET_POSTS, username="my_android_guide")
