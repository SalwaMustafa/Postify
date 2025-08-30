from fastapi import FastAPI
from routes import Upload_text, Upload_settings

app = FastAPI()

app.include_router(Upload_text.upload_text_router)
app.include_router(Upload_settings.settings_router)
