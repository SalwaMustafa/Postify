from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    APP_NAME : str
    APP_VERSION : str
    FILE_ALLOWED_TYPES: str = ""

    @property
    def file_allowed_types_list(self) -> list[str]:
        return [t.strip() for t in self.FILE_ALLOWED_TYPES.split(",") if t.strip()]
    
    VOICE_MAX_SIZE_MB : int

    MONGODB_URL : str
    MONGODB_DATABASE : str
    GOOGLE_API_KEY : str

    class Config:
        env_file = '.env'



def get_settings():
    return Settings()