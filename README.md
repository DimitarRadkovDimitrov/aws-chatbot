# AWS Chatbot

Python script building chatbot using AWS Lex and Boto3 SDK. Chatbot fulfills service (food, cleaning, homecare, and taxi) and calls lambda function to store the collected user data.

<br>

## Prerequisites

* Update every lambda field in [chatbotAWS.py](./chatbotAWS.py) with your own lambda identifiers.
* Make sure your .aws/credentials file is up to date.
* Install project dependencies in root directory with pipenv.
    ```
    pipenv install
    ```

<br>

## Run

* Build the chatbot and hook it up to your lambda function.
    ```
    pipenv run python3 chatbotAWS.py
    ```
