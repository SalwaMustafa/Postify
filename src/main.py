from fastapi import FastAPI
from routes import Upload_text, Upload_settings, Upload_voice
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():

    settings = get_settings()

    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

@app.on_event("shutdown")
async def shutdown_db_client():

    app.mongo_conn.close()

app.include_router(Upload_text.upload_text_router)
app.include_router(Upload_settings.settings_router)
app.include_router(Upload_voice.upload_voice_router)
