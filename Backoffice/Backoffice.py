# this is for all functionalities for backoffice site

from fastapi import APIRouter
from . import User
from pymongo import MongoClient

mongo = MongoClient('mongodb+srv://gayashangamage:2692g.rg0968CJ@consultservice.c3gvek2.mongodb.net/?retryWrites=true&w=majority&appName=consultService')
db = mongo['consult']
cluster = db['users']

routes = APIRouter()
routes.include_router(User.auth)

# create new live session
@routes.post('/set-live-session', tags=['backoffice-function'])
async def setLiveSession(): 
    pass

# 
@routes.get('/list-session', tags=['backoffice-function'])
async def listSession():
    pass

# manage admins' timeslots 
@routes.post('/manage-timeslots', tags=['backoffice-function'])
async def manageTimeSlots():
    pass

# accept refund request made by client
@routes.post('/refund-accept', tags=['backoffice-function'])
async def refuncAccept():
    pass

# list all client 
@routes.get('/clients', tags=['backoffice-function'])
async def listClients():
    pass

# get single client information
@routes.get('/client/:id', tags=['backoffice-function'])
async def client():
    pass

# admin summery page data 
@routes.get('/summery', tags=['backoffice-function'])
async def summery():
    pass