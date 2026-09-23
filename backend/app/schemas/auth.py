
from pydantic import BaseModel


class AdminLoginRequest(BaseModel):
    user_id: str
    password: str
