from fastapi import FastAPI
from Backoffice import Backoffice
from Client import Client

app = FastAPI()
app.include_router(Backoffice.routes)
app.include_router(Client.routes)
