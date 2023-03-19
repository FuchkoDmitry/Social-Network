# import uvicorn
from fastapi import FastAPI

from apps.user.views import router as user_router
from apps.post.views import posts_router, comments_router

app = FastAPI()
app.include_router(user_router)
app.include_router(posts_router)
app.include_router(comments_router)

# needs for debug
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8080)
