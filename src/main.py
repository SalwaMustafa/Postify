from fastapi import FastAPI
from routes import Upload_text

app = FastAPI()

app.include_router(Upload_text.upload_text_router)
