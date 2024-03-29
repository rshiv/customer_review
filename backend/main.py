from fastapi import FastAPI, Response, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import jwt
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins='*',
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

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

def decode_jwt(token):
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded
    except (jwt.DecodeError, jwt.ExpiredSignatureError):
        return None

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

