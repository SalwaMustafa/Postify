import regex
from models.enums import TextValidationSignal

class TextController:
    def __init__(self):

        self.min_length = 10
        self.max_length = 1000

        self.allowed_pattern = regex.compile(
        r'^[\p{Arabic}A-Za-z0-9\s.,!?،؛\p{Emoji_Presentation}\p{Emoji}\u200d\ufe0f]*$'
        )

    def validate_input(self, user_id: int, content: str):
        if user_id <= 0:
            return False, TextValidationSignal.USER_ID_INVALID.value

        text = content.strip()
        if not text:
            return False, TextValidationSignal.TEXT_EMPTY.value

        if len(text) < self.min_length:
            return False, TextValidationSignal.TEXT_TOO_SHORT.value

        if len(text) > self.max_length:
            return False, TextValidationSignal.TEXT_TOO_LONG.value

        if not self.allowed_pattern.match(text):
            return False, TextValidationSignal.TEXT_INVALID_LANGUAGE.value


        return True, TextValidationSignal.TEXT_VALIDATED_SUCCESS.value