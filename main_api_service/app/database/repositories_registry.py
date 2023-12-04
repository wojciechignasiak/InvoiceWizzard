from app.database.postgres.repositories.user_repository_abc import UserPostgresRepositoryABC
from app.database.postgres.repositories.user_business_entity_repository_abc import UserBusinessEntityPostgresRepositoryABC
from app.database.redis.repositories.user_repository_abc import UserRedisRepositoryABC
from app.database.redis.repositories.user_business_entity_repository_abc import UserBusinessEntityRedisRepositoryABC

class RepositoriesRegistry:
    def __init__(self, 
                user_postgres_repository: UserPostgresRepositoryABC, 
                user_redis_repository: UserRedisRepositoryABC,
                user_business_entity_postgres_repository: UserBusinessEntityPostgresRepositoryABC,
                user_business_entity_redis_repository: UserBusinessEntityRedisRepositoryABC) -> None:
        
        self.user_postgres_repository = user_postgres_repository
        self.user_redis_repository = user_redis_repository
        self.user_business_entity_postgres_repository = user_business_entity_postgres_repository
        self.user_business_entity_redis_repository = user_business_entity_redis_repository


    async def return_user_postgres_repository(self, session) -> UserPostgresRepositoryABC:
        return self.user_postgres_repository(session)
    
    async def return_user_redis_repository(self, redis_client) -> UserRedisRepositoryABC:
        return self.user_redis_repository(redis_client)

    async def return_user_business_entity_postgres_repository(self, session) -> UserBusinessEntityPostgresRepositoryABC:
        return self.user_business_entity_postgres_repository(session)
    
    async def return_user_business_entity_redis_repository(self, redis_client) -> UserBusinessEntityRedisRepositoryABC:
        return self.user_business_entity_redis_repository(redis_client)