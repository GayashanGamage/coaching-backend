# this is for define for schemas
from pydantic import BaseModel, EmailStr


class User(BaseModel):
    fistName: str
    lastName: str
    password: str
    email: EmailStr


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
