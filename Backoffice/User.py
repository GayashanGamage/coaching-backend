# this is for all user account authontication things

from fastapi import APIRouter
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from .Schemas import UserAuth, User, UserEmail, VerificationCode, PasswordReset
from fastapi.responses import JSONResponse
from Auth import *
from random import randint
from datetime import datetime
from Email import *


load_dotenv()
mongo = MongoClient(os.getenv('mongo'))
db = mongo['consult']
admin = db['admin']

auth = APIRouter()

# ------------------------------
# endpoints
# user login - admin


@auth.post('/admin-login', tags=['backoffice-user'])
async def login(user: UserAuth):
    userDetails = admin.find_one({'username': user.username})
    if userDetails != None:
        # get verified password as : bool
        verify_password = verifyPassword(
            user.password, userDetails["password"])

        if verify_password == True:
            # if userDetails['password'] == user.password:
            jwtToken = encodeJWT(os.getenv('adminJWT'), {
                                 'name': user.username})
            return JSONResponse(status_code=200, content={'message': 'sucssesfull', 'token': jwtToken})
        else:
            return JSONResponse(status_code=403, content={'error': 'details are not mach'})
    else:
        return JSONResponse(status_code=404, content={'error': 'email not found'})

# user password change - admin


@auth.patch('/admin-password-reset', tags=['backoffice-user'])
async def passwordReset(passwordReset: PasswordReset):
    userDetails = admin.find_one({"email": passwordReset.email})
    # get hashed password
    hashed_password = hashPassword(passwordReset.password)

    if userDetails == None or userDetails["password_changable"] == False:
        return JSONResponse(status_code=400, content={"error": "not allowed"})
    elif userDetails["password_changable"] == True:
        secreteKeyCount = len(userDetails['validation_key'])
        admin.update_one({"email": userDetails["email"]}, {
                         '$set': {"password": hashed_password, "password_changable": False, f"validation_key.{secreteKeyCount-1}.availability": False}})
        return JSONResponse(status_code=200, content={"message": "sucsessfull"})


# get verification code - admin
# email should contain inside of jwt


@auth.patch('/admin-code-send', tags=['backoffice-user'])
async def verificationCodeSend(user: UserEmail):
    userDetails = admin.find_one({'email': user.email})
    if userDetails != None:
        # set new scret code and setup time
        newData = {'code': randint(
            1000, 9999), 'time': datetime.now(), 'availability': True}
        mailData = {'to': {'name': userDetails['firstName'], 'email': userDetails['email']}, 'params': {
            'code': newData['code']}, 'template': 3, 'subject': 'reset password'}
        if 'validation_key' in userDetails and len(userDetails['validation_key']) < 3:
            # send email
            send_email = sendEmail(mailData)
            if send_email['mail_id'] == None:
                return JSONResponse(status_code=400, content={'error': 'email canot send'})

            newData['email'] = send_email
            # update database
            admin.update_one({'email': userDetails['email']}, {
                             '$push': {'validation_key': newData}})

        elif 'validation_key' in userDetails and len(userDetails['validation_key']) == 3:
            # calculating mail sending time gap
            timeGap = int((datetime.now() - datetime.fromisoformat(
                str(userDetails['validation_key'][0]['time']))).total_seconds())
            if timeGap > 120:
                # send email
                send_email = sendEmail(mailData)
                if send_email['mail_id'] == None:
                    return JSONResponse(status_code=400, content={'error': 'email canot send'})

                newData['email'] = send_email
                # add new secrete key
                admin.update_one({'email': userDetails['email']}, {
                                 '$push': {'validation_key': newData}})
                # remove first secrete key
                admin.update_one({'email': userDetails['email']}, {
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
            admin.update_one({'email': userDetails['email']}, {
                             '$set': {'validation_key': [newData]}})

        # if secrete code store sucsessfull
        return JSONResponse(status_code=200, content={'message': 'sucsessfull transaction'})
    else:
        # if not secrete code store
        return JSONResponse(status_code=404, content={'message': 'email cannot find'})

# verify secrete code


@auth.post('/admin-code-verification', tags=['backoffice-user'])
async def codeVerification(verificationCode: VerificationCode):
    userDetails = admin.find_one({"email": verificationCode.email})
    if userDetails != None and userDetails["validation_key"][-1]["code"] == verificationCode.code:
        admin.update_one({'email': verificationCode.email}, {
                         '$set': {"password_changable": True}})
        return JSONResponse(status_code=200, content={'message': 'sucsusfull'})
    elif userDetails != None and userDetails["validation_key"][-1]["code"] != verificationCode.code:
        return JSONResponse(status_code=400, content={"error": "key not valied"})
    else:
        return JSONResponse(status_code=400, content={"error": "not allowed"})

# -----------------------------
