from pydantic import BaseModel, ConfigDict, EmailStr

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

class CreateUserModel(BaseModel):
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


class UserPersonalInformationModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "first_name": "Jan",
                "last_name": "Kowalski",
                "phone_number": "123456789",
                "city": "Warszawa",
                "postal_code": "00-000",
                "street": "Ul. Nowa 6/13"
                }
            }
        )
    first_name: str = None
    last_name: str = None
    phone_number: str = None
    city: str = None
    postal_code: str = None
    street: str = None


class UpdateUserPasswordModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "current_password": "passw0rd!",
                "new_password": "passw0rd!1",
                "new_repeated_password": "passw0rd!1"
                }
            }
        )
    
    current_password: str
    new_password: str
    new_repeated_password: str

class UpdateUserEmailModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "current_email": "email@example.com",
                "new_email": "email1@example.com",
                "new_repeated_email": "email1@example.com"
                }
            }
        )
    
    current_email: EmailStr
    new_email: EmailStr
    new_repeated_email: EmailStr


class ConfirmedUserEmailChangeModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "id": "123456789",
                "new_email": "email1@example.com",
                }
            }
        )
    
    id: str
    new_email: EmailStr

class ConfirmedUserPasswordChangeModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "id": "123456789",
                "new_password": "passw0rd!",
                }
            }
        )
    
    id: str
    new_password: str

class ResetUserPasswordModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "email": "email1@example.com",
                "new_password": "passw0rd!",
                "new_repeated_password": "passw0rd!"
                }
            }
        )
    
    email: EmailStr
    new_password: str
    new_repeated_password: str