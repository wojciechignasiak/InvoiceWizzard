from pydantic import BaseModel, ConfigDict, EmailStr

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


class UserPersonalInformation(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "first_name": "Jan",
                "last_name": "Kowalski",
                "phone_number": "123456789",
                "city": "Warszawa",
                "street": "Ul. Nowa 6/13"
                }
            }
        )
    first_name: str = None
    last_name: str = None
    phone_number: str = None
    city: str = None
    street: str = None