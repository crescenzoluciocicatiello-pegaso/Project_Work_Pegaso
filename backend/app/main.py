# avvio: uvicorn app.main:app --reload

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.db import engine
from app.routers import (
    medici,
    prenotazioni,
    prestazioni,
    ricetta_prestazione,
    ricette,
    slot,
    utenti_pazienti,
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API - Sistema Prenotazioni",
    description="API per la gestione delle prenotazioni",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(utenti_pazienti.router)
app.include_router(medici.router)
app.include_router(prenotazioni.router)
app.include_router(slot.router)
app.include_router(ricette.router)
app.include_router(prestazioni.router)
app.include_router(ricetta_prestazione.router)


@app.get("/")
def root():
    return {
        "message": "API - Sistema Prenotazioni",
        "docs": "/docs",
        "redoc": "/redoc",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
