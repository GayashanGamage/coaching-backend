# this is for define all schemass
from pydantic import BaseModel

class User(BaseModel):
    username : str
    password : str