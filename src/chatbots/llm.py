from langchain.chat_models import init_chat_model
from helpers.config import get_settings   

settings = get_settings()

model = init_chat_model(settings.MODEL_NAME, api_key = settings.GOOGLE_API_KEY)

voice_headers = {"Authorization": f"Bearer {settings.HF_TOKEN}",
           "Content-Type": "audio/wav"}
voice_model = settings.VOICE_URL

