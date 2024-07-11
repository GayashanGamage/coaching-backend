from fastapi import APIRouter
from . import User

routes = APIRouter()
routes.include_router(User.auth)

# book new session 
@routes.post('/session-book', tags=['client-function'])
async def sessionBook():
    pass

# get live sessions schedule in futur timeslot 
@routes.get('/live-session', tags=['client-function'])
async def liveSession():
    pass

# request refund from admin
@routes.post('/refund', tags=['client-function'])
async def refund():
    pass

# postpond session 
@routes.post('/pospond', tags=['client-function'])
async def pospond():
    pass

# change time of session 
@routes.post('/time-change', tags=['client-function'])
async def timeChange():
    pass

# get all booked session 
@routes.get('/session-list', tags=['client-function'])
async def sessionList():
    pass