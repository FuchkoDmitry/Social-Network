from datetime import date
from fastapi import FastAPI
from apps.user.views import router as user_router

app = FastAPI()
app.include_router(user_router)


@app.get("/")
async def root(d: date):
    return {"message": d}
