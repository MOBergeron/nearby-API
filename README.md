# Nearby-API

###Contents
- [API Documentation] (#api-documentation)
  - GET
  - POST
    - [Error Messages] (#error-messages)
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

  * **Code:** 400 BAD REQUEST <br />
    **Content:** `{"error" : "Bad Request"}`
    **Meaning:** Something went wrong in your request. Specified on each route. <br />
  
  OR
  
  * **Code:** 401 UNAUTHORIZED <br />
    **Content:** `{"error" : "Unauthorized"}`
    **Meaning:** Your Basic authorization was refused. <br />

  OR
  
  * **Code:** 404 NOT FOUND <br />
    **Content:** `{"error" : "Not found"}`
    **Meaning:** The requested route does not exist. <br />

  OR
  
  * **Code:** 405 METHOD NOT ALLOWED <br />
    **Content:** `{"error" : "Method Not Allowed"}`
    **Meaning:** The method used on request is not allowed to this route. <br />

  OR
  
  * **Code:** 500 INTERNAL SERVER ERROR <br />
    **Content:** `{"error" : "Internal Server Error"}`
    **Meaning:** Something went wrong in the server. Sorry about that.<br />

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
  
  * **Code:** 201 <br />
    **Content:** `{"result": "Created"}`
    **Meaning:** A new account has been created and the login was successful <br />
  
  OR
  
  * **Code:** 200 <br />
    **Content:** `{"result": "OK"}`
    **Meaning:** The account already existed and the login was successful <br />
 
* **Error Response**

  * **Code:** 400 BAD REQUEST <br />
    **Content:** `{"error" : "Bad Request"}`
    **Meaning:** Not supposed to happen <br />

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
  
  * **Code:** 201 <br />
    **Content:** `{"result" : "fe127933-f9fa-4189-b0e3-1ebb828c1714"}`
    **Meaning:** A Spotted hash been created. The result is the Spotted ID. <br />
 
* **Error Response**

  * **Code:** 400 BAD REQUEST <br />
    **Content:** `{"error" : "Bad Request"}`
    **Meaning:** The form wasn't valid OR your user wasn't found in the database. <br />

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
