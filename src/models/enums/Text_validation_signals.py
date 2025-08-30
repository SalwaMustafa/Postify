from enum import Enum

class TextValidationSignal(Enum):

    TEXT_VALIDATED_SUCCESS = "text_validated_successfully"
    TEXT_EMPTY = "text_empty"
    TEXT_TOO_SHORT = "text_too_short"
    TEXT_TOO_LONG = "text_too_long"
    USER_ID_INVALID = "user_id_invalid"
    TEXT_INVALID_LANGUAGE = "text_invalid_language"
