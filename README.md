# myInstagram

Python implementation of a Instagram API based on the official Instagram API, in particular, you can: 
- get a list of followings about users
- get a list of followers about users
- get a list of stories about users
- get a list of posts about users
- get info about users
- follow users
- login/logout

**ATTENTION!** This is just an un-official Instagram API for educational purpose.

## Table of Contents

- [Installation](#installation)
- [API Methods](#api-methods)
- [Usage](#usage)

## Installation

```bash
python3 -m venv venv/
source venv/bin/activate
pip install -r requirements.txt
```

## API Methods

        ... TODO ...

## Usage

This is a simple way to interact with Instagram API.

```python
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
```
