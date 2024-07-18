from fastapi import FastAPI
from Backoffice import Backoffice
from Client import Client
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins = [
    # this is only access to localhost
    "https://api.gamage.me",
    "http://localhost",
    "http://localhost:8080",
    # add vuejs localhost port
    "http://localhost:5173/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(Backoffice.routes)
app.include_router(Client.routes)
