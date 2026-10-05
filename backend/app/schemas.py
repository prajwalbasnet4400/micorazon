from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

Binary = Literal[0, 1]


class SignupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(pattern=r"^\+?[0-9]{7,15}$")
    address: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("name", "address")
    @classmethod
    def strip(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("must be at least 2 characters")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    phone: str
    new_password: str = Field(min_length=8, max_length=128)


class User(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    address: str


class AuthResponse(BaseModel):
    token: str
    user: User


class HealthData(BaseModel):
    """Clinical inputs. Field names match the UCI heart failure clinical records dataset."""

    age: int = Field(ge=1, le=120, description="Age of the patient (years)")
    sex: Binary = Field(description="1 = male, 0 = female")
    anaemia: Binary = Field(description="Decrease of red blood cells or hemoglobin")
    creatinine_phosphokinase: int = Field(ge=1, le=10_000, description="CPK enzyme level in blood (mcg/L)")
    diabetes: Binary
    ejection_fraction: int = Field(ge=5, le=90, description="% of blood leaving the heart per contraction")
    high_blood_pressure: Binary
    platelets: float = Field(ge=10_000, le=1_000_000, description="Platelets in blood (kiloplatelets/mL)")
    serum_creatinine: float = Field(ge=0.1, le=15, description="Serum creatinine level (mg/dL)")
    serum_sodium: int = Field(ge=100, le=160, description="Serum sodium level (mEq/L)")
    smoking: Binary
    time: int = Field(ge=0, le=365, description="Follow-up period (days)")


class Factor(BaseModel):
    feature: str
    label: str
    value: float
    contribution: float
    direction: Literal["increases", "decreases"]


class PredictionResult(BaseModel):
    id: int
    status: Literal["Healthy", "At Risk"]
    risk_level: Literal["Low", "Moderate", "High", "Very High"]
    probability_healthy: float
    probability_at_risk: float
    top_factors: list[Factor]
    suggestions: list[str]
    inputs: HealthData
    created_at: str
