from fastapi import APIRouter
from models import storage
from .schemes import SettingsInput

settings_router = APIRouter()

@settings_router.post('/upload/settings')
async def get_answers(answers : SettingsInput):
    storage.user_answers[answers.user_id] = answers
    return {
            "data" : storage.user_answers
        }
