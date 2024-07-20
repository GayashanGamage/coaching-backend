# this is for all user account authontication things

from fastapi import APIRouter
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from .Schemas import UserAuth, User, UserEmail, VerificationCode, PasswordReset, UserDetails
from fastapi.responses import JSONResponse
from Auth import *
from random import randint
from datetime import datetime
from Email import *
from typing import Dict


load_dotenv()
mongo = MongoClient(os.getenv('mongo'))
db = mongo['consult']
admin = db['admin']

auth = APIRouter()

# ------------------------------


# endpoints
# create new admin user
createUser = {
    200 : {
        "description" : "successful",
        "content" : {
            "application/json" : {
                "example" : {
                    "message" : "successful"
                }
            }
        }
    },
    400 : {
        "description" : "duplicated",
        "content" : {
            "application/json" : {
                "example" : {
                    "error" : "duplicated",
                    "field" : "email | username"
                }
            }
        }
    },
}

@auth.post('/create-user',tags=['backoffice-user'] ,responses=createUser, summary="create new admin user")
async def createUser(userDetails : UserDetails):
    # find duplicate username or email
    userName = admin.find_one({'username' : userDetails.username})
    email = admin.find_one({'email' : userDetails.email})
    # if username and email not duplicate
    if userName == None and email == None:
        userDetails.password = hashPassword(userDetails.password)
        userData = userDetails.model_dump()
        admin.insert_one(userData)
        return JSONResponse(status_code=200, content={'message' : 'account create succesfully'})
    # if username or mail duplicate
    else:
        # find what is duplicated return that field
        field = ''
        if userName != None:
            field = 'username'
        else:
            field = 'email'
        return JSONResponse(status_code=400, content={'error' : 'duplicated', 'field' : field})
        

# user login - admin
adminLogin = {
    200 : {
        "description" : "successful",
        "content" : {
            "application/json" : {
                "example" : {
                    "message" : "successful"
                }
            }
        }
    },
    400 : {
        "description" : "invalied details",
        "content" : {
            "application/json" : {
                "example" : {
                    "error" : "invalied details"
                }
            }
        }
    },
    404 : {
        "description" : "email not found",
        "content" : {
            "application/json" : {
                "example" : {
                    "error" : "email not found"
                }
            }
        }
    },
}

@auth.post('/admin-login', tags=['backoffice-user'], responses=adminLogin, summary="login functionality for admin")
async def login(user: UserAuth):
    # find user by usernam in database
    userDetails = admin.find_one({'username': user.username})
    # if user found
    if userDetails != None:
        # get verified password 
        verify_password = verifyPassword(
            user.password, userDetails["password"])
        # if password verified issue token
        if verify_password == True:
            JWTdata = {'username' : userDetails['username'], 'password' : userDetails['password']}
            jwtToken = encodeJWT(JWTdata, os.getenv('adminJWT'))
            return JSONResponse(status_code=200, content={'message': 'sucssesfull', 'token': jwtToken})
        # if password not valied
        else:
            return JSONResponse(status_code=400, content={'error': 'invalied details'})
    # if user not found
    else:
        return JSONResponse(status_code=404, content={'error': 'email not found'})

# user password change - admin
adminPasswordReset = {
    200 : {
        "description" : "successful",
        "content" : {
            "application/json" : {
                "example" : {
                    "message" : "successful"
                }
            }
        }
    },
    400 : {
        "description" : "invalied request",
        "content" : {
            "application/json" : {
                "example" : {
                    "error" : "invalied request"
                }
            }
        }
    },
    404 : {
        "description" : "email not found",
        "content" : {
            "application/json" : {
                "example" : {
                    "error" : "email not found"
                }
            }
        }
    },
}

@auth.patch('/admin-password-reset', tags=['backoffice-user'], responses=adminPasswordReset, summary="chamge password of admin account")
async def passwordReset(passwordReset: PasswordReset):
    # find email from database
    userDetails = admin.find_one({"email": passwordReset.email})
    # get hashed password
    hashed_password = hashPassword(passwordReset.password)
    # if email not found or 'password_changable' False
    if userDetails == None or userDetails["password_changable"] == False:
        return JSONResponse(status_code=400, content={"error": "invalied request"})
    # if all conditions satisfied to reset password
    elif userDetails["password_changable"] == True:
        secreteKeyCount = len(userDetails['validation_key'])
        # update database
        admin.update_one({"email": userDetails["email"]}, {
                         '$set': {"password": hashed_password, "password_changable": False, f"validation_key.{secreteKeyCount-1}.availability": False}})
        return JSONResponse(status_code=200, content={"message": "sucsessfull"})
    # cannot find email from database
    else:
        return JSONResponse(status_code=404, content={"error" : "email not found"})

