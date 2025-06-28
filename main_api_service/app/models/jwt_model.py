from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID

class JWTPayloadModel(BaseModel):
    user_id: UUID
    email: EmailStr
    exp: datetime

class JWTDataModel(BaseModel):
    algorithm: str = "HS256"
    secret: str
    payload: JWTPayloadModel