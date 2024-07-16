# this is for all functionalities for backoffice site

from fastapi import APIRouter
from . import User
from pymongo import MongoClient
from .Schemas import LiveSession, LiveSessionWithId
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

mongo = MongoClient(os.getenv('mongo'))
db = mongo['consult']
cluster = db['users']
liveSessionSchedul = db['liveSessionSchedul']

routes = APIRouter()
routes.include_router(User.auth)

# create new live session
@routes.post('/set-live-session', tags=['backoffice-function'])
async def setLiveSession(details : LiveSession):
    allSession = liveSessionSchedul.find_one({'date' : details.date})
    
    # find sameday sessions 
    if allSession != None:
        return JSONResponse(status_code=400, content={"message" : "cannot post two sessions in one day"})
    else:
        sessionData = details.model_dump()
        liveSessionSchedul.insert_one(sessionData)
        return JSONResponse(status_code=200, content={"message" : "sucsesfull"})

# update live session details
@routes.patch('/update-live-session', tags=['backoffice-function'])
async def updateLiveSession(details : LiveSessionWithId):
    session = liveSessionSchedul.find_one({'_id' : ObjectId(details.id)})
    if session == None:
        return JSONResponse(status_code=400, content={"error" : 'content not found'})
    else:
        updatedDetails = details.model_dump(exclude={'_id', 'create'})
        liveSessionSchedul.update_one({'_id' : ObjectId(details.id) }, {'$set' : updatedDetails})
        return JSONResponse(status_code=200, content={'message' : 'sucsessful'})

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