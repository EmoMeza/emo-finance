from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: str | None = None
    email: str | None = None


class LoginRequest(BaseModel):
    identifier: str
    password: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "identifier": "user@example.com",
                "password": "securepassword123"
            }
        }
    }
