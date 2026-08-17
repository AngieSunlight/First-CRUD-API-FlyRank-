import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def sign_up_user(email, password):
    data = supabase.auth.sign_up({"email": email, "password": password})
    return data

def login(email, password):
    data = supabase.auth.sign_in_with_password({"email": email, "password": password})
    return data

def getUser_Token(token):
    response = supabase.auth.get_user(token)
    return response

if __name__ == "__main__":
    print("Supabase client created:", supabase)