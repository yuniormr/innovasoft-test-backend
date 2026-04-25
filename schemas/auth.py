from pydantic import BaseModel, EmailStr, field_validator
import re


# ── Request schemas ───────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_rules(cls, v: str) -> str:
        if len(v) < 8 or len(v) > 20:
            raise ValueError("La contraseña debe tener entre 8 y 20 caracteres.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("La contraseña debe contener al menos una mayúscula.")
        if not re.search(r"[a-z]", v):
            raise ValueError("La contraseña debe contener al menos una minúscula.")
        if not re.search(r"\d", v):
            raise ValueError("La contraseña debe contener al menos un número.")
        return v


# ── Response schemas ──────────────────────────────────────────────────────────

class LoginResponse(BaseModel):
    token: str
    expiration: str
    userid: str
    username: str


class RegisterResponse(BaseModel):
    status: str
    message: str
