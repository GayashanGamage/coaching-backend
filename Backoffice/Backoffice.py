# this is for all functionalities for backoffice site

from fastapi import APIRouter
from . import User
from pymongo import MongoClient
from .Schemas import LiveSession, LiveSessionWithId, timeSlot
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

mongo = MongoClient(os.getenv('mongo'))
db = mongo['consult']
cluster = db['users']
liveSessionSchedul = db['liveSessionSchedul']
calendar = db['calendar']
user = db['user']

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

#list all live sessions 
@routes.get('/list-session', tags=['backoffice-function'])
async def listSession():
    allSessions = liveSessionSchedul.find()
    if allSessions == None:
        return JSONResponse(status_code=400, content={'error' : 'no content'})
    else:
        sessionList = []
        for item in allSessions:
            # convert all datetime and object to string
            item['_id'] = str(item['_id'])
            item['postTime'] = str(item['postTime'])
            item['create'] = str(item['create'])
            
            # this is optional field. there for we have to check the existancy
            if 'lastUpdate' in item:
                item['lastUpdate'] = str(item['lastUpdate'])
            sessionList.append(item)
        return JSONResponse(status_code=200, content={'sessions' : sessionList})


# get admins' timeslots 
@routes.get('/get-timeslots', tags=['backoffice-function'])
async def getTimeSlots(date : str): # 2024-07-17
    schedulDetails = calendar.find_one({'date' : date})
    if schedulDetails == None:
        schedulDetails = []
    return JSONResponse(status_code=200, content={'date' : date, 'avilableTime' : schedulDetails})
    

# set admins' timeslots 
# 24 hours should be in avilableTime
@routes.post('/set-timeslots', tags=['backoffice-function'])
async def setTimeSlots(details : timeSlot):
    schedulDetails = calendar.find_one({'date' : details.date})

    # create new date
    if schedulDetails == None:
        calendar.insert_one(details.model_dump())
        return JSONResponse(status_code=201, content={'message' : 'create new date'})
    # request without timeslots
    elif len(details.avilableTime) == 0:
        return JSONResponse(status_code=400, content={'erro' : 'cannot strore empty timeslots'})
    # upodate existing date
    else:
        calendar.update_one({'date' : details.date}, {'$set' : {'avilableTime' : details.avilableTime}})
        return JSONResponse(status_code=200, content={'message' : 'update sucssesfully'})


# list all client 
@routes.get('/clients', tags=['backoffice-function'])
async def listClients():
    clientDetails = user.find({}, {'email' : 1, 'lastName' : 1, 'firstName' : 1})
    clientList = []
    if clientDetails == None:
        clientDetails = []
    else:
        for item in clientDetails:
            item['_id'] = str(item['_id'])
            clientList.append(item)
    return JSONResponse(status_code=200, content={'allUsers' : clientList})

# get single client information
@routes.get('/client/{id}', tags=['backoffice-function'])
async def client(id : str):
    clientDetails = user.find_one({'_id' : ObjectId(id)}, {'password' : 0, 'validation_key' : 0})
    if clientDetails == None:
        return JSONResponse(status_code=400, content={"error" : "no content"})
    else:
        clientDetails['_id'] = str(clientDetails['_id'])
        return JSONResponse(status_code=200, content=clientDetails)

# admin summery page data 
@routes.get('/summery', tags=['backoffice-function'])
async def summery():
    pass