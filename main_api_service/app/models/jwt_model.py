from pydantic import BaseModel, EmailStr

class JWTPayloadModel(BaseModel):
    id: str
    email: EmailStr
    exp: int

class JWTDataModel(BaseModel):
    algorithm: str = "HS256"
    secret: str
    payload: JWTPayloadModel