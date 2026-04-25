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


# ── Shared validators ─────────────────────────────────────────────────────────

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# Acepta dígitos, espacios, guiones, paréntesis y signo +. Mínimo 7 dígitos netos.
_PHONE_RE = re.compile(r"^[\d\s\-\(\)\+]{7,20}$")
# Letras (incluye tildes, ñ), espacios y guion. Sin dígitos ni símbolos.
_NOMBRE_RE = re.compile(r"^[A-Za-záéíóúÁÉÍÓÚüÜñÑ\s\-]+$")
# Alfanumérico y guion (cédula, DIMEX, pasaporte). Sin espacios.
_IDENTIFICACION_RE = re.compile(r"^[A-Za-z0-9\-]{5,20}$")


def _validate_date(v: str) -> str:
    if not _DATE_RE.match(v):
        raise ValueError("date_format")
    return v


def _validate_phone(v: str) -> str:
    digits = re.sub(r"\D", "", v)
    if len(digits) < 7:
        raise ValueError("phone_min_digits")
    if not _PHONE_RE.match(v):
        raise ValueError("phone_invalid_chars")
    return v


def _validate_name(v: str) -> str:
    v = v.strip()
    if len(v) < 2:
        raise ValueError("name_min_length")
    if not _NOMBRE_RE.match(v):
        raise ValueError("name_only_letters")
    return v


def _validate_identificacion(v: str) -> str:
    v = v.strip()
    if not _IDENTIFICACION_RE.match(v):
        raise ValueError("id_format")
    return v


# ── Create / Update payloads ──────────────────────────────────────────────────

class ClientListRequest(BaseModel):
    identificacion: Optional[str] = None
    nombre: Optional[str] = None
    usuarioId: str


class ClientCreateRequest(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50)
    apellidos: str = Field(..., min_length=2, max_length=100)
    identificacion: str = Field(..., min_length=5, max_length=20)
    telefonoCelular: str = Field(..., max_length=20)
    otroTelefono: Optional[str] = Field(default=None, max_length=20)
    direccion: str = Field(..., min_length=5, max_length=200)
    fNacimiento: str
    fAfiliacion: str
    sexo: Literal["M", "F"]
    resenaPersonal: str = Field(..., min_length=3, max_length=200)
    imagen: Optional[str] = None
    interesFK: str = Field(..., min_length=1)
    usuarioId: str

    @field_validator("nombre", "apellidos")
    @classmethod
    def validate_nombre_apellidos_create(cls, v: str, info) -> str:
        return _validate_name(v)

    @field_validator("identificacion")
    @classmethod
    def validate_identificacion_create(cls, v: str) -> str:
        return _validate_identificacion(v)

    @field_validator("telefonoCelular")
    @classmethod
    def validate_celular(cls, v: str) -> str:
        return _validate_phone(v)

    @field_validator("otroTelefono")
    @classmethod
    def validate_otro_telefono(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            return _validate_phone(v)
        return v

    @field_validator("direccion", "resenaPersonal", "interesFK")
    @classmethod
    def strip_and_check_blank(cls, v: str, info) -> str:
        v = v.strip()
        if not v:
            raise ValueError("field_blank")
        return v

    @field_validator("fNacimiento")
    @classmethod
    def validate_nacimiento(cls, v: str) -> str:
        return _validate_date(v)

    @field_validator("fAfiliacion")
    @classmethod
    def validate_afiliacion(cls, v: str) -> str:
        return _validate_date(v)


class ClientUpdateRequest(BaseModel):
    id: str
    nombre: str = Field(..., min_length=2, max_length=50)
    apellidos: str = Field(..., min_length=2, max_length=100)
    identificacion: str = Field(..., min_length=5, max_length=20)
    celular: str = Field(..., max_length=20)
    otroTelefono: Optional[str] = Field(default=None, max_length=20)
    direccion: str = Field(..., min_length=5, max_length=200)
    fNacimiento: str
    fAfiliacion: str
    sexo: Literal["M", "F"]
    resennaPersonal: str = Field(..., min_length=3, max_length=200)
    imagen: Optional[str] = None
    interesFK: str = Field(..., min_length=1)
    usuarioId: str

    @field_validator("nombre", "apellidos")
    @classmethod
    def validate_nombre_apellidos_update(cls, v: str, info) -> str:
        return _validate_name(v)

    @field_validator("identificacion")
    @classmethod
    def validate_identificacion_update(cls, v: str) -> str:
        return _validate_identificacion(v)

    @field_validator("celular")
    @classmethod
    def validate_celular(cls, v: str) -> str:
        return _validate_phone(v)

    @field_validator("otroTelefono")
    @classmethod
    def validate_otro_telefono(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            return _validate_phone(v)
        return v

    @field_validator("direccion", "resennaPersonal", "interesFK")
    @classmethod
    def strip_and_check_blank(cls, v: str, info) -> str:
        v = v.strip()
        if not v:
            raise ValueError("field_blank")
        return v

    @field_validator("fNacimiento")
    @classmethod
    def validate_nacimiento(cls, v: str) -> str:
        return _validate_date(v)

    @field_validator("fAfiliacion")
    @classmethod
    def validate_afiliacion(cls, v: str) -> str:
        return _validate_date(v)


# ── Interest ──────────────────────────────────────────────────────────────────

class Interest(BaseModel):
    id: str
    descripcion: str
