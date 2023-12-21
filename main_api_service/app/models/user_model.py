from pydantic import BaseModel, ConfigDict, EmailStr
from fastapi import HTTPException, status
from datetime import date
from uuid import uuid4
import re
from typing import Optional
from app.schema.schema import User



class UserModel(BaseModel):
    id: str
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    city: Optional[str]
    postal_code: Optional[str]
    street: Optional[str]
    registration_date: str
    last_login: str
    email_notification: bool
    push_notification: bool

    def user_schema_to_model(user_schema: User) -> "UserModel":
        return UserModel(
            id=str(user_schema.id),
            email=user_schema.email,
            first_name=user_schema.first_name,
            last_name=user_schema.last_name,
            phone_number=user_schema.phone_number,
            city=user_schema.city,
            postal_code=user_schema.postal_code,
            street=user_schema.street,
            registration_date=str(user_schema.registration_date),
            last_login=str(user_schema.last_login),
            email_notification=user_schema.email_notification,
            push_notification=user_schema.push_notification
        )

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._validate_email()
        self._validate_password()

    def _validate_email(self):
        if self.email != self.repeated_email:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Provided email adresses don't match.")
        
    def _validate_password(self):
        if len(self.password) < 8:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Provided password is too short.")
        if self.password != self.repeated_password:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Provided passwords don't match.")
        if not re.search(r'\d', self.password):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Password needs to contatain at least 1 digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', self.password):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Password needs to contatain at least 1 special character.")


class CreateUserModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "email": "email@example.com",
                "password": "hashedPassword",
                "salt": "asksmdadkwdaskdawdakjfja===1asa!",
                }
            }
        )
    
    email: EmailStr
    password: str
    salt: str

    @property
    def id(self):
        return uuid4()
    
    @property
    def registration_date(self):
        return date.today()
    
    @property
    def last_login(self):
        return date.today()


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
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    street: Optional[str] = None


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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._validate_new_password()
        
    def _validate_new_password(self):
        if len(self.new_password) < 8:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Provided password is too short.")
        if self.new_password != self.new_repeated_password:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Provided passwords don't match.")
        if not re.search(r'\d', self.new_password):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Password needs to contatain at least 1 digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', self.new_password):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Password needs to contatain at least 1 special character.")
        

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._validate_email()

    def _validate_email(self):
        if self.new_email != self.new_repeated_email:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Provided email adresses don't match.")


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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._validate_new_password()
        
    def _validate_new_password(self):
        if len(self.new_password) < 8:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Provided password is too short.")
        if self.new_password != self.new_repeated_password:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Provided passwords don't match.")
        if not re.search(r'\d', self.new_password):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Password needs to contatain at least 1 digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', self.new_password):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Password needs to contatain at least 1 special character.")