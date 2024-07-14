# this is for define for schemas
from pydantic import BaseModel, EmailStr


class User(BaseModel):
    password: str
    email: EmailStr


class UserBasics(User):
    firstName: str
    lastName: str
    password: str


class UserEmail(BaseModel):
    email: EmailStr


class UserVerification(UserEmail):
    password: str


class VerificationCode(UserEmail):
    code: int


class PasswordReset(UserVerification):
    pass
