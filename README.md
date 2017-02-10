# Nearby-API

###Contents
- [API Documentation] (#api-documentation)
  - GET
  - POST
    - [Authentication] (#authentication)
    - [Create a spotted] (#create-a-spotted)

## API Documentation

The base address to join the dev API is : https://nbyapi.mo-bergeron.com

###Authentication
----
  This is the main call to be able to authenticate with the API.

* **URL**

  /v1/login/

* **Method:**
  
  `POST`
  
*  **URL Params**

   None

*  **Headers Params**

  **Required**:
  
  `service-provider=Facebook / Google`
  
  `Authorization=Your Basic Auth token`

* **Data Params**

  None

* **Success Response:**
  
  * **Code:** 201 <br />
    **Content:** `CREATED`
  
  OR
  
  * **Code:** 200 <br />
    **Content:** `OK`
 
* **Error Response:**

  * **Code:** 401 UNAUTHORIZED <br />
    **Content:** TODO

  OR
  
  * **Code:** 404 NOT FOUND <br />
    **Content:** TODO

* **Sample Call:**

  TODO

* **Notes:**

  None 
  

###Create a Spotted
----
  This is the call to create a new Spotted message.

* **URL**

  /v1/spotted

* **Method:**
  
  `POST`
  
*  **URL Params**

   **Required**:
   
   `anonimity=[boolean]`
   `longitude=[float]`
   `latitude=[float]`
   `message=[string]`
   `picture=[url]`

*  **Headers Params**

  **Required**:
  
  `service-provider=Facebook / Google`
  
  `Authorization=Your Basic Auth token`

* **Data Params**

  None

* **Success Response:**
  
  * **Code:** 201 <br />
    **Content:** `{"spottedId" : "fe127933-f9fa-4189-b0e3-1ebb828c1714"}`
 
* **Error Response:**

  * **Code:** 401 UNAUTHORIZED <br />
    **Content:** TODO

  OR
  
  * **Code:** 400 BAD REQUEST <br />
    **Content:** TODO
    
  OR
  
  * **Code:** 404 NOT FOUND <br />
    **Content:** TODO

* **Sample Call:**

  TODO

* **Notes:**

  None 



## Requirements
* Python 2.7
* Flask 0.12
* Flask-WTF 0.14
* Flask-Script 0.4.0
* boto3 1.4.4

## Installation
First, you have to install python 2.7. It is quite easy depending on your OS.

Then, run the following command to install dependencies : 
`pip install flask flask-wtf flask-script boto3`

Make `run.sh` executable with `chmod +x run.sh`.

Once this is done, you can either install or not DynamoDB by executing the following `./run.py install`. If not, download it by yourself and unzip it in `instance/dynamodb/` for the server to work.

After all of this, you are ready to run the server with `./run.py runserver -e dev -d local` which runs the server with the development environment and starts DynamoDB locally

P.S : You won't be able to run the server on production since you are missing important keys that are not in the repository.
