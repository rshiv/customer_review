from fastapi import FastAPI, Response, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import jwt
import psycopg2
from dotenv import load_dotenv
import os
<<<<<<< HEAD
import json
from pydantic import BaseModel
import requests
import time

=======
>>>>>>> main

load_dotenv()  # Load environment variables from .env file

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
<<<<<<< HEAD
    allow_origins="*",  # Allows all origins in the list
=======
    allow_origins='*',
>>>>>>> main
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

<<<<<<< HEAD

@app.get("/api/check-auth")
async def check_auth(request: Request):
    # Logic to check if the user is authorized
    # For demonstration, this will just return False
    conn_string = f"dbname='{DB_NAME}' user='{DB_USER}' host='{DB_HOST}' password='{DB_PASSWORD}' port='{DB_PORT}'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    account_id = request.query_params.get("account_id")
    user_id = request.query_params.get("user_id")

    check_user_query = (
        """select * from oauth_tokens where user_id like %s and account like %s"""
    )
    cursor.execute(
        check_user_query,
        (user_id, account_id),
    )
    user = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    if user == None:
        return {"isAuthorized": False}

    return {"isAuthorized": True}


@app.get("/api/start-oauth")
async def start_oauth(request: Request):
    account_id = request.query_params.get("account_id")
    client_id = "68dc9f855ea0af1443581fec28195802"
    redirect_uri = (
        "https://d8443-service-21188800-a4e43a24.us.monday.app/api/oauth-callback"
    )
    state_value = account_id
    oauth_url = f"https://auth.monday.com/oauth2/authorize?client_id={client_id}&redirect_uri={redirect_uri}&state={state_value}"
    print("Redirecting to:", oauth_url)
    return RedirectResponse(oauth_url)


=======
@app.get("/api/check-auth")
async def check_auth(request: Request, user_id: str):
    return {"isAuthorized": False}

@app.get("/api/start-oauth")
async def start_oauth(request: Request):
    account_id = request.query_params.get('account_id')
    client_id = '68dc9f855ea0af1443581fec28195802'
    redirect_uri = 'https://d8443-service-21188800-a4e43a24.us.monday.app/api/oauth-callback'
    state_value = account_id 
    oauth_url = f"https://auth.monday.com/oauth2/authorize?client_id={client_id}&redirect_uri={redirect_uri}&state={state_value}"
    print("Redirecting to:", oauth_url)
    return RedirectResponse(oauth_url)

>>>>>>> main
def decode_jwt(token):
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded
    except (jwt.DecodeError, jwt.ExpiredSignatureError):
        return None

<<<<<<< HEAD

def store_oauth_details(user_id, access_token, account_id):
    conn_string = f"dbname='{DB_NAME}' user='{DB_USER}' host='{DB_HOST}' password='{DB_PASSWORD}' port='{DB_PORT}'"

    try:
        # Connect to your PostgreSQL database
        conn = psycopg2.connect(conn_string)

        # Create a cursor object
        cursor = conn.cursor()

        # SQL query to insert data
        query = """
        INSERT INTO oauth_tokens (user_id, access_token, account_id) 
        VALUES (%s, %s, %s);
        """

        # Execute the SQL command
        cursor.execute(query, (user_id, access_token, account_id))

        # Commit the changes to the database
        conn.commit()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        print("OAuth details stored successfully.")
    except Exception as e:
        print(f"An error occurred while storing OAuth details: {e}")


@app.get("/api/oauth-callback")
async def oauth_callback(request: Request, code: str):
    state = request.query_params.get("state")
    token_url = "https://auth.monday.com/oauth2/token"
    client_id = "68dc9f855ea0af1443581fec28195802"
    client_secret = "b11ccbfef8f820add6a95082f3306af4"
    redirect_uri = (
        "https://d8443-service-21188800-a4e43a24.us.monday.app/api/oauth-callback"
    )

    payload = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": redirect_uri,
    }

    response = requests.post(token_url, data=payload)
    token_data = response.json()

    access_token = token_data.get("access_token")

    decoded_token = decode_jwt(access_token) if access_token else None
    user_id = decoded_token.get("uid") if decoded_token else None

    store_oauth_details(user_id, access_token, state)

    return {"status": "success", "message": "Authentication successful"}


