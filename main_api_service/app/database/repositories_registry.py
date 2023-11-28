from app.database.postgres.repositories.user_repository import UserPostgresRepository
from app.database.postgres.repositories.user_business_entites_repository import UserBusinessEntityPostgresRepository
from app.database.redis.repositories.user_repository import UserRedisRepository
from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis

class RepositoriesRegistry:
    def __init__(self, 
                user_postgres_repository: UserPostgresRepository, 
                user_redis_repository: UserRedisRepository,
                user_business_entity_postgres_repository: UserBusinessEntityPostgresRepository) -> None:
        self.user_postgres_repository: UserPostgresRepository = user_postgres_repository
        self.user_redis_repository: UserRedisRepository = user_redis_repository
        self.user_business_entity_postgres_repository: UserBusinessEntityPostgresRepository = user_business_entity_postgres_repository


    async def return_user_postgres_repository(self, session: AsyncSession) -> UserPostgresRepository:
        return self.user_postgres_repository(session)
    
    async def return_user_redis_repository(self, redis_client: Redis) -> UserRedisRepository:
        return self.user_redis_repository(redis_client)

    async def return_user_business_entity_postgres_repository(self, session: AsyncSession) -> UserBusinessEntityPostgresRepository:
        return self.user_business_entity_postgres_repository(session)