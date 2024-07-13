# this is for all user account authontication things

from fastapi import APIRouter
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from .Schemas import UserAuth, User, UserEmail
from fastapi.responses import JSONResponse
from Auth import *
from random import randint
from datetime import datetime
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# brevo configuration
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = os.getenv('brevo')
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
    sib_api_v3_sdk.ApiClient(configuration))

load_dotenv()
mongo = MongoClient(os.getenv('mongo'))
db = mongo['consult']
admin = db['admin']

auth = APIRouter()

# ------------------------------
# seperated functions
# send email


def sendEmail(mailData):
    print(mailData)
    Sender = {"name": "gayashan", "email": "gayashan.randimagamage@gmail.com"}
    Headers = {"Some-Custom-Name": "unique-id-1234"}
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=mailData['to'], headers=Headers, sender=Sender, subject=mailData['subject'], params=mailData['params'], template_id=mailData['template'])
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=[{"name": "chamodi", "email": "chamodijanithya@gmail.com"}], headers={"Some-Custom-Name": "unique-id-1234"}, sender={
                                                   "name": "gayashan", "email": "gayashan.randimagamage@gmail.com"}, subject="password reset", template_id=3, params=mailData["params"])
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        return {'mail_id': api_response._message_id, 'message': 'sucsusfull'}
    except ApiException as e:
        return {'mail_id': None, 'message': 'Unsucsusfull'}


# ------------------------------
# endpoints
# user login - admin
@auth.post('/admin-login', tags=['backoffice-user'])
async def login(user: UserAuth):
    userDetails = admin.find_one({'username': user.username})
    if userDetails != None:
        if userDetails['password'] == user.password:
            jwtToken = encodeJWT(os.getenv('adminJWT'), {
                                 'name': user.username})
            return JSONResponse(status_code=200, content={'message': 'sucssesfull', 'token': jwtToken})
        else:
            return JSONResponse(status_code=403, content={'error': 'details are not mach'})
    else:
        return JSONResponse(status_code=404, content={'error': 'email not found'})

# user password change - admin


@auth.patch('/admin-password-reset', tags=['backoffice-user'])
async def passwordReset():
    pass

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


# @app.post('/admin-code-verification')
# async def codeVerification(code: VerificationCode):
#     pass

# -----------------------------
