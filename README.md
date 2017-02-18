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
  - POST
    - [Authentication] (#authentication)
    - [Create a spotted] (#create-a-spotted)
    - [Link Facebook] (#link-facebook)
    - [Link Google] (#link-google)
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
  
  * **Code:** 200
  * **Content:** 
```json
{
    "_id": "58a6267ce66036254c9518f8",
    "anonymity": true,
    "userId": "58a6044be66036180128f034",
    "location": {
        "type": "Point",
        "coordinates": [
            70,
            70
        ]
    },
    "creationDate": "2017-02-17T05:05:16.930000+00:00",
    "pictureURL": "https://s3.ca-central-1.amazonaws.com/spottednearby/41c8f63a-3f61-44d1-9d7a-ff3638f6c292.jpg",
    "message": "Lorem Ipsum"
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
  
  * **Code:** 200
  * **Content:** 
```json
[{
    "_id": "58a6267ce66036254c9518f8",
    "anonymity": true,
    "userId": "58a6044be66036180128f034",
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
    "anonymity": false,
    "userId": "58a6044be66036180128f034",
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
  * **Meaning:** Validation error.

###Get my Spotteds
----
  This is the call to get my Spotted messages.

* **URL**

  /v1/spotted/me

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
  
  * **Code:** 200
  * **Content:** 
```json
[{
    "_id": "58a6267ce66036254c9518f8",
    "anonymity": true,
    "userId": "58a6044be66036180128f034",
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
    "anonymity": false,
    "userId": "58a6044be66036180128f034",
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
  
  * **Code:** 200
  * **Content:** 
```json
[{
    "_id": "58a6267ce66036254c9518f8",
    "anonymity": true,
    "userId": "58a6044be66036180128f034",
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
    "anonymity": false,
    "userId": "58a6044be66036180128f034",
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

##POST
###Authentication
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
  
  * **Code:** 201
  * **Content:** `{"result": "Created"}`
  * **Meaning:** A new account has been created and the login was successful
  
  OR
  
  * **Code:** 200
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
  
  * **Code:** 201
  * **Content:** `{"result" : "fe127933-f9fa-4189-b0e3-1ebb828c1714"}`
  * **Meaning:** A Spotted has been created. The result is the Spotted ID.
 
* **Error Response**

  * **Code:** 400 BAD REQUEST
  * **Content:** `{"error" : "Bad Request"}`
  * **Meaning:** The form wasn't valid OR your user wasn't found in the database.

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
  
  * **Code:** 200
  * **Content:** `{"result": "OK"}`
  * **Meaning:** Facebook account was successfully linked to Nearby account.
 
* **Error Response**

  * **Code:** 400 BAD REQUEST
  * **Content:** `{"error" : "Bad Request"}`
  * **Meaning:** Validation error.

  OR

  * **Code:** 401 Unauthorized
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
  
  * **Code:** 200
  * **Content:** `{"result": "OK"}`
  * **Meaning:** Google account was successfully linked to Nearby account.
 
* **Error Response**

  * **Code:** 400 BAD REQUEST
  * **Content:** `{"error" : "Bad Request"}`
  * **Meaning:** Validation error.

  OR

  * **Code:** 401 Unauthorized
  * **Content:** `{"error" : "Unauthorized"}`
  * **Meaning:** Couldn't authenticate the Google ID with Google token.

  OR

  * **Code:** 403 FORBIDDEN
  * **Content:** `{"error" : "Forbidden"}`
  * **Meaning:** That Google account already exists in Nearby system OR that Nearby account is already linked to a Google account. It can't be linked.

## Requirements
* Python 2.7
* Flask 0.12
* Flask-WTF 0.14
* boto3 1.4.4
* python-pymongo 3.4.0

## Installation
First, you have to install python 2.7. It is quite easy depending on your OS.

Then, run the following command to install dependencies : 
`pip install flask flask-wtf flask-pymongo boto3`

Make `run.py` executable with `chmod +x run.py`.

`TO BE COMPLETED`

P.S : You won't be able to run the server on production since you are missing important keys that are not in the repository.
