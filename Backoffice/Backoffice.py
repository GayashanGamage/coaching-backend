# this is for all functionalities for backoffice site

from fastapi import APIRouter, Depends
from . import User
from pymongo import MongoClient
from .Schemas import LiveSession, LiveSessionWithId, timeSlot, User as UserName
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from bson import ObjectId
from Auth import authVerification
from typing import Dict

load_dotenv()

mongo = MongoClient(os.getenv('mongo'))
db = mongo['consult']
cluster = db['users']
liveSessionSchedul = db['liveSessionSchedul']
calendar = db['calendar']
user = db['user']
admin = db['admin']

routes = APIRouter()
routes.include_router(User.auth)

# create new live session
# update live session details
responses = { 200 : {
        "description" : "successfull",
        "content" : {
            "application/json" : {
                "example" : {
                    "session" : "[]",
                }
            }
        }
    },
    400 : {
        "error" : "duplicate content",
        "content" : {
            "application/json" : {
                "example" : {
                    "error" : "duplicate content"
                }
            }
        }
    },
}

@routes.post('/set-live-session', tags=['backoffice-function'], responses=responses, summary="list new live sessions")
async def setLiveSession(details : LiveSession):
    # find sessions from database that same to 'details' day
    allSession = liveSessionSchedul.find_one({'date' : details.date})
    # if there is sameday session in database 
    if allSession != None:
        return JSONResponse(status_code=400, content={"message" : "cannot post two sessions in one day"})
    # if no sameday session
    else:
        sessionData = details.model_dump()
        # insert 'details' to database
        liveSessionSchedul.insert_one(sessionData)
        return JSONResponse(status_code=200, content={"message" : "sucsesfull"})

# update live sessions
# update live session details
responses = { 200 : {
        "description" : "successfull",
        "content" : {
            "application/json" : {
                "example" : {
                    "session" : "[]",
                }
            }
        }
    },
    400 : {
        "error" : "no content",
        "content" : {
            "application/json" : {
                "example" : {
                    "error" : "no content"
                }
            }
        }
    },
}

@routes.patch('/update-live-session', tags=['backoffice-function'], summary="update liveSession", responses=responses)
async def updateLiveSession(details : LiveSessionWithId):
    # find livesession using 'details' id
    session = liveSessionSchedul.find_one({'_id' : ObjectId(details.id)})
    # if cannot find 'details' id from database
    if session == None:
        return JSONResponse(status_code=400, content={"error" : 'content not found'})
    # if find 'details' id session from database
    else:
        updatedDetails = details.model_dump(exclude={'_id', 'create'})
        # update database
        liveSessionSchedul.update_one({'_id' : ObjectId(details.id) }, {'$set' : updatedDetails})
        return JSONResponse(status_code=200, content={'message' : 'sucsessful'})

#list all live sessions 
responses = { 200 : {
        "description" : "successfull",
        "content" : {
            "application/json" : {
                "example" : {
                    "session" : "[]",
                }
            }
        }
    },
    400 : {
        "error" : "no content",
        "content" : {
            "application/json" : {
                "example" : {
                    "error" : "no content"
                }
            }
        }
    },
}

# TODO: this should implement to get filterd output using query parameters
@routes.get('/list-session', tags=['backoffice-function'], responses=responses, summary="get all listed sessions")
async def listSession():
    # get all livesessions from database
    allSessions = liveSessionSchedul.find()
    # if there is no sessions
    if allSessions == None:
        return JSONResponse(status_code=400, content={'error' : 'no content'})
    # if there are sessions
    else:
        # store all session in list with string converted '_id', 'postTime', 'create'
        sessionList = []
        for item in allSessions:
            # convert all datetime and object to string
            item['_id'] = str(item['_id'])
            item['postTime'] = str(item['postTime'])
            item['create'] = str(item['create'])
            
            # this is optional field 'lastUpdate'. there for we have to check the existancy
            if 'lastUpdate' in item:
                item['lastUpdate'] = str(item['lastUpdate'])
            sessionList.append(item)
        return JSONResponse(status_code=200, content={'sessions' : sessionList})


# get admins' timeslots 
responses = { 200 : {
        "description" : "successfull",
        "content" : {
            "application/json" : {
                "example" : {
                    "date" : "2024-07-17",
                    "avilableTiem" : '[]'
                }
            }
        }
    },
}
@routes.get('/get-timeslots', tags=['backoffice-function'], summary="get recervable timeslots", responses=responses)
async def getTimeSlots(date : str): # 2024-07-17
    """
    **date** - format should be '2024-07-17' 
    """
    #TODO : recervable timeslots should implement 
    # get date from document
    schedulDetails = calendar.find_one({'date' : date})
    if schedulDetails == None:
        schedulDetails = []
    return JSONResponse(status_code=200, content={'date' : date, 'avilableTime' : schedulDetails})
    

