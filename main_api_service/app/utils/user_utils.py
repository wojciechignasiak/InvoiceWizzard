import os
import base64
import argon2
import jwt
from app.models.jwt_model import JWTDataModel
from app.logging import logger

class UserUtils:
    
    async def salt_generator(self) -> str:
        try:
            salt: bytes = os.urandom(16)
            return base64.b64encode(salt).decode('utf-8')
        except Exception as e:
            logger.error(f"UserUtils.salt_generator() Error: {e}")
            raise Exception("Error durning salt generation occured.")

    async def hash_password(self, salt: str, password: str) -> str:
        try:
            ph = argon2.PasswordHasher()
            hashed_password = ph.hash(password + salt)
            return hashed_password
        except Exception as e:
            logger.error(f"UserUtils.hash_password() Error: {e}")
            raise Exception("Error durning hashing password occured.")
    
    async def verify_password(self, salt: str, password: str, hash: str) -> bool:
        try:
            ph = argon2.PasswordHasher()
            is_the_same = ph.verify(hash, password+salt)
            return is_the_same
        except Exception as e:
            logger.error(f"UserUtils.verify_password() Error: {e}")
            raise Exception("Error durning verifying password.")

    async def jwt_encoder(self, jwt_data: JWTDataModel) -> str:
        try:
            jwt_token = jwt.encode(
                jwt_data.payload.model_dump(),
                jwt_data.secret,
                jwt_data.algorithm
            )
            return jwt_token
        except Exception as e:
            logger.error(f"UserUtils.jwt_encoder() Error: {e}")
            raise Exception("Error durning encoding jwt occured.")