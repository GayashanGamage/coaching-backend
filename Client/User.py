# this is for all user account related things
# create new account and authonticate

from fastapi import APIRouter
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from .Schemas import User, UserBasics, UserEmail, VerificationCode
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

maxKeyCount = 3
maxTimeGap = 120

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
async def passwordReset(user: User):
    userDetails = userdb.find_one({"email": user.email})
    if userDetails == None or userDetails["password_changable"] == False:
        return JSONResponse(status_code=400, content={"error": "not allowed"})
    elif userDetails["password_changable"] == True:
        # get hashed password
        hashed_password = hashPassword(user.password)

        secreteKeyCount = len(userDetails['validation_key'])
        userdb.update_one({"email": userDetails["email"]}, {
            '$set': {"password": hashed_password, "password_changable": False, f"validation_key.{secreteKeyCount-1}.availability": False}})
        return JSONResponse(status_code=200, content={"message": "sucsessfull"})

# send verification code by email and setup database according that


@auth.post('/verificationcode', tags=['client-user'])
async def verificationCode(userEmail: UserEmail):
    userDetails = userdb.find_one({'email': userEmail.email})
    if userDetails != None:
        # set new scret code and setup time
        newData = {'code': randint(
            1000, 9999), 'time': datetime.now(), 'availability': True}
        mailData = {'to': [{'name': userDetails['firstName'], 'email': userDetails['email']}], 'params': {
            'code': newData['code']}, 'template': 3, 'subject': 'reset password'}
        if 'validation_key' in userDetails and len(userDetails['validation_key']) < 3:
            # send email
            send_email = sendEmail(mailData)
            if send_email['mail_id'] == None:
                return JSONResponse(status_code=400, content={'error': 'email canot send'})

            newData['email'] = send_email
            # update database
            userdb.update_one({'email': userDetails['email']}, {
                '$push': {'validation_key': newData}})

        elif 'validation_key' in userDetails and len(userDetails['validation_key']) == maxKeyCount:
            # calculating mail sending time gap
            timeGap = int((datetime.now() - datetime.fromisoformat(
                str(userDetails['validation_key'][0]['time']))).total_seconds())
            if timeGap > maxTimeGap:
                # send email
                send_email = sendEmail(mailData)
                if send_email['mail_id'] == None:
                    return JSONResponse(status_code=400, content={'error': 'email canot send'})

                newData['email'] = send_email
                # add new secrete key
                userdb.update_one({'email': userDetails['email']}, {
                    '$push': {'validation_key': newData}})
                # remove first secrete key
                userdb.update_one({'email': userDetails['email']}, {
                    '$pop': {'validation_key': -1}})
            else:
                # if too many request
                return JSONResponse(status_code=400, content={'error': 'too many request send'})
        else:
            # send email
            send_email = sendEmail(mailData)
            if send_email['mail_id'] == None:
                return JSONResponse(status_code=400, content={'error': 'email canot send'})

            newData['email'] = send_email
            # update database
            userdb.update_one({'email': userDetails['email']}, {
                '$set': {'validation_key': [newData]}})

        # if secrete code store sucsessfull
        return JSONResponse(status_code=200, content={'message': 'sucsessfull transaction'})
    else:
        # if not secrete code store
        return JSONResponse(status_code=404, content={'message': 'email cannot find'})

# verify secreate code


@auth.post('/code-verification', tags=['client-user'])
async def codeVerification(verificationCode: VerificationCode):
    userDetails = userdb.find_one({"email": verificationCode.email})
    if userDetails != None and userDetails["validation_key"][-1]["code"] == verificationCode.code:
        userdb.update_one({'email': verificationCode.email}, {
            '$set': {"password_changable": True}})
        return JSONResponse(status_code=200, content={'message': 'sucsusfull'})
    elif userDetails != None and userDetails["validation_key"][-1]["code"] != verificationCode.code:
        return JSONResponse(status_code=400, content={"error": "key not valied"})
    else:
        return JSONResponse(status_code=400, content={"error": "not allowed"})


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
