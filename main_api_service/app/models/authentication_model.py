from pydantic import BaseModel, Configdict, EmailStr

class LogInModel(BaseModel):
    model_config = Configdict(json_schema_extra={
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