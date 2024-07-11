# this is for all user account related things 
# create new account and authonticate

from fastapi import APIRouter

auth = APIRouter()

# login for user
@auth.post('/login', tags=['client-user'])
async def login():
    pass

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
async def register():
    pass