# set admins' timeslots 
# endpoint output documentation
responses = { 200 : {
        "description" : "update existing date",
        "content" : {
            "application/json" : {
                "example" : {
                    "message" : "update successfully"
                }
            }
        }
    },
    201 : {
        "description" : "new date created",
        "content" : {
            "application/json" : {
                "example" : {
                    "message" : "create new date"
                }
            }
        }
    },
    400 : {
        "description" : "zero timeslots",
        "content" : {
            "application/json" : {
                "example" : {
                    "error" : "invalied input"
                }
            }
        }
    },
}
@routes.post('/set-timeslots', tags=['backoffice-function'], responses=responses, summary="set or update timeslots by admin")
async def setTimeSlots(details : timeSlot):
    """
    if admin set at lease one available timeslot in paticuller date, it will store in database. otherwise not
    """
    # find selected date available timeslots 
    schedulDetails = calendar.find_one({'date' : details.date})
    # if cannot find date in datebase, create new date and assign available timeslots 
    if schedulDetails == None:
        calendar.insert_one(details.model_dump())
        return JSONResponse(status_code=201, content={'message' : 'create new date'})
    # request without timeslots
    elif len(details.avilableTime) == 0:
        return JSONResponse(status_code=400, content={'error' : 'invalied input'})
    # if can find date in database, update existing date
    else:
        calendar.update_one({'date' : details.date}, {'$set' : {'avilableTime' : details.avilableTime}})
        return JSONResponse(status_code=200, content={'message' : 'update sucssesfully'})


# list all client 
# endpoint output documentation
responses = { 200 : {
        "description" : "successful",
        "content" : {
            "application/json" : {
                "example" : {
                    "_id" : "id",
                    "firstName" : "gayashan",
                    "lastName" : "gamage",
                    "email" : "example@mail.com"
                }
            }
        }
    },
}

@routes.get('/clients', tags=['backoffice-function'], responses=responses, summary="list all clients")
async def listClients():
    # get all clients from database
    clientDetails = user.find({}, {'email' : 1, 'lastName' : 1, 'firstName' : 1})
    # store all client in list with string converted '_id'
    clientList = []
    if clientDetails == None:
        clientDetails = []
    else:
        for item in clientDetails:
            item['_id'] = str(item['_id'])
            clientList.append(item)
    return JSONResponse(status_code=200, content={'allUsers' : clientList})

# get single client information
# endpoint output documentation
responses = { 200 : {
        "description" : "successful",
        "content" : {
            "application/json" : {
                "example" : {
                    "_id" : "id",
                    "firstName" : "gayashan",
                    "lastName" : "gamage",
                    "email" : "example@mail.com"
                }
            }
        }
    },
    400 : {
        "description" : "invalied email",
        "content" : {
            "application/json" : {
                "example" : {
                    "error" : "invalied details"
                }
            }
        }
    },
}

@routes.get('/client/{id}', tags=['backoffice-function'], responses=responses, summary="get one client by id")
async def client(id : str):
    # get document according to '_id' 
    clientDetails = user.find_one({'_id' : ObjectId(id)}, {'password' : 0, 'validation_key' : 0})
    # if document cannot find related to '_id'
    if clientDetails == None:
        return JSONResponse(status_code=400, content={"error" : "invalied details"})
    # otherwise return the document
    else:
        clientDetails['_id'] = str(clientDetails['_id'])
        return JSONResponse(status_code=200, content=clientDetails)

# admin summery page data 
# document responses
responses = { 200 : {
        "description" : "successful",
        "content" : {
            "application/json" : {
                "example" : {
                    "message" : "successful"
                }
            }
        }
    },
    401 : {
        "description" : "unauthorized request",
        "content" : {
            "application/json" : {
                "example" : {
                    "error" : "unauthorized"
                }
            }
        }
    },
}

@routes.get('/summary', tags=['backoffice-function'], responses=responses, summary="summary of entire platform")
async def summary(token: Dict =Depends(authVerification)):
    # validate JTW token
    if token == False:
        return JSONResponse(status_code=401, content={'error' : 'unauthorized'})
    else:
        return JSONResponse(status_code=200, content={'message' : 'successful'})

# JWT verification
# docuemnt respond
responses = { 200 : {
        "description" : "successful",
        "content" : {
            "application/json" : {
                "example" : {
                    "message" : "successful"
                }
            }
        }
    },
    401 : {
        "description" : "unauthorized request",
        "content" : {
            "application/json" : {
                "example" : {
                    "error" : "unauthorized"
                }
            }
        }
    },
}

@routes.get('/admin-auth', tags=['backoffice-function'], responses=responses, summary="basic JWT verification for admin")
async def adminAuth(user : UserName, token : Dict = Depends(authVerification)):
    # find user details from database
    userDetails = admin.find_one({'username' : user.username})
    # evaluate borth username and JWT token
    if token and userDetails and token['password'] == userDetails['password']:
        return JSONResponse(status_code=200, content={'message' : 'successful'})
    else:
        return JSONResponse(status_code=401, content={'error' : 'unathorized'})