# get verification code - admin
# email should contain inside of jwt
adminCodeSend = {
    500 : {
        "description" : "email cannot send",
        "content" : {
            "application/json" : {
                "example" : {
                    "error" : "email cannot send"
                }
            }
        }
    },
    429 : {
        "description" : "too many request send",
        "content" : {
            "application/json" : {
                "example" : {
                    "error" : "too many request send"
                }
            }
        }
    },
    404 : {
        "description" : "email cannot find",
        "content" : {
            "application/json" : {
                "example" : {
                    "error" : "email cannot find"
                }
            }
        }
    },
}


@auth.patch('/admin-code-send', tags=['backoffice-user'], responses=adminCodeSend, summary="send secreat code via email to reset password for admin account")
async def verificationCodeSend(user: UserEmail):

    # get details from database using email
    userDetails = admin.find_one({'email': user.email})
    # if email in database
    if userDetails != None:
        # set new scret code and setup time
        newData = {'code': randint(
            1000, 9999), 'time': datetime.now(), 'availability': True}
        # set all required details for transactional email
        mailData = {'to': {'name': userDetails['firstName'], 'email': userDetails['email']}, 'params': {
            'code': newData['code']}, 'template': 3, 'subject': 'reset password'}
        # 'validation_key' in userDetails and it's lenth is less thatn 3
        if 'validation_key' in userDetails and len(userDetails['validation_key']) < 3:
            # send email
            send_email = sendEmail(mailData)
            # if send email fail 
            if send_email['mail_id'] == None:
                return JSONResponse(status_code=500, content={'error': 'email canot send'})
            # else insert email data into newData
            newData['email'] = send_email
            # update database
            admin.update_one({'email': userDetails['email']}, {
                             '$push': {'validation_key': newData}})
        # 'validation_key' in useDetails and lenth is eaqual to 3
        elif 'validation_key' in userDetails and len(userDetails['validation_key']) == 3:
            # calculating mail sending time gap
            timeGap = int((datetime.now() - datetime.fromisoformat(
                str(userDetails['validation_key'][0]['time']))).total_seconds())
            # timegap greater than 120
            if timeGap > 120:
                # send email
                send_email = sendEmail(mailData)
                # if email does not send 
                if send_email['mail_id'] == None:
                    return JSONResponse(status_code=500, content={'error': 'email canot send'})
                # else update send email data into 'newData'
                newData['email'] = send_email
                # update datase - append new item
                admin.update_one({'email': userDetails['email']}, {
                                 '$push': {'validation_key': newData}})
                # update database - remove first item
                admin.update_one({'email': userDetails['email']}, {
                                 '$pop': {'validation_key': -1}})
            # timegap is less than 120
            else:
                return JSONResponse(status_code=429, content={'error': 'too many request send'})
        # 'validation_key' not in 'userDetials'
        else:
            # send email with secrete code
            send_email = sendEmail(mailData)
            # if email sending fail
            if send_email['mail_id'] == None:
                return JSONResponse(status_code=500, content={'error': 'email canot send'})
            # else insert email sending return data to 'newData'
            newData['email'] = send_email
            # update database
            admin.update_one({'email': userDetails['email']}, {
                             '$set': {'validation_key': [newData]}})
        # if secrete code store sucsessfull
        return JSONResponse(status_code=200, content={'message': 'sucsessfull'})
    # email not found
    else:
        return JSONResponse(status_code=404, content={'message': 'email cannot find'})


# verify secrete code
adminVerificationCode = {
    200 : {
        "description" : "successful",
        "content" : {
            "application/json" : {
                "example" : {
                    "message" : "successful"
                }
            }
        }
    },
    400 : {
        "description" : "invalide key",
        "content" : {
            "application/json" : {
                "example" : {
                    "error" : "invalied key"
                }
            }
        }
    },
    404 : {
        "description" : "email not found",
        "content" : {
            "application/json" : {
                "example" : {
                    "message" : "email not found"
                }
            }
        }
    },
}
@auth.post('/admin-code-verification', tags=['backoffice-user'], responses=adminVerificationCode, summary="secrete key validation")
async def codeVerification(verificationCode: VerificationCode):
    
    # find email from database 
    userDetails = admin.find_one({"email": verificationCode.email})
    # all details mached 
    if userDetails != None and userDetails["validation_key"][-1]["code"] == verificationCode.code:
        admin.update_one({'email': verificationCode.email}, {
                         '$set': {"password_changable": True}})
        return JSONResponse(status_code=200, content={'message': 'sucsusfull'})
    # email valied and key not valied  
    elif userDetails != None and userDetails["validation_key"][-1]["code"] != verificationCode.code:
        return JSONResponse(status_code=400, content={"error": "invalide key"})
    # both are invalied
    else:
        return JSONResponse(status_code=404, content={"error": "email not found"})

# -----------------------------
