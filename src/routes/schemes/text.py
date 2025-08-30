from pydantic import BaseModel

class TextInput(BaseModel):

    user_id: int
    content: str
