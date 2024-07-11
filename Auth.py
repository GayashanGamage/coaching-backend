import os 
from jose import jwt
from dotenv import load_dotenv

load_dotenv()

def encodeJWT(secret, userData):
    return jwt.encode(userData, secret, algorithm='HS256')