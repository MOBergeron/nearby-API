<p align="center"><img src="https://cloud.githubusercontent.com/assets/838845/22188506/d9a96e0c-e0e3-11e6-9c3f-84a01cf50039.png"></p>

# Nearby-API

###Contents
- [API Documentation] (#api-documentation)
  - [Error Messages] (#error-messages)
  - GET
    - [Get a spotted] (#get-a-spotted)
    - [Get Spotteds] (#get-spotteds)
    - [Get my Spotteds] (#get-my-spotteds)
    - [Get Spotteds by user ID] (#get-spotteds-by-user-id)
    - [Get a User] (#get-a-user)
    - [Get my User] (#get-my-user)
  - POST
    - [Create Account and Authentication] (#create-account-and-authentication)
    - [Create a spotted] (#create-a-spotted)
    - [Disable account] (#disable-account)
    - [Link Facebook] (#link-facebook)
    - [Link Google] (#link-google)
    - [Merge Facebook] (#merge-facebook)
    - [Merge Google] (#merge-google)
- [Requirements] (#requirements)
- [Installation] (#installation)

## API Documentation

The base address to join the dev API is : https://nbyapi.mo-bergeron.com

###Error Messages
----
  The following error messages can be encountered when calling any route.
  
* **Error Response**

  * **Code:** 400 BAD REQUEST
  * **Content:** `{"error" : "Bad Request"}`
  * **Meaning:** Something went wrong in your request. Usually a validation error. Specified on each route.
  
  OR
  
  * **Code:** 401 UNAUTHORIZED
  * **Content:** `{"error" : "Unauthorized"}`
  * **Meaning:** Your Basic authorization was refused.

  OR
  
  * **Code:** 404 NOT FOUND
  * **Content:** `{"error" : "Not Found"}`
  * **Meaning:** The requested route does not exist.

  OR
  
  * **Code:** 405 METHOD NOT ALLOWED
  * **Content:** `{"error" : "Method Not Allowed"}`
  * **Meaning:** The method used on request is not allowed to this route.

  OR
  
  * **Code:** 410 GONE
  * **Content:** `{"error" : "Gone"}`
  * **Meaning:** Your Nearby account has been disabled. Login to enable it again.

  OR
  
  * **Code:** 500 INTERNAL SERVER ERROR
  * **Content:** `{"error" : "Internal Server Error"}`
  * **Meaning:** Something went wrong in the server. Sorry about that.<br />

##GET
###Get a Spotted
----
  This is the call to get a Spotted message.

* **URL**

  /v1/spotted/{spottedId}

* **Method**
  
  `GET`
  
*  **URL Params**

    None

*  **Headers Params**

  **Required:**
  
  `Service-Provider: Facebook OR Google OR Guest`
  
  `Authorization: Basic {Base64 of ID:token}`

* **Data Params**

    None

* **Success Response**
  
  * **Code:** 200 OK
  * **Content:** 
```json
{
   "_id":"58a8dac79cfcc62fc0a94883",
   "creationDate":"2017-02-18T23:37:43.690000+00:00",
   "userId":"58a6044be66036180128f034",
   "pictureURL":null,
   "location":{
      "type":"Point",
      "coordinates":[
         45.5578415,
         -73.5515155
      ]
   },
   "message":"Y0l0",
   "fullName":"Marc Grenier",
   "profilePictureURL":"https://scontent.xx.fbcdn.net/v/t1.0-1/p50x50/15822655_10154966769969571_1156185999583138092_n.jpg?oh=9b6519cd03d8ca97e10538623fb19d95&oe=593BF8D9"
}
```
  * **Meaning:** A spotted object is returned.
 
* **Error Response**

  * **Code:** 400 BAD REQUEST
  * **Content:** `{"error" : "Bad Request"}`
  * **Meaning:** The {spottedId} was not UUID validated.

  OR

  * **Code:** 404 NOT FOUND
  * **Content:** `{"error" : "Not Found"}`
  * **Meaning:** The requested Spotted was not found.

###Get Spotteds
----
  This is the call to get Spotted messages.

* **URL**

  /v1/spotteds

* **Method**
  
  `GET`
  
*  **URL Params**

  **Required:**

  `minLat=[float]`

  `maxLat=[float]`
  
  `minLong=[float]`
  
  `maxLong=[float]`
  
  `locationOnly=[boolean]`

*  **Headers Params**

  **Required:**
  
  `Service-Provider: Facebook OR Google OR Guest`
  
  `Authorization: Basic {Base64 of ID:token}`

* **Data Params**

    None

* **Success Response**
  
  * **Code:** 200 OK
  * **Content:** 
```json
// Note userId is null when anonym is True
[{
    "_id": "58a6267ce66036254c9518f8",
    "userId": "58a6044be66036180128f034",
    "anonymity": false,
    "location": {
        "type": "Point",
        "coordinates": [
            70,
            70
        ]
    },
    "creationDate": "2017-02-17T05:05:16.930000+00:00",
    "message": "Lorem Ipsum1"
}, {
    "_id": "58a6267ce66036254c9518f8",
    "userId": "None",
    "anonymity": true,
    "location": {
        "type": "Point",
        "coordinates": [
            70,
            70
        ]
    },
    "creationDate": "2017-02-17T05:05:16.930000+00:00",
    "pictureURL": "https://s3.ca-central-1.amazonaws.com/spottednearby/41c8f63a-3f61-44d1-9d7a-ff3638f6c292.jpg",
    "message": "Lorem Ipsum2"
}]
```

```json
// locationOnly is True
[{
    "_id": "58a6267ce66036254c9518f8",
    "creationDate":"2017-02-18T23:37:43.690000+00:00",
    "location": {
        "type": "Point",
        "coordinates": [
            70,
            70
        ]
    },
}, {
    "_id": "58a6267ce66036254c9518f8",
    "creationDate":"2017-02-18T23:37:43.690000+00:00",
    "location": {
        "type": "Point",
        "coordinates": [
            70,
            70
        ]
    },
}]
```
  * **Meaning:** A list of spotted object is returned.
 
* **Error Response**

  * **Code:** 400 BAD REQUEST
  * **Content:** `{"error" : "Bad Request"}`
  * **Meaning:** Validation error.

###Get my Spotteds
----
  This is the call to get my Spotted messages.

* **URL**

  /v1/spotted/me

* **Method**
  
  `GET`
  
*  **URL Params**

  **Optional:**

  `skip=[integer]`

  `since=[date '%Y-%m-%d %H:%M:%S']`

*  **Headers Params**

  **Required:**
  
  `Service-Provider: Facebook OR Google`
  
  `Authorization: Basic {Base64 of ID:token}`

* **Data Params**

    None

* **Success Response**
  
  * **Code:** 200 OK
  * **Content:** 
```json
[{
    "_id": "58a6267ce66036254c9518f8",
    "userId": "58a6044be66036180128f034",
    "anonymity": false,
    "location": {
        "type": "Point",
        "coordinates": [
            70,
            70
        ]
    },
    "creationDate": "2017-02-17T05:05:16.930000+00:00",
    "pictureURL": "https://s3.ca-central-1.amazonaws.com/spottednearby/41c8f63a-3f61-44d1-9d7a-ff3638f6c292.jpg",
    "message": "Lorem Ipsum1"
}, {
    "_id": "58a6267ce66036254c9518f8",
    "userId": "58a6044be66036180128f034",
    "anonymity": true,
    "location": {
        "type": "Point",
        "coordinates": [
            70,
            70
        ]
    },
    "creationDate": "2017-02-17T05:05:16.930000+00:00",
    "pictureURL": "https://s3.ca-central-1.amazonaws.com/spottednearby/41c8f63a-3f61-44d1-9d7a-ff3638f6c292.jpg",
    "message": "Lorem Ipsum2"
}]
```
  * **Meaning:** A list of spotted object is returned.
 
* **Error Response**

  * **Code:** 400 BAD REQUEST
  * **Content:** `{"error" : "Bad Request"}`
  * **Meaning:** The {spottedId} was not UUID validated.

  OR

  * **Code:** 404 NOT FOUND
  * **Content:** `{"error" : "Not Found"}`
  * **Meaning:** The requested Spotted was not found.

###Get Spotteds by user ID
----
  This is the call to get Spotted messages with a user ID.

* **URL**

  /v1/spotteds/{userId}

* **Method**
  
  `GET`
  
*  **URL Params**

    None

*  **Headers Params**

  **Required:**
  
  `Service-Provider: Facebook OR Google`
  
  `Authorization: Basic {Base64 of ID:token}`

* **Data Params**

    None

* **Success Response**
  
  * **Code:** 200 OK
  * **Content:** 
```json
// Note userId is null when anonym is True
[{
    "_id": "58a6267ce66036254c9518f8",
    "userId": "58a6044be66036180128f034",
    "anonymity": false,
    "location": {
        "type": "Point",
        "coordinates": [
            70,
            70
        ]
    },
    "creationDate": "2017-02-17T05:05:16.930000+00:00",
    "pictureURL": "https://s3.ca-central-1.amazonaws.com/spottednearby/41c8f63a-3f61-44d1-9d7a-ff3638f6c292.jpg",
    "message": "Lorem Ipsum1"
}, {
    "_id": "58a6267ce66036254c9518f8",
    "userId": null,
    "anonymity": true,
    "location": {
        "type": "Point",
        "coordinates": [
            70,
            70
        ]
    },
    "creationDate": "2017-02-17T05:05:16.930000+00:00",
    "pictureURL": "https://s3.ca-central-1.amazonaws.com/spottednearby/41c8f63a-3f61-44d1-9d7a-ff3638f6c292.jpg",
    "message": "Lorem Ipsum2"
}]
```
  * **Meaning:** A list of spotted object is returned.
 
* **Error Response**

  * **Code:** 400 BAD REQUEST
  * **Content:** `{"error" : "Bad Request"}`
  * **Meaning:** The {userId} was not UUID validated.
  
###Get a User
----
  This is the call to get a User.

* **URL**

  /v1/user/{userId}

* **Method**
  
  `GET`
  
*  **URL Params**

    None

*  **Headers Params**

  **Required:**
  
  `Service-Provider: Facebook OR Google`
  
  `Authorization: Basic {Base64 of ID:token}`

* **Data Params**

    None

* **Success Response**
  
  * **Code:** 200 OK
  * **Content:** 
```json
{
   "_id":"58a8dac79cfcc62fc0a94883",
   "fullName":"Marc Grenier",
   "profilePictureURL":"https://scontent.xx.fbcdn.net/v/t1.0-1/p50x50/15822655_10154966769969571_1156185999583138092_n.jpg?oh=9b6519cd03d8ca97e10538623fb19d95&oe=593BF8D9"
}
```
  * **Meaning:** A user object is returned.
 
* **Error Response**

  * **Code:** 400 BAD REQUEST
  * **Content:** `{"error" : "Bad Request"}`
  * **Meaning:** The {userId} was not ObjectId validated.

  OR

  * **Code:** 404 NOT FOUND
  * **Content:** `{"error" : "Not Found"}`
  * **Meaning:** The {userId} was not found.

###Get my User
----
  This is the call to get my User.

* **URL**

  /v1/user/me

* **Method**
  
  `GET`
  
*  **URL Params**

    None

*  **Headers Params**

  **Required:**
  
  `Service-Provider: Facebook OR Google`
  
  `Authorization: Basic {Base64 of ID:token}`

* **Data Params**

    None

* **Success Response**
  
  * **Code:** 200 OK
  * **Content:** 
```json
{
   "_id":"58a8dac79cfcc62fc0a94883",
   "creationDate":"2017-02-18T23:37:43.690000+00:00",
   "disabled":false,
   "facebookId":"58a6044be66036180128f034",
   "facebookDate":"2017-02-18T23:37:43.690000+00:00",
   "googleId":"58a6044be66036180128f034",
   "googleDate":"2017-02-18T23:37:43.690000+00:00",
   "fullName":"Marc Grenier",
   "profilePictureURL":"https://scontent.xx.fbcdn.net/v/t1.0-1/p50x50/15822655_10154966769969571_1156185999583138092_n.jpg?oh=9b6519cd03d8ca97e10538623fb19d95&oe=593BF8D9"
}
```
  * **Meaning:** A user object is returned.
 
* **Error Response**

  * **Code:** 400 BAD REQUEST
  * **Content:** `{"error" : "Bad Request"}`
  * **Meaning:** The {userId} was not ObjectId validated.

  OR

  * **Code:** 404 NOT FOUND
  * **Content:** `{"error" : "Not Found"}`
  * **Meaning:** The {userId} was not found.

##POST
###Create Account and Authentication
----
  This is the main call to be able to authenticate with the API.

* **URL**

  /v1/login/

* **Method**
  
  `POST`
  
*  **URL Params**

   None

*  **Headers Params**

  **Required:**
  
  `Service-Provider: Facebook OR Google`
  
  `Authorization: Basic {Base64 of ID:token}`

* **Data Params**

  None

* **Success Response**
  
  * **Code:** 201 CREATED
  * **Content:** `{"result": "Created"}`
  * **Meaning:** A new account has been created and the login was successful
  
  OR
  
  * **Code:** 200 OK
  * **Content:** `{"result": "OK"}`
  * **Meaning:** The account already existed and the login was successful
 
* **Error Response**

  * **Code:** 400 BAD REQUEST
  * **Content:** `{"error" : "Bad Request"}`
  * **Meaning:** Not supposed to happen

###Create a Spotted
----
  This is the call to create a new Spotted message.

* **URL**

  /v1/spotted

* **Method**
  
  `POST`
  
*  **URL Params**

    None

*  **Headers Params**

  **Required:**
  
  `Service-Provider: Facebook OR Google`
  
  `Authorization: Basic {Base64 of ID:token}`

* **Data Params**

   **Required:**
   
   `anonymity=[boolean]`
   
   `longitude=[float]`
   
   `latitude=[float]`
   
   `message=[string]`
   
   **Optional:**
   
   `picture=[file]`

* **Success Response**
  
  * **Code:** 201 CREATED
  * **Content:** `{"result" : "fe127933-f9fa-4189-b0e3-1ebb828c1714"}`
  * **Meaning:** A Spotted has been created. The result is the Spotted ID.
 
* **Error Response**

  * **Code:** 400 BAD REQUEST
  * **Content:** `{"error" : "Bad Request"}`
  * **Meaning:** The form wasn't valid OR your user wasn't found in the database.
  
###Disable Account
----
  This is the call to disable your account.

* **URL**

  /v1/disable/

* **Method**
  
  `POST`
  
*  **URL Params**

   None

*  **Headers Params**

  **Required:**
  
  `Service-Provider: Facebook OR Google`
  
  `Authorization: Basic {Base64 of ID:token}`

* **Data Params**

  None

* **Success Response**
  
  * **Code:** 200 OK
  * **Content:** `{"result": "OK"}`
  * **Meaning:** The account was successfully disabled.
 
* **Error Response**
  
  * **Code:** 400 BAD REQUEST
  * **Content:** `{"result": "Bad Request"}`
  * **Meaning:** The account was not successfully disabled.

###Link Facebook
----
  This is the call to link a Facebook to an existing Nearby account linked with Google

* **URL**

  /v1/link/facebook

* **Method**
  
  `POST`
  
*  **URL Params**

   None

*  **Headers Params**

  **Required:**
  
  `Service-Provider: Google`
  
  `Authorization: Basic {Base64 of ID:token}`

* **Data Params**

   **Required:**
   
   `facebookId=[string]`
   
   `token=[string]`

* **Success Response**
  
  * **Code:** 200 OK
  * **Content:** `{"result": "OK"}`
  * **Meaning:** Facebook account was successfully linked to Nearby account.
 
* **Error Response**

  * **Code:** 400 BAD REQUEST
  * **Content:** `{"error" : "Bad Request"}`
  * **Meaning:** Validation error.

  OR

  * **Code:** 401 UNAUTHORIZED
  * **Content:** `{"error" : "Unauthorized"}`
  * **Meaning:** Couldn't authenticate the Facebook ID with Facebook token.

  OR

  * **Code:** 403 FORBIDDEN
  * **Content:** `{"error" : "Forbidden"}`
  * **Meaning:** That Facebook account already exists in Nearby system OR that Nearby account is already linked to a Facebook account. It can't be linked.

###Link Google
----
  This is the call to link a Google to an existing Nearby account linked with Facebook

* **URL**

  /v1/link/facebook

* **Method**
  
  `POST`
  
*  **URL Params**

   None

*  **Headers Params**

  **Required:**
  
  `Service-Provider: Facebook`
  
  `Authorization: Basic {Base64 of ID:token}`

* **Data Params**

   **Required:**
   
   `googleId=[string]`
   
   `token=[string]`

* **Success Response**
  
  * **Code:** 200 OK
  * **Content:** `{"result": "OK"}`
  * **Meaning:** Google account was successfully linked to Nearby account.
 
* **Error Response**

  * **Code:** 400 BAD REQUEST
  * **Content:** `{"error" : "Bad Request"}`
  * **Meaning:** Validation error.

  OR

  * **Code:** 401 UNAUTHORIZED
  * **Content:** `{"error" : "Unauthorized"}`
  * **Meaning:** Couldn't authenticate the Google ID with Google token.

  OR

  * **Code:** 403 FORBIDDEN
  * **Content:** `{"error" : "Forbidden"}`
  * **Meaning:** That Google account already exists in Nearby system OR that Nearby account is already linked to a Google account. It can't be linked.

###Merge Facebook
----
  This is the call to merge an existing Facebook Nearby account to an existing Google Nearby account.

* **URL**

  /v1/merge/facebook

* **Method**
  
  `POST`
  
*  **URL Params**

   None

*  **Headers Params**

  **Required:**
  
  `Service-Provider: Google`
  
  `Authorization: Basic {Base64 of ID:token}`

* **Data Params**

   **Required:**
   
   `facebookId=[string]`
   
   `token=[string]`

* **Success Response**
  
  * **Code:** 200 OK
  * **Content:** `{"result": "OK"}`
  * **Meaning:** Facebook Nearby account was successfully merged to Google Nearby account.
 
* **Error Response**

  * **Code:** 400 BAD REQUEST
  * **Content:** `{"error" : "Bad Request"}`
  * **Meaning:** Validation error.

  OR

  * **Code:** 401 UNAUTHORIZED
  * **Content:** `{"error" : "Unauthorized"}`
  * **Meaning:** The provided Facebook ID and token aren't valid.

  OR

  * **Code:** 404 NOT FOUND
  * **Content:** `{"error" : "Not Found"}`
  * **Meaning:** There is no Facebook Nearby account with that Facebook ID

###Merge Google
----
  This is the call to merge an existing Google Nearby account to an existing Facebook Nearby account.

* **URL**

  /v1/merge/google

* **Method**
  
  `POST`
  
*  **URL Params**

   None

*  **Headers Params**

  **Required:**
  
  `Service-Provider: Facebook`
  
  `Authorization: Basic {Base64 of ID:token}`

* **Data Params**

   **Required:**
   
   `googleId=[string]`
   
   `token=[string]`

* **Success Response**
  
  * **Code:** 200 OK
  * **Content:** `{"result": "OK"}`
  * **Meaning:** Google Nearby account was successfully merged to Facebook Nearby account.
 
* **Error Response**

  * **Code:** 400 BAD REQUEST
  * **Content:** `{"error" : "Bad Request"}`
  * **Meaning:** Validation error.

  OR

  * **Code:** 401 UNAUTHORIZED
  * **Content:** `{"error" : "Unauthorized"}`
  * **Meaning:** The provided Google ID and token aren't valid.

  OR

  * **Code:** 404 NOT FOUND
  * **Content:** `{"error" : "Not Found"}`
  * **Meaning:** There is no Google Nearby account with that Google ID

  
## Requirements
* Python 2.7
* Flask 0.12
* Flask-WTF 0.14
* boto3 1.4.4
* python-pymongo 3.4.0

## Installation
First, you have to install python 2.7. It is quite easy depending on your OS.

Then, run the following command to install dependencies : 
`pip install flask flask-wtf flask-pymongo flask-cors google-api-python-client boto`

Make `run.py` executable with `chmod +x run.py`.

`TO BE COMPLETED`

P.S : You won't be able to run the server on production since you are missing important keys that are not in the repository.
