from pydantic import BaseModel, Field
from typing import List, Optional

class SettingsInput(BaseModel):
    user_id: int
    level_of_complexity: str
    main_topic: str
    target_audience: str
    tone_of_voice: str
    cta: str
    word_limit: int  
    use_emojis: bool
    num_emojis: int = 0
    use_hashtags: bool
    num_hashtags: int = 0
    language: str
    target_country: str
    occasion: Optional[str] = None
    main_goal: str
    required_words: List[str] = Field(default_factory=list)
    forbidden_words: List[str] = Field(default_factory=list)