class ItemData(BaseModel):
    account_id: str
    board_id: str
    item_id: str
    user_id: str
    till_snooze: int


shortestTime = 9999999999


@app.post("/api/snoozeitem")
async def snooze_item(request: ItemData):

    conn_string = f"dbname='{DB_NAME}' user='{DB_USER}' host='{DB_HOST}' password='{DB_PASSWORD}' port='{DB_PORT}'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    # getting access token
    access_token_query = """select access_token from oauth_tokens where user_id like %s and account_id like %s"""
    cursor.execute(
        access_token_query,
        (
            request.user_id,
            request.account_id,
        ),
    )

    access_token = cursor.fetchone()
    access_token = access_token[0]
    # archive item
    # archive_query = f"mutation {{ archive_item (item_id: {request.item_id}) {{ id }} }}"
    # url = "https://api.monday.com/v2"
    # headers = {"Content-Type": "application/json", "Authorization": access_token}
    # payload = {"query": archive_query}
    # requests.post(url, json=payload, headers=headers)
    # add logic to handle archive fails

    # add archived item to DB
    insert_query = """INSERT INTO ITEMS (ACCOUNT_ID , BOARD_ID , ITEM_ID , USER_ID, TILL_SNOOZE) VALUES (%s, %s, %s, %s, %s)"""
    cursor.execute(
        insert_query,
        (
            request.account_id,
            request.board_id,
            request.item_id,
            request.user_id,
            request.till_snooze,
        ),
    )
    global shortestTime
    print(request.till_snooze)
    if request.till_snooze < shortestTime:
        shortestTime = request.till_snooze
        print(shortestTime)
    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "success"}


