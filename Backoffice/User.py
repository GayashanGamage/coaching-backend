# this is for all user account authontication things 

from fastapi import APIRouter
from pymongo import MongoClient
import os 
from dotenv import load_dotenv
from .Schemas import User
from fastapi.responses import JSONResponse
from Auth import *

load_dotenv()
mongo = MongoClient(os.getenv('mongo'))
db = mongo['consult']
admin = db['admin']

auth = APIRouter()

# user login - admin
@auth.post('/admin-login', tags=['backoffice-user'])
async def login(user : User):
    userDetails = admin.find_one({'username' : user.username})
    if userDetails != None:
        if userDetails['password'] == user.password: 
            jwtToken = encodeJWT(os.getenv('adminJWT'), {'name' : user.username})
            return JSONResponse(status_code=200, content={'message' : 'sucssesfull', 'token' : jwtToken})
        else:
            return JSONResponse(status_code=403, content={'error' : 'details are not mach'}) 
    else:
        return JSONResponse(status_code=404, content={'error' : 'email not found'})

# user password change - admin
@auth.post('/admin-password-reset', tags=['backoffice-user'])
async def passwordReset():
    pass

# get verification code - admin
@auth.post('/admin-verification-code', tags=['backoffice-user'])
async def verificationCode():
    pass

