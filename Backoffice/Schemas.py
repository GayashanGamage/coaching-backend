# this is for define all schemass
from pydantic import BaseModel, EmailStr


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
