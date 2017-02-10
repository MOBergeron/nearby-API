# Nearby-API

###Contents
- [API Documentation] (#api-documentation)
  - [Error Messages] (#error-messages)
  - GET
    - [Get a spotted] (#get-a-spotted)
    - [Get my Spotteds] (#get-my-spotteds)
    - [Get Spotteds by user ID] (#get-spotteds-by-user-id)
  - POST
    - [Authentication] (#authentication)
    - [Create a spotted] (#create-a-spotted)
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
  * **Meaning:** Something went wrong in your request. Specified on each route.
  
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
  
  `Service-Provider: {Facebook} OR {Google}`
  
  `Authorization: Basic {Base64 of facebookId:facebookToken}`

* **Data Params**

    None

* **Success Response**
  
  * **Code:** 200
  * **Content:** 
```json
  {
    "result": {
        "anonimity": true,
        "userId": "04d35c92-5896-4ecc-8189-449b02b40f1c",
        "geoJson": {
            "type": "Point",
            "coordinates": [
                70,
                70
            ]
        },
        "hashKey": 159990,
        "geohash": 15999003033159630343,
        "isArchived": false,
        "spottedId": "fcfb501d-e109-44a9-81cc-58e57e1ad112",
        "message": "Lorem Ipsum"
    }
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
  
  `Service-Provider: {Facebook} OR {Google}`
  
  `Authorization: Basic {Base64 of facebookId:facebookToken}`

* **Data Params**

    None

* **Success Response**
  
  * **Code:** 200
  * **Content:** 
```json
{
    "result": [{
        "anonimity": true,
        "userId": "04d35c92-5896-4ecc-8189-449b02b40f1c",
        "geoJson": {
            "type": "Point",
            "coordinates": [
                70,
                70
            ]
        },
        "hashKey": 159990,
        "geohash": 15999003033159630343,
        "isArchived": false,
        "spottedId": "fcfb501d-e109-44a9-81cc-58e57e1ad112",
        "message": "Lorem Ipsum1"
    }, {
        "anonimity": false,
        "userId": "04d35c92-5896-4ecc-8189-449b02b40f1c",
        "geoJson": {
            "type": "Point",
            "coordinates": [
                70,
                70
            ]
        },
        "hashKey": 159990,
        "geohash": 15999003033159630343,
        "isArchived": false,
        "spottedId": "fcfb501d-e109-44a9-81cc-58e57e1ad112",
        "message": "Lorem Ipsum2"
    }]
}
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
  
  `Service-Provider: {Facebook} OR {Google}`
  
  `Authorization: Basic {Base64 of facebookId:facebookToken}`

* **Data Params**

    None

* **Success Response**
  
  * **Code:** 200
  * **Content:** 
```json
{
    "result": [{
        "anonimity": true,
        "userId": "04d35c92-5896-4ecc-8189-449b02b40f1c",
        "geoJson": {
            "type": "Point",
            "coordinates": [
                70,
                70
            ]
        },
        "hashKey": 159990,
        "geohash": 15999003033159630343,
        "isArchived": false,
        "spottedId": "fcfb501d-e109-44a9-81cc-58e57e1ad112",
        "message": "Lorem Ipsum1"
    }, {
        "anonimity": false,
        "userId": "04d35c92-5896-4ecc-8189-449b02b40f1c",
        "geoJson": {
            "type": "Point",
            "coordinates": [
                70,
                70
            ]
        },
        "hashKey": 159990,
        "geohash": 15999003033159630343,
        "isArchived": false,
        "spottedId": "fcfb501d-e109-44a9-81cc-58e57e1ad112",
        "message": "Lorem Ipsum2"
    }]
}
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
  
  `Service-Provider: {Facebook} OR {Google}`
  
  `Authorization: Basic {Base64 of facebookId:facebookToken}`

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
  
  `Service-Provider: {Facebook} OR {Google}`
  
  `Authorization: Basic {Base64 of facebookId:facebookToken}`

* **Data Params**

   **Required:**
   
   `anonimity=[boolean]`
   
   `longitude=[float]`
   
   `latitude=[float]`
   
   `message=[string]`
   
   **Optional:**
   
   `picture=[url]`

* **Success Response**
  
  * **Code:** 201
  * **Content:** `{"result" : "fe127933-f9fa-4189-b0e3-1ebb828c1714"}`
  * **Meaning:** A Spotted has been created. The result is the Spotted ID.
 
* **Error Response**

  * **Code:** 400 BAD REQUEST
  * **Content:** `{"error" : "Bad Request"}`
  * **Meaning:** The form wasn't valid OR your user wasn't found in the database.

## Requirements
* Python 2.7
* Flask 0.12
* Flask-WTF 0.14
* Flask-Script 0.4.0
* boto3 1.4.4
* python-geohash 0.8.3

## Installation
First, you have to install python 2.7. It is quite easy depending on your OS.

Then, run the following command to install dependencies : 
`pip install flask flask-wtf flask-script boto3 python-geohash`

Make `run.sh` executable with `chmod +x run.sh`.

Once this is done, you can either install or not DynamoDB by executing the following `./run.py install`. If not, download it by yourself and unzip it in `instance/dynamodb/` for the server to work.

After all of this, you are ready to run the server with `./run.py runserver -e dev -d local` which runs the server with the development environment and starts DynamoDB locally

P.S : You won't be able to run the server on production since you are missing important keys that are not in the repository.
