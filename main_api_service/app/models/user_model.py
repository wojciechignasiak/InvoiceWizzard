from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import date

class NewUserTemporaryModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "email": "email@example.com",
                "password": "hashedPassword",
                "salt": "asksmdadkwdaskdawdakjfja===1asa!",
                "registration_date": "2023-10-25"
                }
            }
        )
    
    email: EmailStr
    password: str
    salt: str
    registration_date: str

class RegisterUserModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "email": "email@example.com",
                "repeated_email": "email@example.com",
                "password": "passw0rd!",
                "repeated_password": "passw0rd!"
                }
            }
        )
    email: EmailStr
    repeated_email: EmailStr
    password: str
    repeated_password: str
