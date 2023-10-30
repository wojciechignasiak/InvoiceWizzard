import os 

class UserUtils:
    
    async def salt_generator():
        try:
            salt = os.urandom(16)
            return salt
        except Exception as e:
            print(f"Error durning generating salt occured: {e}")