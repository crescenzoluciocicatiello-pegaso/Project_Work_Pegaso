from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    username: str
    password: str


# pazienti

class UtentePazienteBase(BaseModel):
    username: str = Field(..., max_length=50)
    email: EmailStr
    nome: str = Field(..., max_length=50)
    cognome: str = Field(..., max_length=50)
    sesso: Optional[str] = Field(None, max_length=1)
    telefono: Optional[str] = Field(None, max_length=20)
    data_nascita: date
    comune_nascita: Optional[str] = Field(None, max_length=50)
    codice_fiscale: str = Field(..., max_length=16)


class UtentePazienteCreate(UtentePazienteBase):
    password: str = Field(..., min_length=8)


# senza password
class UtentePazienteResponse(UtentePazienteBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# medici

class MedicoBase(BaseModel):
    nome: str = Field(..., max_length=50)
    cognome: str = Field(..., max_length=50)
    specializzazione: Optional[str] = Field(None, max_length=100)
    codice_fiscale: str = Field(..., max_length=16)


class MedicoCreate(MedicoBase):
    pass


class MedicoResponse(MedicoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# prestazioni

class PrestazioneBase(BaseModel):
    codice_prestazione: str = Field(..., max_length=20)
    descrizione: str = Field(..., max_length=255)


class PrestazioneCreate(PrestazioneBase):
    pass


class PrestazioneResponse(PrestazioneBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# slot

class SlotBase(BaseModel):
    id_prestazione: int
    data_inizio_slot: datetime
    data_fine_slot: datetime
    stato_slot: str = Field(default="0", max_length=1)  # 0 libero, 1 occupato


class SlotCreate(SlotBase):
    pass


class SlotResponse(SlotBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ricette

class RicettaBase(BaseModel):
    nre: str = Field(..., max_length=15)
    data_emissione: date
    data_scadenza: Optional[date] = None
    id_paziente: int
    id_medico: int


class RicettaCreate(RicettaBase):
    nre: str = Field(..., pattern=r"^[A-Z0-9]{15}$")


class RicettaResponse(RicettaBase):
    id: int
    nome_medico: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class RicettaResponsePaziente(BaseModel):
    id: int
    nre: str = Field(..., max_length=15)
    data_emissione: date
    data_scadenza: Optional[date] = None
    nome_medico: Optional[str] = None


# ricetta - prestazione

class RicettaPrestazioneBase(BaseModel):
    id: int
    id_ricetta: int
    id_prestazione: int
    prenotata: bool = False


class RicettaPrestazioneCreate(BaseModel):
    id_ricetta: int
    id_prestazione: int


class RicettaPrestazioneResponse(RicettaPrestazioneBase):
    codice_prestazione: Optional[str] = None
    descrizione: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# prenotazioni

class PrenotazioneBase(BaseModel):
    note_paziente: Optional[str] = Field(None, max_length=255)
    stato_pren: str = Field(..., max_length=20)
    id_paziente: int
    id_ricetta_prestazione: int
    id_slot: int


class PrenotazioneCreate(PrenotazioneBase):
    pass


class PrenotazioneResponse(PrenotazioneBase):
    id: int
    data_prenotazione: datetime
    codice_fiscale: str = Field(..., max_length=16)
    nome: str = Field(..., max_length=50)
    cognome: str = Field(..., max_length=50)
    data_nascita: date
    comune_nascita: Optional[str] = Field(None, max_length=50)
    codice_prestazione: str = Field(..., max_length=20)
    descrizione: str = Field(..., max_length=255)
    data_inizio_slot: datetime
    data_fine_slot: datetime
    model_config = ConfigDict(from_attributes=True)
