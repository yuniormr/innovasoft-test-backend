from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
import re


# ── Client list item (returned by Listado) ────────────────────────────────────

class ClientListItem(BaseModel):
    id: str
    identificacion: str
    nombre: str
    apellidos: str


# ── Full client detail ────────────────────────────────────────────────────────

class ClientDetail(BaseModel):
    id: str
    nombre: str
    apellidos: str
    identificacion: str
    telefonoCelular: Optional[str] = None
    otroTelefono: Optional[str] = None
    direccion: Optional[str] = None
    fNacimiento: Optional[str] = None
    fAfiliacion: Optional[str] = None
    sexo: Optional[str] = None
    resenaPersonal: Optional[str] = None
    imagen: Optional[str] = None
    interesesId: Optional[str] = None


# ── Shared validator ──────────────────────────────────────────────────────────

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _validate_date(v: str, field_name: str) -> str:
    if not _DATE_RE.match(v):
        raise ValueError(f"{field_name} debe tener el formato YYYY-MM-DD.")
    return v


# ── Create / Update payloads ──────────────────────────────────────────────────

class ClientListRequest(BaseModel):
    identificacion: Optional[str] = None
    nombre: Optional[str] = None
    usuarioId: str


class ClientCreateRequest(BaseModel):
    nombre: str = Field(..., max_length=50)
    apellidos: str = Field(..., max_length=100)
    identificacion: str = Field(..., max_length=20)
    telefonoCelular: str = Field(..., max_length=20)
    otroTelefono: Optional[str] = Field(default=None, max_length=20)
    direccion: str = Field(..., max_length=200)
    fNacimiento: str
    fAfiliacion: str
    sexo: Literal["M", "F"]
    resenaPersonal: str = Field(..., max_length=200)
    imagen: Optional[str] = None
    interesFK: str
    usuarioId: str

    @field_validator("fNacimiento")
    @classmethod
    def validate_nacimiento(cls, v: str) -> str:
        return _validate_date(v, "fNacimiento")

    @field_validator("fAfiliacion")
    @classmethod
    def validate_afiliacion(cls, v: str) -> str:
        return _validate_date(v, "fAfiliacion")


class ClientUpdateRequest(BaseModel):
    id: str
    nombre: str = Field(..., max_length=50)
    apellidos: str = Field(..., max_length=100)
    identificacion: str = Field(..., max_length=20)
    celular: str = Field(..., max_length=20)
    otroTelefono: Optional[str] = Field(default=None, max_length=20)
    direccion: str = Field(..., max_length=200)
    fNacimiento: str
    fAfiliacion: str
    sexo: Literal["M", "F"]
    resennaPersonal: str = Field(..., max_length=200)
    imagen: Optional[str] = None
    interesFK: str
    usuarioId: str

    @field_validator("fNacimiento")
    @classmethod
    def validate_nacimiento(cls, v: str) -> str:
        return _validate_date(v, "fNacimiento")

    @field_validator("fAfiliacion")
    @classmethod
    def validate_afiliacion(cls, v: str) -> str:
        return _validate_date(v, "fAfiliacion")


# ── Interest ──────────────────────────────────────────────────────────────────

class Interest(BaseModel):
    id: str
    descripcion: str
