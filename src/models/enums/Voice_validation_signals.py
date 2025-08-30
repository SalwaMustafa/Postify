from enum import Enum

class VoiceResponseSignal(Enum):
    
    FILE_VALIDATED_SUCCESS = "voice_file_validated_successfully"
    FILE_TYPE_NOT_SUPPORTED = "voice_file_type_not_supported"
    FILE_SIZE_EXCEEDED = "voice_file_size_exceeded"
  
