from pydantic import BaseModel

class SaveRequest(BaseModel):
    thread_id : str
    title: str


class GetHistoryRequest(BaseModel):
    user_id: str

