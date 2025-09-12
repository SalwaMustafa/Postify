from pydantic import BaseModel, Field
from typing import List

class PostOutput(BaseModel):
    title: str = Field(..., description="The catchy title of the social media post")
    description: str = Field(..., description="The main engaging content of the post")
    
