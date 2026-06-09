from datetime import date
from typing import Optional, Literal
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


class DoctorRegister(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    dni: str = Field(..., pattern=r"^\d{7,8}$")
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    date_of_birth: date = Field(..., alias="dateOfBirth")
    specialty: str = Field(..., min_length=3)
    license_number: str = Field(..., alias="licenseNumber", min_length=3)


class StaffCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    dni: str = Field(..., pattern=r"^\d{7,8}$")
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    date_of_birth: date = Field(..., alias="dateOfBirth")
    role: Literal["admin", "staff", "doctor"] = "staff"
    specialty: Optional[str] = None
    license_number: Optional[str] = Field(None, alias="licenseNumber")


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = Field(None, alias="isActive")
    specialty: Optional[str] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    username: str
    email: str
    role: str
    dni: str
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    specialty: Optional[str] = None
    license_number: Optional[str] = Field(None, alias="licenseNumber")
    is_active: bool = Field(..., alias="isActive")
