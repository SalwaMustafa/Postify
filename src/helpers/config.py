from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    APP_NAME : str
    APP_VERSION : str
    MONGODB_URL : str
    MONGODB_DATABASE : str
    GOOGLE_API_KEY : str
    MODEL_NAME : str
    BACKEND_URL : str
    HF_TOKEN : str
    VOICE_URL : str
    
    class Config:
        env_file = '.env'



def get_settings():
    return Settings()