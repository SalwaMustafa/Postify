from fastapi import UploadFile
from models.enums import VoiceResponseSignal
from helpers.config import get_settings 

class VoiceController:

    def __init__(self):

        self.app_settings = get_settings()
        self.size_scale = 1048576  # 1MB = 1048576 bytes
        

    async def validate_uploaded_voice(self, file: UploadFile):

        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES :
            return False, VoiceResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        contents = await file.read()
        file_size = len(contents)
        await file.seek(0)  

        if file_size > self.app_settings.VOICE_MAX_SIZE_MB * self.size_scale:
            return False, VoiceResponseSignal.FILE_SIZE_EXCEEDED.value

        return True, VoiceResponseSignal.FILE_VALIDATED_SUCCESS.value
    