import os 
import argon2

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