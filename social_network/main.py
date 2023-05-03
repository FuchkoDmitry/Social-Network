# import uvicorn
from fastapi import FastAPI

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

import aioredis

from apps.user.views import router as user_router
from apps.post.views import posts_router, comments_router

app = FastAPI()
app.include_router(user_router)
app.include_router(posts_router)
app.include_router(comments_router)
# redis = aioredis.from_url('redis://localhost:5370', encoding="utf8", decode_responses=True)
redis = aioredis.from_url('redis://localhost:6379', encoding="utf8", decode_responses=True)
FastAPICache.init(RedisBackend(redis), prefix='fastapi:cache')

# needs for debug
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8080)
