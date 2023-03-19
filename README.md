# myInstagram

Python implementation of a Instagram API based on the official Instagram API, in particular, you can: 
- get a list of followings about users
- get a list of followers about users
- get a list of stories about users
- get a list of posts about users
- follow/unfollow users
- get info about users
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

python3 init.py
```

## API Methods
    
### GET_USER_BY_USERNAME

This method return info about a user using its Instagram username (es. @my_android_guide)

Params:

    username (str): Instagram username of the user

Return value:

    dict: info of the user

How to call method:

```python
callAPI(API_ENDPOINTS.GET_USER_BY_USERNAME, username="my_android_guide")
 ```

### GET_USER_BY_ID

This method return info about a user using its Instagram ID (es. 44575834543)

Params:

    user_id (str): Instagram ID associated to an user Instagram account

Return value:

    dict: info of the user

How to call method:

```python
callAPI(API_ENDPOINTS.GET_USER_BY_ID, user_id="44575834543")
 ```

### GET_FOLLOWINGS

This method return all users that follow another user

Params:

    username (str): Instagram username of the user you want get list of following users

Return value:

    list: list of all following users 

How to call method:

```python
callAPI(API_ENDPOINTS.GET_FOLLOWINGS, username="my_android_guide")
 ```

### GET_FOLLOWERS

This method return all users that are followed by another user

Params:

    username (str): Instagram username of the user you want get list of follower users

Return value:

    list: list of all follower users 

How to call method:

```python
callAPI(API_ENDPOINTS.GET_FOLLOWERS, username="my_android_guide")
 ```

### FOLLOW_USER

This method send a friendship request to follow a user

Params:

    username (str): Instagram username of the user you want follow

Return value:

    None

How to call method:

```python
callAPI(API_ENDPOINTS.FOLLOW_USER, username="my_android_guide")
 ```

### UNFOLLOW_USER

This method send a friendship request to unfollow a user you want follow anynore

Params:

    username (str): Instagram username of the user you want unfollow

Return value:

    None

How to call method:

```python
callAPI(API_ENDPOINTS.UNFOLLOW_USER, username="my_android_guide")
 ```

### GET_FRIENDSHIP_STATUS

This method return info about the friendship status with another user (es. you follow it, you sent a friendship request ecc..)

Params:

    username (str): Instagram username of the user

Return value:

    dict: friendship info of the user

How to call method:

```python
callAPI(API_ENDPOINTS.GET_FRIENDSHIP_STATUS, username="my_android_guide")
 ```

### GET_STORIES

This method download all stories published by another user 

Params:

    username (str): Instagram username of the user

Return value:

    None

How to call method:

```python
callAPI(API_ENDPOINTS.GET_STORIES, username="my_android_guide")
 ```

### GET_POSTS

This method download all posts published by another user 

Params:

    username (str): Instagram username of the user

Return value:

    None

How to call method:

```python
callAPI(API_ENDPOINTS.GET_POSTS, username="my_android_guide")
 ```
 
## Usage

This is a simple way to interact with Instagram API.

```python
from myInstagram import MyInstagram
from utils import API_ENDPOINTS

if __name__ == "__main__":

    credentials = [input("username: "), input("password: ")]

    myInstaClient = MyInstagram()

    myInstaClient.Login(*credentials)

    infoUser = myInstaClient.callAPI(API_ENDPOINTS.GET_USER_BY_USERNAME, username="my_android_guide")

    myInstaClient.callAPI(API_ENDPOINTS.GET_STORIES, username="my_android_guide")
```
