# this is for all user account authontication things 

from fastapi import APIRouter
from pymongo import MongoClient
import os 
from dotenv import load_dotenv


load_dotenv()
mongo = MongoClient(os.getenv('mongo'))
db = mongo['consult']
admin = db['admin']

auth = APIRouter()

# user login - admin
@auth.post('/admin-login', tags=['backoffice-user'])
async def login():
    pass

# user password change - admin
@auth.post('/admin-password-reset', tags=['backoffice-user'])
async def passwordReset():
    pass

# get verification code - admin
@auth.post('/admin-verification-code', tags=['backoffice-user'])
async def verificationCode():
    pass

