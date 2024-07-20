import os
from jose import jwt
from dotenv import load_dotenv
from passlib.hash import pbkdf2_sha256
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
from typing import Annotated

load_dotenv()
bearer = HTTPBearer()

# encode JWT
def encodeJWT(username, secret, userData):
    return jwt.encode({'username' : username}, secret, algorithm='HS256')

# decode JWT
def decodeJWT(token):
    #TODO: there are two JWT token for client and admin
    adminSecret = os.getenv('adminJWT')
    return jwt.decode(token, adminSecret, algorithms='HS256')
    

# hash plain password
def hashPassword(password):
    return pbkdf2_sha256.hash(password)

# verify hashed password
def verifyPassword(password, hashedPassword):
    return pbkdf2_sha256.verify(password, hashedPassword)

# verify authontication
def authVerification(auth : Annotated[HTTPAuthorizationCredentials, Depends(bearer)]):
    return decodeJWT(auth.credentials)