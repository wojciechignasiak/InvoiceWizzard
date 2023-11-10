from pydantic import BaseModel, EmailStr
from datetime import datetime

class JWTPayloadModel(BaseModel):
    id: str
    email: EmailStr
    exp: datetime

class JWTDataModel(BaseModel):
    algorithm: str = "HS256"
    secret: str
    payload: JWTPayloadModel