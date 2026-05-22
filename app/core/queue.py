from arq.connections import RedisSettings, ArqRedis, create_pool
from app.core.config import get_settings

settings = get_settings()


async def get_redis_pool() -> ArqRedis:
    return await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))


# 全局 redis 实例，worker 启动后赋值
redis: ArqRedis | None = None


async def setup_redis():
    global redis
    redis = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
    return redis


async def close_redis():
    global redis
    if redis:
        await redis.close()
        redis = None


# ARQ Worker settings — 供 `arq worker` CLI 使用
class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    functions: list = []  # app 启动时动态注册
    max_jobs = 20
    job_timeout = 120
    poll_delay = 0.5
    keep_result = 86400  # 24h
