import os
import argon2
import jwt
from app.models.jwt_model import JWTDataModel, JWTPayloadModel


class UserUtils:
    
    async def salt_generator(self) -> str:
        try:
            salt = os.urandom(16)
            return str(salt)
        except Exception as e:
            print("UserUtils.salt_generator() Error:", e)
            raise Exception("Error durning salt generation occured.")

    async def hash_password(self, salt: str, password: str) -> str:
        try:
            ph = argon2.PasswordHasher()
            hashed_password = ph.hash(password + salt)
            return hashed_password
        except Exception as e:
            print("UserUtils.hash_password() Error:", e)
            print(f"Error durning hashing password occured")
    
    async def verify_password(self, salt: str, password: str, hash: str) -> bool:
        try:
            ph = argon2.PasswordHasher()
            is_the_same = ph.verify(hash, password+salt)
            return is_the_same
        except Exception as e:
            print("UserUtils.verify_password() Error:", e)
            print(f"Error durning verifying password.")

    async def jwt_encoder(self, jwt_data: JWTDataModel) -> str:
        try:
            jwt_token = jwt.encode(
                jwt_data.payload.model_dump(),
                jwt_data.secret,
                jwt_data.algorithm
            )
            return jwt_token
        except Exception as e:
            print("UserUtils.jwt_encoder() Error:", e)
            raise Exception("Error durning encoding jwt occured.")