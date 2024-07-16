# this is for define all schemass
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

date = str(datetime.now().date())
time = str(datetime.now().time())

class User(BaseModel):
    username: str


class UserAuth(User):
    password: str


class UserEmail(BaseModel):
    email: EmailStr


class UserVerification(UserEmail):
    password: str


class VerificationCode(UserEmail):
    code: int


class PasswordReset(UserVerification):
    pass

class LiveSession(BaseModel):
    title : str
    description : str
    agenda : list
    venue : str
    date : str = Field(default=date)
    time : str = Field(default=time)
    postTime : datetime
    create : Optional[datetime] = Field(default=datetime.now())

class LiveSessionWithId(LiveSession):
    id : str
    lastUpdate : Optional[datetime] = Field(default=datetime.now())