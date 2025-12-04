from pydantic import BaseModel

class UserBase(BaseModel):
    preferred_category: str
    preferred_style: str
