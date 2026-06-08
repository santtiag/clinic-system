from datetime import date
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class PatientRegister(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    dni: str = Field(..., pattern=r"^\d{7,8}$")
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    date_of_birth: date = Field(..., alias="dateOfBirth")


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
