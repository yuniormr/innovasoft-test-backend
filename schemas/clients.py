from pydantic import BaseModel
from typing import Optional


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


# ── Create / Update payloads ──────────────────────────────────────────────────

class ClientListRequest(BaseModel):
    identificacion: Optional[str] = None
    nombre: Optional[str] = None
    usuarioId: str


class ClientCreateRequest(BaseModel):
    nombre: str
    apellidos: str
    identificacion: str
    telefonoCelular: str
    otroTelefono: Optional[str] = None
    direccion: str
    fNacimiento: str          # "YYYY-MM-DD"
    fAfiliacion: str          # "YYYY-MM-DD"
    sexo: str                 # "M" | "F"
    resenaPersonal: str
    imagen: Optional[str] = None
    interesFK: str
    usuarioId: str


class ClientUpdateRequest(BaseModel):
    id: str
    nombre: str
    apellidos: str
    identificacion: str
    celular: str
    otroTelefono: Optional[str] = None
    direccion: str
    fNacimiento: str
    fAfiliacion: str
    sexo: str
    resennaPersonal: str
    imagen: Optional[str] = None
    interesFK: str
    usuarioId: str


# ── Interest ──────────────────────────────────────────────────────────────────

class Interest(BaseModel):
    id: str
    descripcion: str
