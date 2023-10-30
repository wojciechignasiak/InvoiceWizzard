import os 
from argon2 import PasswordHasher

class UserUtils:
    
    async def salt_generator(self):
        try:
            salt = os.urandom(16)
            return salt
        except Exception as e:
            print(f"Error durning generating salt occured: {e}")

    async def hash_password(self, salt: str, password: str) -> str:
        try:
            ph = PasswordHasher()
            hashed_password = ph.hash(password + salt)
            return hashed_password
        except Exception as e:
            print(f"Error durning hashing password occured: {e}")