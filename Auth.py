import os
from jose import jwt
from dotenv import load_dotenv
from passlib.hash import pbkdf2_sha256

load_dotenv()


def encodeJWT(secret, userData):
    return jwt.encode(userData, secret, algorithm='HS256')


# hash plain password
def hashPassword(password):
    return pbkdf2_sha256.hash(password)

# verify hashed password


def verifyPassword(password, hashedPassword):
    return pbkdf2_sha256.verify(password, hashedPassword)
