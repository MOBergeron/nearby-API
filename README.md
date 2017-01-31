# Nearby-API
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

Once this is done, you can either install or not DynamoDB by executing the following `./run.sh install`. If not, download it by yourself and unzip it in `instance/dynamodb/` for the server to work.

After all of this, you are ready to run the server with `./run.sh runserver -e dev -d local` which runs the server with the development environment and starts DynamoDB locally

P.S : You won't be able to run the server on production since you are missing important keys that are not in the repository.
