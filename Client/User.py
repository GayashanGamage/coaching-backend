# this is for all user account related things
# create new account and authonticate

from fastapi import APIRouter
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from .Schemas import User, UserBasics
from fastapi.responses import JSONResponse
from Auth import *
from random import randint
from datetime import datetime
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from Email import *

# brevo configuration
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = os.getenv('brevo')
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
    sib_api_v3_sdk.ApiClient(configuration))

# mongodb configuration
load_dotenv()
mongo = MongoClient(os.getenv('mongo'))
db = mongo['consult']
userdb = db['user']

auth = APIRouter()

# login for user


@auth.post('/login', tags=['client-user'])
async def login(user: User):
    userDetails = userdb.find_one({'email': user.email})
    if userDetails != None:
        # get verified password as : bool
        verify_password = verifyPassword(
            user.password, userDetails["password"])

        if verify_password == True:
            # if userDetails['password'] == user.password:
            jwtToken = encodeJWT(os.getenv('adminJWT'), {
                                 'name': user.email})
            return JSONResponse(status_code=200, content={'message': 'sucssesfull', 'token': jwtToken})
        else:
            return JSONResponse(status_code=403, content={'error': 'details are not mach'})
    else:
        return JSONResponse(status_code=404, content={'error': 'email not found'})

# change passwrod


@auth.post('/password-reset', tags=['client-user'])
async def passwordReset():
    pass

# get verification code for


@auth.post('/verification-code', tags=['client-user'])
async def verificationCode():
    pass

# create a new use account


@auth.post('/register', tags=['client-user'])
async def register(user: UserBasics):
    userDetails = userdb.find_one({"email": user.email})
    if userDetails == None:
        mailData = {'to': [{"name": user.firstName, "email": user.email}], 'subject': "welcome to Dfernando.com", "params": {
            "username": user.firstName}, "template": 4}
        hash_password = hashPassword(user.password)
        try:
            userdb.insert_one({"email": user.email, "fistName": user.firstName,
                               "lastName": user.lastName, "password": hash_password})
            welcomeEmail(mailData)
            return JSONResponse(status_code=201, content={"message": "sucsessfull"})
        except:
            return JSONResponse(status_code=400, content={"error": "something whent wrong"})
    else:
        print(userDetails)
        return JSONResponse(status_code=400, content={"error": "email exist"})
