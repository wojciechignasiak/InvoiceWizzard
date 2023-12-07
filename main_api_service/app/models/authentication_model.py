from pydantic import BaseModel, ConfigDict, EmailStr

class LogInModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "email": "email@example.com",
                "password": "passw0rd!",
                "remember_me": False
                }
            }
        )
    email: EmailStr
    password: str
    remember_me: bool = False