@app.get("/api/itemssnoozed")
async def get_items(request: Request):
    account_id = request.query_params.get("account_id")
    board_id = request.query_params.get("board_id")
    user_id = request.query_params.get("user_id")

    conn_string = f"dbname='{DB_NAME}' user='{DB_USER}' host='{DB_HOST}' password='{DB_PASSWORD}' port='{DB_PORT}'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    get_items_query = """select item_id,till_snooze from items where account_id like %s and board_id like %s"""
    cursor.execute(
        get_items_query,
        (
            account_id,
            board_id,
        ),
    )

    items = cursor.fetchall()

    return {"status": "success", "items": items}


class UnsnoozeItemData(BaseModel):
    account_id: str
    board_id: str
    user_id: str
    item_id: str


@app.post("/api/itemssnoozed")
async def unsnooze_onClick(request: UnsnoozeItemData):
    conn_string = f"dbname='{DB_NAME}' user='{DB_USER}' host='{DB_HOST}' password='{DB_PASSWORD}' port='{DB_PORT}'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    # getting access token
    access_token_query = """select access_token from oauth_tokens where user_id like %s and account_id like %s"""
    cursor.execute(
        access_token_query,
        (
            request.user_id,
            request.account_id,
        ),
    )
    access_token = cursor.fetchone()
    access_token = access_token[0]

    # duplicate item
    copy_item_query = f"mutation {{ duplicate_item (board_id: {request.board_id}, item_id: {request.item_id}, with_updates: true) {{ id }} }}"
    url = "https://api.monday.com/v2"
    headers = {"Content-Type": "application/json", "Authorization": access_token}
    payload = {"query": copy_item_query}
    requests.post(url, json=payload, headers=headers)

    # delete item from DB
    delete_query = """delete from items where board_id like %s and account_id like %s and item_id like %s"""
    cursor.execute(
        delete_query,
        (request.board_id, request.account_id, request.item_id),
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "success", "message": "items unsnoozed"}


def initilise():
    conn_string = f"dbname='{DB_NAME}' user='{DB_USER}' host='{DB_HOST}' password='{DB_PASSWORD}' port='{DB_PORT}'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    shortest_time_query = """select min(till_snooze) from items"""
    cursor.execute(shortest_time_query)
    shortestTime = cursor.fetchone()
    shortestTime = shortestTime[0]
    print(shortestTime)

    conn.commit()
    cursor.close()
    conn.close()


initilise()

while True:
    print("here")
    current_time_unix = int(time.time())
    if current_time_unix >= int(shortestTime):
        conn_string = f"dbname='{DB_NAME}' user='{DB_USER}' host='{DB_HOST}' password='{DB_PASSWORD}' port='{DB_PORT}'"
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        query = """select items.item_id , item.board_id,oauth_tokens.access_token,items.account_id from items inner join oauth_tokens on items.user_id = oauth_tokens.user_id and items.account_id = oauth_tokens.account_id where till_snooze<=%d"""
        cursor.execute(query, (current_time_unix))
        items = cursor.fetchall()
        for item in items:

            #duplicate item
            # copy_item_query = f"mutation {{ duplicate_item (board_id: {item[1]}, item_id: {item[0]}, with_updates: true) {{ id }} }}"
            # url = "https://api.monday.com/v2"
            # headers = {"Content-Type": "application/json", "Authorization": item[2]}
            # payload = {"query": copy_item_query}
            # requests.post(url, json=payload, headers=headers)

            # delete item from DB
            delete_query = """delete from items where board_id like %s and account_id like %s and item_id like %s"""
            cursor.execute(
                delete_query,
                (item[1], item[3], item[0]),
            )
        shortest_time_query = """select min(till_snooze) from items"""
        cursor.execute(shortest_time_query)
        shortestTime = cursor.fetchone()
        shortestTime = shortestTime[0]
        conn.commit()
        cursor.close()
        conn.close()
=======
def store_oauth_details(user_id, access_token, account_id):
    conn_string = f"dbname='{DB_NAME}' user='{DB_USER}' host='{DB_HOST}' password='{DB_PASSWORD}' port='{DB_PORT}'"
    print(conn_string)
    try:
        # Connect to your PostgreSQL database
        conn = psycopg2.connect(conn_string)
        
        # Create a cursor object
        cursor = conn.cursor()
        
        # SQL query to insert data
        query = """
        INSERT INTO oauth_tokens (user_id, access_token, account_id) 
        VALUES (%s, %s, %s);
        """
        
        # Execute the SQL command
        cursor.execute(query, (user_id, access_token, account_id))
        
        # Commit the changes to the database
        conn.commit()
        
        # Close the cursor and connection
        cursor.close()
        conn.close()

        print("OAuth details stored successfully.")
    except Exception as e:
        print(f"An error occurred while storing OAuth details: {e}")
        
@app.get("/api/oauth-callback")
async def oauth_callback(request: Request, code: str):
    state = request.query_params.get('state') 
    token_url = 'https://auth.monday.com/oauth2/token'
    client_id = '68dc9f855ea0af1443581fec28195802'
    client_secret = 'b11ccbfef8f820add6a95082f3306af4'
    redirect_uri = 'https://d8443-service-21188800-a4e43a24.us.monday.app/api/oauth-callback'
    
    payload = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'redirect_uri': redirect_uri
    }

    response = requests.post(token_url, data=payload)
    token_data = response.json()
    print(token_data)
    
    access_token = token_data.get('access_token')
    print(access_token)
    decoded_token = decode_jwt(access_token) if access_token else None
    user_id = decoded_token.get('uid') if decoded_token else None
    
    store_oauth_details(user_id, access_token, state)
    
    return {"status": "success", "message": "Authentication successful"}

>>>>>>> main
